from __future__ import annotations
from multiprocessing import cpu_count

from loguru import logger


def get_parallelization_workers(n_jobs: int = 1) -> int:
    if n_jobs == 0:
        logger.warning("Нельзя выбрать ноль процессов. Параллельные вычисления отключены.")
        return 1
    if n_jobs == -1:
        logger.info(f"Передано n_jobs = {n_jobs}. Будут использованы все доступные ядра ({cpu_count()}).")
        return cpu_count()
    if n_jobs < -1:
        logger.info(
            f"Передано отрицательное значение n_jobs = {n_jobs}. Будут использованы {-n_jobs} процесса(ов)."
        )
        n_jobs = -n_jobs
    if n_jobs > cpu_count():
        logger.warning(
            (
                f"Выбрано количество n_jobs = {n_jobs} большее, чем доступное число ядер: {cpu_count()}.\n"
                f"Будут использованы все доступные ядра ({cpu_count()})."
            )
        )

    return n_jobs
