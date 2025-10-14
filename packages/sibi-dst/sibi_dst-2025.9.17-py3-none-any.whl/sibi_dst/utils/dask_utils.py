from __future__ import annotations
import asyncio
from typing import List, Any, Dict, Optional
import dask
import dask.dataframe as dd
import numpy as np
import pandas as pd
from distributed import Client


def _to_int_safe(x) -> int:
    """Convert scalar-like to int safely."""
    if x is None:
        return 0
    if hasattr(x, "item"):
        try:
            return int(x.item())
        except Exception:
            return 0
    if hasattr(x, "iloc"):
        try:
            return int(x.iloc[0])
        except Exception:
            return 0
    try:
        return int(x)
    except Exception:
        return 0


# ----------------------------------------------------------------------
# Dask emptiness helpers
# ----------------------------------------------------------------------

def dask_is_probably_empty(ddf: dd.DataFrame) -> bool:
    """Quick structural check before computing."""
    return getattr(ddf, "npartitions", 0) == 0 or len(ddf._meta.columns) == 0


def dask_is_empty_truthful(ddf: dd.DataFrame, dask_client: Optional[Client] = None) -> bool:
    """Full compute of row count across all partitions."""
    if dask_client:
        total = dask_client.sync(lambda: ddf.map_partitions(len).sum().compute())
    else:
        total = ddf.map_partitions(len).sum().compute()
    return int(total) == 0


def dask_is_empty(ddf: dd.DataFrame, *, sample: int = 4, dask_client: Optional[Client] = None) -> bool:
    """
    Heuristic emptiness check.
    Uses only a few partitions; falls back to full compute if needed.
    """
    if dask_is_probably_empty(ddf):
        return True

    k = min(max(sample, 1), ddf.npartitions)
    tasks = [ddf.get_partition(i).map_partitions(len) for i in range(k)]

    if dask_client:
        probes = dask_client.gather(dask_client.compute(tasks))
    else:
        probes = dask.compute(*tasks, scheduler="threads")

    if any(_to_int_safe(n) > 0 for n in probes):
        return False
    if k == ddf.npartitions and all(_to_int_safe(n) == 0 for n in probes):
        return True

    return dask_is_empty_truthful(ddf, dask_client=dask_client)


# ----------------------------------------------------------------------
# Unique value extractor (client-safe)
# ----------------------------------------------------------------------

class UniqueValuesExtractor:
    """
    Extract unique non-null values from Dask or pandas columns,
    using async thread offload and optional Dask client integration.
    """

    def __init__(self, dask_client: Optional[Client] = None):
        self.dask_client = dask_client

    # ---------- internal ----------
    def _compute_to_list_sync(self, series) -> List[Any]:
        """Compute unique list synchronously with or without client."""
        if hasattr(series, "compute"):
            if self.dask_client:
                result = self.dask_client.sync(lambda: series.compute())
            else:
                result = series.compute()
        else:
            result = series

        if isinstance(result, (np.ndarray, pd.Series, list)):
            return pd.Series(result).dropna().unique().tolist()
        return [result]

    async def compute_to_list(self, series) -> List[Any]:
        """Offload compute to thread to avoid blocking."""
        return await asyncio.to_thread(self._compute_to_list_sync, series)

    # ---------- public ----------
    async def extract_unique_values(self, df, *columns: str) -> Dict[str, List[Any]]:
        """
        Concurrently extract unique values for requested columns.
        Compatible with Dask and Pandas.
        """
        async def one(col: str):
            ser = df[col].dropna().unique()
            return col, await self.compute_to_list(ser)

        results = await asyncio.gather(*(one(c) for c in columns))
        return dict(results)

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
    Resilient Dask client lifecycle with:
    - Shared JSON registry + file lock
    - Reference counting across processes
    - Watchdog health checks with auto-reattach
    - Optional external scheduler
    - No premature shutdown while tasks run
    """

    REGISTRY_PATH = os.path.join(tempfile.gettempdir(), "shared_dask_cluster.json")
    REGISTRY_LOCK = FileLock(REGISTRY_PATH + ".lock")
    WATCHDOG_INTERVAL = 60

    def __init__(self, **kwargs):
        self.dask_client: Optional[Client] = None
        self.own_dask_client: bool = False
        self.logger = kwargs.get("logger") or logging.getLogger(__name__)
        self._watchdog_task: Optional[asyncio.Task] = None
        self._watchdog_stop = asyncio.Event()

    # ---------- registry ----------

    @classmethod
    def _read_registry(cls) -> Optional[dict]:
        if not os.path.exists(cls.REGISTRY_PATH):
            return None
        try:
            with open(cls.REGISTRY_PATH, "r") as f:
                data = json.load(f)
            if not isinstance(data, dict) or "address" not in data:
                return None
            return data
        except (json.JSONDecodeError, OSError):
            return None

    @classmethod
    def _write_registry(cls, data: dict) -> None:
        tmp = cls.REGISTRY_PATH + ".tmp"
        with open(tmp, "w") as f:
            json.dump(data, f)
        os.replace(tmp, cls.REGISTRY_PATH)

    @classmethod
    def _remove_registry(cls) -> None:
        with suppress(FileNotFoundError):
            os.remove(cls.REGISTRY_PATH)

    @classmethod
    def _cleanup_stale_registry(cls, logger=None) -> None:
        reg = cls._read_registry()
        if not reg:
            return
        try:
            c = Client(address=reg["address"], timeout=5)
            c.close()
        except Exception:
            if logger:
                logger.warning(f"Stale Dask registry at {reg.get('address')}. Removing.")
            cls._remove_registry()

    # ---------- init ----------

    def _init_dask_client(
        self,
        dask_client: Optional[Client] = None,
        *,
        logger=None,
        scheduler_address: Optional[str] = None,
        use_remote_cluster: bool = False,
        n_workers: int = 4,
        threads_per_worker: int = 2,
        processes: bool = False,
        asynchronous: bool = False,
        memory_limit: str = "auto",
        local_directory: Optional[str] = None,
        silence_logs: str = "warning",
        resources: Optional[dict] = None,
        timeout: int = 30,
        watchdog: bool = True,
    ) -> None:
        self.logger = logger or self.logger
        self.dask_client = dask_client
        self.own_dask_client = False

        logging.getLogger("distributed.scheduler").setLevel(logging.WARNING)
        logging.getLogger("distributed.worker").setLevel(logging.WARNING)
        logging.getLogger("distributed.comm").setLevel(logging.ERROR)
        logging.getLogger("distributed.batched").setLevel(logging.ERROR)
        logging.getLogger("distributed.shuffle._scheduler_plugin").setLevel(logging.ERROR)

        # 1) reuse existing client in-context
        if self.dask_client is None:
            with suppress(ValueError, RuntimeError):
                self.dask_client = get_client()

        # 2) external scheduler
        if self.dask_client is None and use_remote_cluster and scheduler_address:
            try:
                self.dask_client = Client(address=scheduler_address, timeout=timeout)
                self.own_dask_client = True
                self.logger.info(
                    f"Connected to external scheduler {scheduler_address}. "
                    f"Dashboard: {self.dask_client.dashboard_link}"
                )
                if watchdog:
                    self._start_watchdog()
                return
            except Exception as e:
                self.logger.warning(f"Remote connect failed: {e}. Falling back to local.")

        # 3) shared local cluster (registry)
        with self.REGISTRY_LOCK:
            self._cleanup_stale_registry(self.logger)
            reg = self._read_registry()

            if reg:
                try:
                    self.dask_client = Client(address=reg["address"], timeout=timeout)
                    reg["refcount"] = int(reg.get("refcount", 0)) + 1
                    self._write_registry(reg)
                    self.logger.info(
                        f"Reusing LocalCluster at {reg['address']} (refcount={reg['refcount']})."
                    )
                    if watchdog:
                        self._start_watchdog()
                    return
                except Exception:
                    self.logger.warning("Registry address unreachable. Recreating.")
                    self._remove_registry()

            # create new local cluster
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

            reg = {"address": cluster.scheduler_address, "refcount": 1}
            self._write_registry(reg)
            self.logger.info(
                f"Started LocalCluster {reg['address']} "
                f"({n_workers} workers x {threads_per_worker} threads). "
                f"Dashboard: {self.dask_client.dashboard_link}"
            )

        if watchdog:
            self._start_watchdog()

    # ---------- watchdog ----------

    def _start_watchdog(self) -> None:
        async def watchdog_loop():
            while not self._watchdog_stop.is_set():
                await asyncio.sleep(self.WATCHDOG_INTERVAL)
                try:
                    # verify live client
                    if not self.dask_client:
                        raise RuntimeError("No client bound.")
                    self.dask_client.scheduler_info()
                except Exception:
                    # attempt reattach using registry or recreate
                    self.logger.warning("Dask watchdog: client unhealthy. Reattaching.")
                    try:
                        with self.REGISTRY_LOCK:
                            self._cleanup_stale_registry(self.logger)
                            reg = self._read_registry()
                            if reg:
                                self.dask_client = Client(address=reg["address"], timeout=10)
                                self.logger.info("Reattached to existing LocalCluster.")
                            else:
                                # recreate minimal in-proc cluster
                                cluster = LocalCluster(
                                    n_workers=2, threads_per_worker=1, processes=False, silence_logs="warning"
                                )
                                self.dask_client = Client(cluster)
                                self.own_dask_client = True
                                self._write_registry({"address": cluster.scheduler_address, "refcount": 1})
                                self.logger.info("Recreated LocalCluster.")
                    except Exception as e:
                        self.logger.error(f"Watchdog reattach failed: {e}")

        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                self._watchdog_task = loop.create_task(watchdog_loop())
                self.logger.debug("Started Dask watchdog.")
        except RuntimeError:
            self.logger.debug("Watchdog not started. No running loop.")

    async def _stop_watchdog(self) -> None:
        self._watchdog_stop.set()
        if self._watchdog_task:
            with suppress(Exception):
                await asyncio.wait([self._watchdog_task], timeout=5)
            self._watchdog_task = None

    # ---------- close ----------

    def _close_dask_client(self) -> None:
        if not self.dask_client:
            return

        # Do not close if other references remain in registry
        with self.REGISTRY_LOCK:
            reg = self._read_registry()
            if reg and "refcount" in reg:
                reg["refcount"] = max(0, int(reg["refcount"]) - 1)
                if reg["refcount"] == 0:
                    self.logger.info("Refcount reached 0. Closing LocalCluster.")
                    try:
                        cluster = getattr(self.dask_client, "cluster", None)
                        # Grace period for running futures
                        with suppress(Exception):
                            self.dask_client.wait_for_workers(0, timeout="1s")
                        self.dask_client.close()
                        if cluster:
                            cluster.close()
                    except Exception as e:
                        self.logger.warning(f"Error closing cluster: {e}")
                    self._remove_registry()
                else:
                    self._write_registry(reg)
                    self.logger.debug(f"Decremented refcount to {reg['refcount']}.")
            else:
                # No registry info. Close only if we truly own it.
                if self.own_dask_client:
                    with suppress(Exception):
                        cluster = getattr(self.dask_client, "cluster", None)
                        self.dask_client.close()
                        if cluster:
                            cluster.close()
                self.logger.debug("Closed client without registry tracking.")

        # stop watchdog
        if self._watchdog_task:
            asyncio.create_task(self._stop_watchdog())


# ---------- persistent singleton ----------

_persistent_mixin: Optional[DaskClientMixin] = None


def get_persistent_client(
    *,
    logger: Optional[logging.Logger] = None,
    use_remote_cluster: bool = False,
    scheduler_address: Optional[str] = None,
) -> Client:
    global _persistent_mixin
    if _persistent_mixin is None or _persistent_mixin.dask_client is None:
        _persistent_mixin = DaskClientMixin(logger=logger)
        _persistent_mixin._init_dask_client(
            use_remote_cluster=use_remote_cluster,
            scheduler_address=scheduler_address,
            n_workers=4,
            threads_per_worker=2,
            processes=False,
            watchdog=True,
        )
    return _persistent_mixin.dask_client  # type: ignore[return-value]


# ---------- shared session contexts ----------

def shared_dask_session(*, async_mode: bool = True, **kwargs):
    """
    Context manager for shared Dask client.
    Keeps cluster alive across contexts via registry refcounting.
    """

    mixin = DaskClientMixin()
    mixin._init_dask_client(**kwargs)

    if async_mode:
        @asynccontextmanager
        async def _async_manager():
            try:
                # Hold a strong reference inside the context
                client = mixin.dask_client
                yield client
            finally:
                # Only close if this instance truly owns and refcount reaches zero
                mixin._close_dask_client()
        return _async_manager()
    else:
        @contextmanager
        def _sync_manager():
            try:
                client = mixin.dask_client
                yield client
            finally:
                mixin._close_dask_client()
        return _sync_manager()


# from __future__ import annotations
#
# from typing import List, Any, Dict
#
# import dask
# import dask.dataframe as dd
#
# def _to_int_safe(x) -> int:
#     """
#     Convert scalar-like to int safely.
#     Handles numpy scalars, pandas Series/DataFrame outputs.
#     """
#     if hasattr(x, "item"):        # numpy scalar, pandas scalar
#         return int(x.item())
#     if hasattr(x, "iloc"):        # Series-like
#         return int(x.iloc[0])
#     return int(x)
#
# def dask_is_probably_empty(ddf: dd.DataFrame) -> bool:
#     return getattr(ddf, "npartitions", 0) == 0 or len(ddf._meta.columns) == 0
#
#
# def dask_is_empty_truthful(ddf: dd.DataFrame) -> bool:
#     n = ddf.map_partitions(len).sum().compute()
#     return int(n) == 0
#
#
# def dask_is_empty(ddf: dd.DataFrame, *, sample: int = 4) -> bool:
#     if dask_is_probably_empty(ddf):
#         return True
#
#     k = min(max(sample, 1), ddf.npartitions)
#     probes = dask.compute(*[
#         ddf.get_partition(i).map_partitions(len) for i in range(k)
#     ], scheduler="threads")
#
#     if any(_to_int_safe(n) > 0 for n in probes):
#         return False
#     if k == ddf.npartitions and all(_to_int_safe(n) == 0 for n in probes):
#         return True
#
#     return dask_is_empty_truthful(ddf)
#
# class UniqueValuesExtractor:
#     @staticmethod
#     def _compute_to_list_sync(series) -> List[Any]:
#         """Run in a worker thread when Dask-backed."""
#         if hasattr(series, "compute"):
#             return series.compute().tolist()
#         return series.tolist()
#
#     async def compute_to_list(self, series) -> List[Any]:
#         # Offload potential Dask .compute() to a thread to avoid blocking the event loop
#         return await asyncio.to_thread(self._compute_to_list_sync, series)
#
#     async def extract_unique_values(self, df, *columns: str) -> Dict[str, List[Any]]:
#         async def one(col: str):
#             ser = df[col].dropna().unique()
#             return col, await self.compute_to_list(ser)
#
#         pairs = await asyncio.gather(*(one(c) for c in columns))
#         return dict(pairs)
#
# import asyncio
# import json
# import logging
# import os
# import tempfile
# from contextlib import suppress, asynccontextmanager, contextmanager
# from typing import Optional
# from dask.distributed import Client, LocalCluster, get_client
# from filelock import FileLock
#
#
# class DaskClientMixin:
#     """
#     Provides shared Dask client lifecycle management with:
#     - Shared registry (JSON + file lock)
#     - Automatic refcounting across processes
#     - Auto-cleanup of stale clusters
#     - Optional background watchdog to monitor cluster health
#     """
#
#     REGISTRY_PATH = os.path.join(tempfile.gettempdir(), "shared_dask_cluster.json")
#     REGISTRY_LOCK = FileLock(REGISTRY_PATH + ".lock")
#     WATCHDOG_INTERVAL = 60  # seconds between health checks
#
#     def __init__(self, **kwargs):
#         self.dask_client: Optional[Client] = None
#         self.own_dask_client: bool = False
#         self.logger = kwargs.get("logger") or logging.getLogger(__name__)
#         self._watchdog_task: Optional[asyncio.Task] = None
#         self._watchdog_stop = asyncio.Event()
#
#     # ----------------------------------------------------------------------
#     # Registry management
#     # ----------------------------------------------------------------------
#     @classmethod
#     def _read_registry(cls) -> Optional[dict]:
#         """Read registry JSON if it exists and is valid."""
#         if not os.path.exists(cls.REGISTRY_PATH):
#             return None
#         try:
#             with open(cls.REGISTRY_PATH, "r") as f:
#                 data = json.load(f)
#             if "address" not in data or not isinstance(data["address"], str):
#                 return None
#             return data
#         except (json.JSONDecodeError, OSError):
#             return None
#
#     @classmethod
#     def _write_registry(cls, data: dict) -> None:
#         """Write updated registry JSON atomically."""
#         tmp_path = cls.REGISTRY_PATH + ".tmp"
#         with open(tmp_path, "w") as f:
#             json.dump(data, f)
#         os.replace(tmp_path, cls.REGISTRY_PATH)
#
#     @classmethod
#     def _remove_registry(cls) -> None:
#         """Delete the registry file if present."""
#         with suppress(FileNotFoundError):
#             os.remove(cls.REGISTRY_PATH)
#
#     @classmethod
#     def _cleanup_stale_registry(cls, logger=None):
#         """Detect and remove stale registry entries if cluster is unreachable."""
#         registry = cls._read_registry()
#         if not registry:
#             return
#         try:
#             client = Client(address=registry["address"], timeout=5)
#             client.close()
#         except Exception:
#             if logger:
#                 logger.warning(
#                     f"Detected stale Dask cluster registry at {registry.get('address')}. Cleaning up."
#                 )
#             cls._remove_registry()
#
#     # ----------------------------------------------------------------------
#     # Dask client initialization
#     # ----------------------------------------------------------------------
#     def _init_dask_client(
#         self,
#         dask_client: Optional[Client] = None,
#         *,
#         logger=None,
#         scheduler_address: Optional[str] = None,
#         use_remote_cluster: bool = False,
#         n_workers: int = 2,
#         threads_per_worker: int = 1,
#         processes: bool = False,
#         asynchronous: bool = False,
#         memory_limit: str = "auto",
#         local_directory: Optional[str] = None,
#         silence_logs: str = "info",
#         resources: Optional[dict] = None,
#         timeout: int = 30,
#         watchdog: bool = True,
#     ):
#         """Initialize or attach to a shared Dask client."""
#         self.logger = logger or self.logger
#         self.dask_client = dask_client
#         self.own_dask_client = False
#
#         # Silence excessive logging
#         logging.getLogger("distributed.scheduler").setLevel(logging.WARNING)
#         logging.getLogger("distributed.worker").setLevel(logging.WARNING)
#         logging.getLogger("distributed.shuffle._scheduler_plugin").setLevel(logging.ERROR)
#
#         # 1️⃣ Try reusing existing client
#         if self.dask_client is None:
#             with suppress(ValueError, RuntimeError):
#                 self.dask_client = get_client()
#
#         # 2️⃣ Try remote cluster connection
#         if self.dask_client is None and use_remote_cluster and scheduler_address:
#             try:
#                 self.dask_client = Client(address=scheduler_address, timeout=timeout)
#                 self.own_dask_client = True
#                 self.logger.info(
#                     f"Connected to external Dask scheduler at {scheduler_address}. "
#                     f"Dashboard: {self.dask_client.dashboard_link}"
#                 )
#                 if watchdog:
#                     self._start_watchdog()
#                 return
#             except Exception as e:
#                 self.logger.warning(
#                     f"Failed to connect to remote Dask scheduler: {e}. Falling back to local cluster."
#                 )
#
#         # 3️⃣ Shared local cluster via registry
#         with self.REGISTRY_LOCK:
#             self._cleanup_stale_registry(self.logger)
#             registry = self._read_registry()
#
#             if registry:
#                 try:
#                     self.dask_client = Client(address=registry["address"], timeout=timeout)
#                     registry["refcount"] = registry.get("refcount", 0) + 1
#                     self._write_registry(registry)
#                     self.logger.info(
#                         f"Reusing existing LocalCluster at {registry['address']} (refcount={registry['refcount']})."
#                     )
#                     if watchdog:
#                         self._start_watchdog()
#                     return
#                 except Exception:
#                     self.logger.warning("Existing cluster unreachable. Recreating.")
#                     self._remove_registry()
#
#             # Create a new local cluster
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
#             registry = {"address": cluster.scheduler_address, "refcount": 1}
#             self._write_registry(registry)
#             self.logger.info(
#                 f"Started new LocalCluster ({n_workers} workers × {threads_per_worker} threads). "
#                 f"Dashboard: {self.dask_client.dashboard_link}"
#             )
#
#         if watchdog:
#             self._start_watchdog()
#
#     # ----------------------------------------------------------------------
#     # Watchdog logic
#     # ----------------------------------------------------------------------
#     def _start_watchdog(self):
#         """Spawn a background watchdog that monitors registry health."""
#         async def watchdog_loop():
#             while not self._watchdog_stop.is_set():
#                 await asyncio.sleep(self.WATCHDOG_INTERVAL)
#                 try:
#                     self._cleanup_stale_registry(self.logger)
#                 except Exception as e:
#                     self.logger.warning(f"Dask watchdog encountered an error: {e}")
#
#         try:
#             loop = asyncio.get_event_loop()
#             if loop.is_running():
#                 self._watchdog_task = loop.create_task(watchdog_loop())
#                 self.logger.debug("Started Dask registry watchdog (async).")
#         except RuntimeError:
#             # Fallback for synchronous usage
#             self.logger.debug("Watchdog skipped (no active event loop).")
#
#     async def _stop_watchdog(self):
#         """Stop the watchdog loop gracefully."""
#         self._watchdog_stop.set()
#         if self._watchdog_task:
#             await asyncio.wait([self._watchdog_task], timeout=5)
#             self._watchdog_task = None
#
#     # ----------------------------------------------------------------------
#     # Client cleanup
#     # ----------------------------------------------------------------------
#     def _close_dask_client(self):
#         """Safely close client and update registry reference count."""
#         if not self.dask_client:
#             return
#
#         with self.REGISTRY_LOCK:
#             registry = self._read_registry()
#
#             if registry and "refcount" in registry:
#                 registry["refcount"] = max(0, registry["refcount"] - 1)
#                 if registry["refcount"] == 0:
#                     self.logger.info("Reference count 0 — closing LocalCluster.")
#                     try:
#                         cluster = getattr(self.dask_client, "cluster", None)
#                         self.dask_client.close()
#                         if cluster:
#                             cluster.close()
#                     except Exception as e:
#                         self.logger.warning(f"Error closing Dask cluster: {e}")
#                     self._remove_registry()
#                 else:
#                     self._write_registry(registry)
#                     self.logger.debug(
#                         f"Decremented LocalCluster refcount to {registry['refcount']}."
#                     )
#             else:
#                 with suppress(Exception):
#                     self.dask_client.close()
#                 self.logger.debug("Closed Dask client without registry tracking.")
#
#         # Stop watchdog if active
#         if self._watchdog_task:
#             asyncio.create_task(self._stop_watchdog())
#
#
# # ----------------------------------------------------------------------
# # Shared Dask session (sync + async)
# # ----------------------------------------------------------------------
# def shared_dask_session(*, async_mode: bool = True, **kwargs):
#     """
#     Context manager for a shared Dask session (supports async + sync).
#
#     Example:
#         async with shared_dask_session(logger=logger) as client:
#             ...
#
#         with shared_dask_session(async_mode=False) as client:
#             ...
#     """
#     mixin = DaskClientMixin()
#     mixin._init_dask_client(**kwargs)
#
#     if async_mode:
#         @asynccontextmanager
#         async def _async_manager():
#             try:
#                 yield mixin.dask_client
#             finally:
#                 mixin._close_dask_client()
#         return _async_manager()
#     else:
#         @contextmanager
#         def _sync_manager():
#             try:
#                 yield mixin.dask_client
#             finally:
#                 mixin._close_dask_client()
#         return _sync_manager()
#
