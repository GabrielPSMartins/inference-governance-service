import time
from uuid import UUID

RATE_LIMIT_MAX_REQUESTS = 5
RATE_LIMIT_WINDOW_SECONDS = 60

_request_log: dict[UUID, list[float]] = {}
_last_purge: float = 0.0


def _purge_inactive_users(now: float) -> None:
    """
    Remove do log os usuários sem nenhuma requisição dentro da janela.

    Sem isso, o dicionário só cresce: um usuário que nunca mais volta
    mantém sua chave para sempre, e como o user_id é livre, um cliente
    rotacionando UUIDs inflaria a memória. A varredura roda no máximo uma
    vez por janela, para não custar O(n) em toda requisição. Ela limita a
    memória aos usuários ativos no último minuto; não impede o abuso por
    rotação dentro da janela, o que só a autenticação resolve.
    """
    global _last_purge
    if now - _last_purge < RATE_LIMIT_WINDOW_SECONDS:
        return

    window_start = now - RATE_LIMIT_WINDOW_SECONDS
    inactive = [
        user_id
        for user_id, timestamps in _request_log.items()
        if not timestamps or timestamps[-1] <= window_start
    ]
    for user_id in inactive:
        del _request_log[user_id]
    _last_purge = now


def is_rate_limited(user_id: UUID) -> bool:
    """
    Verifica se o usuário ultrapassou o limite de requisições permitidas
    dentro da janela de tempo configurada.
    """
    now = time.time()
    _purge_inactive_users(now)
    window_start = now - RATE_LIMIT_WINDOW_SECONDS

    timestamps = [ts for ts in _request_log.get(user_id, []) if ts > window_start]

    if len(timestamps) >= RATE_LIMIT_MAX_REQUESTS:
        _request_log[user_id] = timestamps
        return True

    timestamps.append(now)
    _request_log[user_id] = timestamps
    return False
