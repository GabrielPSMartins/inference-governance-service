import time
from collections import defaultdict
from uuid import UUID

RATE_LIMIT_MAX_REQUESTS = 5
RATE_LIMIT_WINDOW_SECONDS = 60

_request_log: dict[UUID, list[float]] = defaultdict(list)


def is_rate_limited(user_id: UUID) -> bool:
    """
    Verifica se o usuário ultrapassou o limite de requisições permitidas
    dentro da janela de tempo configurada.
    """
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW_SECONDS

    timestamps = _request_log[user_id]
    timestamps[:] = [ts for ts in timestamps if ts > window_start]

    if len(timestamps) >= RATE_LIMIT_MAX_REQUESTS:
        return True

    timestamps.append(now)
    return False