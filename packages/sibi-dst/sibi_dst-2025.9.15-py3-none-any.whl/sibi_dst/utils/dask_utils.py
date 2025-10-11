from __future__ import annotations

import asyncio
import logging
from typing import List, Any, Dict

import dask
import dask.dataframe as dd

def _to_int_safe(x) -> int:
    """
    Convert scalar-like to int safely.
    Handles numpy scalars, pandas Series/DataFrame outputs.
    """
    if hasattr(x, "item"):        # numpy scalar, pandas scalar
        return int(x.item())
    if hasattr(x, "iloc"):        # Series-like
        return int(x.iloc[0])
    return int(x)

def dask_is_probably_empty(ddf: dd.DataFrame) -> bool:
    return getattr(ddf, "npartitions", 0) == 0 or len(ddf._meta.columns) == 0


def dask_is_empty_truthful(ddf: dd.DataFrame) -> bool:
    n = ddf.map_partitions(len).sum().compute()
    return int(n) == 0


def dask_is_empty(ddf: dd.DataFrame, *, sample: int = 4) -> bool:
    if dask_is_probably_empty(ddf):
        return True

    k = min(max(sample, 1), ddf.npartitions)
    probes = dask.compute(*[
        ddf.get_partition(i).map_partitions(len) for i in range(k)
    ], scheduler="threads")

    if any(_to_int_safe(n) > 0 for n in probes):
        return False
    if k == ddf.npartitions and all(_to_int_safe(n) == 0 for n in probes):
        return True

    return dask_is_empty_truthful(ddf)

class UniqueValuesExtractor:
    @staticmethod
    def _compute_to_list_sync(series) -> List[Any]:
        """Run in a worker thread when Dask-backed."""
        if hasattr(series, "compute"):
            return series.compute().tolist()
        return series.tolist()

    async def compute_to_list(self, series) -> List[Any]:
        # Offload potential Dask .compute() to a thread to avoid blocking the event loop
        return await asyncio.to_thread(self._compute_to_list_sync, series)

    async def extract_unique_values(self, df, *columns: str) -> Dict[str, List[Any]]:
        async def one(col: str):
            ser = df[col].dropna().unique()
            return col, await self.compute_to_list(ser)

        pairs = await asyncio.gather(*(one(c) for c in columns))
        return dict(pairs)

import asyncio
import json
import logging
import os
import tempfile
from contextlib import suppress, asynccontextmanager, contextmanager
from typing import Optional
from dask.distributed import Client, LocalCluster, get_client
from filelock import FileLock


class DaskClientMixin:
    """
    Provides shared Dask client lifecycle management with:
    - Shared registry (JSON + file lock)
    - Automatic refcounting across processes
    - Auto-cleanup of stale clusters
    - Optional background watchdog to monitor cluster health
    """

    REGISTRY_PATH = os.path.join(tempfile.gettempdir(), "shared_dask_cluster.json")
    REGISTRY_LOCK = FileLock(REGISTRY_PATH + ".lock")
    WATCHDOG_INTERVAL = 60  # seconds between health checks

    def __init__(self, **kwargs):
        self.dask_client: Optional[Client] = None
        self.own_dask_client: bool = False
        self.logger = kwargs.get("logger") or logging.getLogger(__name__)
        self._watchdog_task: Optional[asyncio.Task] = None
        self._watchdog_stop = asyncio.Event()

    # ----------------------------------------------------------------------
    # Registry management
    # ----------------------------------------------------------------------
    @classmethod
    def _read_registry(cls) -> Optional[dict]:
        """Read registry JSON if it exists and is valid."""
        if not os.path.exists(cls.REGISTRY_PATH):
            return None
        try:
            with open(cls.REGISTRY_PATH, "r") as f:
                data = json.load(f)
            if "address" not in data or not isinstance(data["address"], str):
                return None
            return data
        except (json.JSONDecodeError, OSError):
            return None

    @classmethod
    def _write_registry(cls, data: dict) -> None:
        """Write updated registry JSON atomically."""
        tmp_path = cls.REGISTRY_PATH + ".tmp"
        with open(tmp_path, "w") as f:
            json.dump(data, f)
        os.replace(tmp_path, cls.REGISTRY_PATH)

    @classmethod
    def _remove_registry(cls) -> None:
        """Delete the registry file if present."""
        with suppress(FileNotFoundError):
            os.remove(cls.REGISTRY_PATH)

    @classmethod
    def _cleanup_stale_registry(cls, logger=None):
        """Detect and remove stale registry entries if cluster is unreachable."""
        registry = cls._read_registry()
        if not registry:
            return
        try:
            client = Client(address=registry["address"], timeout=5)
            client.close()
        except Exception:
            if logger:
                logger.warning(
                    f"Detected stale Dask cluster registry at {registry.get('address')}. Cleaning up."
                )
            cls._remove_registry()

    # ----------------------------------------------------------------------
    # Dask client initialization
    # ----------------------------------------------------------------------
    def _init_dask_client(
        self,
        dask_client: Optional[Client] = None,
        *,
        logger=None,
        scheduler_address: Optional[str] = None,
        use_remote_cluster: bool = False,
        n_workers: int = 2,
        threads_per_worker: int = 1,
        processes: bool = False,
        asynchronous: bool = False,
        memory_limit: str = "auto",
        local_directory: Optional[str] = None,
        silence_logs: str = "info",
        resources: Optional[dict] = None,
        timeout: int = 30,
        watchdog: bool = True,
    ):
        """Initialize or attach to a shared Dask client."""
        self.logger = logger or self.logger
        self.dask_client = dask_client
        self.own_dask_client = False

        # Silence excessive logging
        logging.getLogger("distributed.scheduler").setLevel(logging.WARNING)
        logging.getLogger("distributed.worker").setLevel(logging.WARNING)
        logging.getLogger("distributed.shuffle._scheduler_plugin").setLevel(logging.ERROR)

        # 1️⃣ Try reusing existing client
        if self.dask_client is None:
            with suppress(ValueError, RuntimeError):
                self.dask_client = get_client()

        # 2️⃣ Try remote cluster connection
        if self.dask_client is None and use_remote_cluster and scheduler_address:
            try:
                self.dask_client = Client(address=scheduler_address, timeout=timeout)
                self.own_dask_client = True
                self.logger.info(
                    f"Connected to external Dask scheduler at {scheduler_address}. "
                    f"Dashboard: {self.dask_client.dashboard_link}"
                )
                if watchdog:
                    self._start_watchdog()
                return
            except Exception as e:
                self.logger.warning(
                    f"Failed to connect to remote Dask scheduler: {e}. Falling back to local cluster."
                )

        # 3️⃣ Shared local cluster via registry
        with self.REGISTRY_LOCK:
            self._cleanup_stale_registry(self.logger)
            registry = self._read_registry()

            if registry:
                try:
                    self.dask_client = Client(address=registry["address"], timeout=timeout)
                    registry["refcount"] = registry.get("refcount", 0) + 1
                    self._write_registry(registry)
                    self.logger.info(
                        f"Reusing existing LocalCluster at {registry['address']} (refcount={registry['refcount']})."
                    )
                    if watchdog:
                        self._start_watchdog()
                    return
                except Exception:
                    self.logger.warning("Existing cluster unreachable. Recreating.")
                    self._remove_registry()

            # Create a new local cluster
            cluster = LocalCluster(
                n_workers=n_workers,
                threads_per_worker=threads_per_worker,
                processes=processes,
                asynchronous=asynchronous,
                memory_limit=memory_limit,
                local_directory=local_directory,
                silence_logs=silence_logs,
                resources=resources,
                timeout=timeout,
            )

            self.dask_client = Client(cluster)
            self.own_dask_client = True
            registry = {"address": cluster.scheduler_address, "refcount": 1}
            self._write_registry(registry)
            self.logger.info(
                f"Started new LocalCluster ({n_workers} workers × {threads_per_worker} threads). "
                f"Dashboard: {self.dask_client.dashboard_link}"
            )

        if watchdog:
            self._start_watchdog()

    # ----------------------------------------------------------------------
    # Watchdog logic
    # ----------------------------------------------------------------------
    def _start_watchdog(self):
        """Spawn a background watchdog that monitors registry health."""
        async def watchdog_loop():
            while not self._watchdog_stop.is_set():
                await asyncio.sleep(self.WATCHDOG_INTERVAL)
                try:
                    self._cleanup_stale_registry(self.logger)
                except Exception as e:
                    self.logger.warning(f"Dask watchdog encountered an error: {e}")

        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                self._watchdog_task = loop.create_task(watchdog_loop())
                self.logger.debug("Started Dask registry watchdog (async).")
        except RuntimeError:
            # Fallback for synchronous usage
            self.logger.debug("Watchdog skipped (no active event loop).")

    async def _stop_watchdog(self):
        """Stop the watchdog loop gracefully."""
        self._watchdog_stop.set()
        if self._watchdog_task:
            await asyncio.wait([self._watchdog_task], timeout=5)
            self._watchdog_task = None

    # ----------------------------------------------------------------------
    # Client cleanup
    # ----------------------------------------------------------------------
    def _close_dask_client(self):
        """Safely close client and update registry reference count."""
        if not self.dask_client:
            return

        with self.REGISTRY_LOCK:
            registry = self._read_registry()

            if registry and "refcount" in registry:
                registry["refcount"] = max(0, registry["refcount"] - 1)
                if registry["refcount"] == 0:
                    self.logger.info("Reference count 0 — closing LocalCluster.")
                    try:
                        cluster = getattr(self.dask_client, "cluster", None)
                        self.dask_client.close()
                        if cluster:
                            cluster.close()
                    except Exception as e:
                        self.logger.warning(f"Error closing Dask cluster: {e}")
                    self._remove_registry()
                else:
                    self._write_registry(registry)
                    self.logger.debug(
                        f"Decremented LocalCluster refcount to {registry['refcount']}."
                    )
            else:
                with suppress(Exception):
                    self.dask_client.close()
                self.logger.debug("Closed Dask client without registry tracking.")

        # Stop watchdog if active
        if self._watchdog_task:
            asyncio.create_task(self._stop_watchdog())


# ----------------------------------------------------------------------
# Shared Dask session (sync + async)
# ----------------------------------------------------------------------
def shared_dask_session(*, async_mode: bool = True, **kwargs):
    """
    Context manager for a shared Dask session (supports async + sync).

    Example:
        async with shared_dask_session(logger=logger) as client:
            ...

        with shared_dask_session(async_mode=False) as client:
            ...
    """
    mixin = DaskClientMixin()
    mixin._init_dask_client(**kwargs)

    if async_mode:
        @asynccontextmanager
        async def _async_manager():
            try:
                yield mixin.dask_client
            finally:
                mixin._close_dask_client()
        return _async_manager()
    else:
        @contextmanager
        def _sync_manager():
            try:
                yield mixin.dask_client
            finally:
                mixin._close_dask_client()
        return _sync_manager()

# from contextlib import suppress, asynccontextmanager
# from dask.distributed import Client, LocalCluster, get_client
# import os
#
# class DaskClientMixin:
#     """
#     Provides shared Dask client lifecycle management.
#     Ensures reuse of an existing client if available,
#     or creates a local in-process Dask cluster for fallback.
#     """
#
#     def _init_dask_client(
#         self,
#         dask_client=None,
#         logger=None,
#         *,
#         n_workers: int = 1,
#         threads_per_worker: int = 1,
#         processes: bool = False,
#         asynchronous: bool = False,
#         memory_limit: str = "auto",
#         #dashboard_address: str | None = None,
#         local_directory: str | None = None,
#         silence_logs: str = "info",
#         resources: dict | None = None,
#         timeout: int = 30,
#     ):
#         self.dask_client = dask_client
#         self.own_dask_client = False
#         self.logger = logger
#         # Apply log filters globally
#         logging.getLogger("distributed.shuffle._scheduler_plugin").setLevel(
#             logging.ERROR
#         )
#         logging.getLogger("distributed.scheduler").setLevel(logging.WARNING)
#         logging.getLogger("distributed.worker").setLevel(logging.WARNING)
#
#         if self.dask_client is None:
#             with suppress(ValueError, RuntimeError):
#                 # Try to attach to an existing client (common in shared Dask setups)
#                 self.dask_client = get_client()
#
#         if self.dask_client is None:
#             # Default to half of logical cores if not specified
#             n_workers = n_workers or max(2, os.cpu_count() // 2)
#
#             cluster = LocalCluster(
#                 n_workers=n_workers,
#                 threads_per_worker=threads_per_worker,
#                 processes=processes,
#                 asynchronous=asynchronous,
#                 memory_limit=memory_limit,
#                 local_directory=local_directory,
#                 silence_logs=silence_logs,
#                 resources=resources,
#                 timeout=timeout,
#             )
#
#             self.dask_client = Client(cluster)
#             self.own_dask_client = True
#
#             if self.logger:
#                 self.logger.info(
#                     f"Started local Dask cluster with {n_workers} workers × {threads_per_worker} threads "
#                     f"({memory_limit} memory per worker). Dashboard: {self.dask_client.dashboard_link}"
#                 )
#         else:
#             if self.logger:
#                 self.logger.debug(
#                     f"Using existing Dask client: {self.dask_client.dashboard_link}"
#                 )
#
#     def _close_dask_client(self):
#         """Close the Dask client if this instance created it."""
#         if getattr(self, "own_dask_client", False) and self.dask_client is not None:
#             try:
#                 cluster = getattr(self.dask_client, "cluster", None)
#                 self.dask_client.close()
#                 if cluster is not None:
#                     cluster.close()
#                 if self.logger:
#                     self.logger.info("Closed local Dask client and cluster.")
#             except Exception as e:
#                 if self.logger:
#                     self.logger.warning(f"Error while closing Dask client: {e}")
#
# @asynccontextmanager
# async def shared_dask_session(**kwargs):
#     mixin = DaskClientMixin()
#     mixin._init_dask_client(**kwargs)
#     try:
#         yield mixin.dask_client
#     finally:
#         mixin._close_dask_client()
