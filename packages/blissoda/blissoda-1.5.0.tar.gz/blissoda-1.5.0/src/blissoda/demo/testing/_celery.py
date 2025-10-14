import time
from typing import Any

from ewoksjob.client import Future
from ewoksjob.client.celery.utils import get_not_finished_futures

from ._display import print_message


def wait_workflows(*futures: Future, timeout: int = 30) -> Any:
    if not futures:
        futures = get_not_finished_futures()

    t0 = time.time()
    for future in futures:
        timepassed = time.time() - t0
        _ = future.result(timeout=timeout - timepassed)
        print_message(f"Job {future.uuid!r} finished", "info")
