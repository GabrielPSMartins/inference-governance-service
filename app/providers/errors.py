class ProviderError(Exception):

    status_code: int = 502
    public_message: str = "Falha ao obter resposta do provedor de IA."

    def __init__(
        self,
        detail: str,
        *,
        error_type: str,
        upstream_status_code: int | None = None,
    ) -> None:
        super().__init__(detail)
        self.error_type = error_type
        self.upstream_status_code = upstream_status_code


class ProviderUnavailableError(ProviderError):
    """Provedor fora do ar, sobrecarregado ou limitando nossas chamadas."""

    status_code = 503
    public_message = "Provedor de IA temporariamente indisponível. Tente novamente mais tarde."


class ProviderTimeoutError(ProviderError):
    """Provedor não respondeu dentro do tempo limite."""

    status_code = 504
    public_message = "O provedor de IA não respondeu a tempo."
