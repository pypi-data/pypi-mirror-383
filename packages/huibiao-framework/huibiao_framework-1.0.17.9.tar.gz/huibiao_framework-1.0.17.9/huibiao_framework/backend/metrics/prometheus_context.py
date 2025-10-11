import os
import shutil
from loguru import logger
from fastapi import FastAPI


class PrometheusContext:
    PROM_MULTI_PROC_OS_VAR = "PROMETHEUS_MULTIPROC_DIR"  #
    DEFAULT_PROMETHEUS_MULTIPROC_DIR = "/temp/prometheus_multiproc_dir"

    @classmethod
    def get_prometheus_multiproc_dir(cls):
        return os.environ.get(
            cls.PROM_MULTI_PROC_OS_VAR, cls.DEFAULT_PROMETHEUS_MULTIPROC_DIR
        )

    @classmethod
    def init(cls):
        """
        Initialize the Prometheus multiprocessing directory.
        """
        prom_dir = os.environ.get(cls.PROM_MULTI_PROC_OS_VAR, None)
        if not prom_dir:
            logger.warning(
                f"Prometheus multiprocessing directory is not set. Using default directory {cls.DEFAULT_PROMETHEUS_MULTIPROC_DIR}."
            )
            prom_dir = cls.DEFAULT_PROMETHEUS_MULTIPROC_DIR
            os.environ["prometheus_multiproc_dir"] = prom_dir
        else:
            logger.info(
                f"Using Prometheus multiprocessing directory from environment variable: {prom_dir}"
            )

        if os.path.exists(prom_dir):
            shutil.rmtree(prom_dir)
            logger.info(
                f"Removed existing Prometheus multiprocessing directory: {prom_dir}"
            )

        os.makedirs(prom_dir, exist_ok=True)
        logger.info(f"Created new Prometheus multiprocessing directory: {prom_dir}")

    @classmethod
    def mount_prometheus_endpoint(cls, app: FastAPI):
        """
        Mount the Prometheus metrics endpoint on the given application.
        """
        from prometheus_client import CollectorRegistry, multiprocess, make_asgi_app

        registry = CollectorRegistry()
        multiprocess.MultiProcessCollector(registry=registry)
        app.mount("/metrics", make_asgi_app(registry=registry))
