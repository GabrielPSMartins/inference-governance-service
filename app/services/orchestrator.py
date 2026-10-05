import time

from app.providers.base import LLMProvider, ProviderResponse
from app.schemas.inference import InferenceRequest, InferenceResponse

SYSTEM_PROMPT = """
Você é um assistente de IA altamente capaz, neutro, direto e honesto.

Siga rigorosamente estas diretrizes em todas as respostas:

1. CLAREZA E OBJETIVIDADE:
   - Responda de forma direta, sem enrolação ou introduções desnecessárias.
   - Adapte a profundidade da resposta à complexidade da pergunta.

2. PRECISÃO E HONESTIDADE:
   - Se você não souber uma informação ou se o contexto for insuficiente, admita claramente.
   - Não invente fatos, dados, links ou citações (evite alucinações).
   - Se uma pergunta for ambígua, peça esclarecimentos ou declare suas premissas antes de responder.

3. ESTILO E FORMATO:
   - Use formatação Markdown (listas, negrito, blocos de código) para facilitar a leitura.
   - Mantenha um tom profissional, amigável e prestativo, evitando respostas robotizadas ou condescendentes.
"""


async def run_inference(
    request: InferenceRequest, provider: LLMProvider
) -> InferenceResponse:
    """
    Orquestra a chamada ao provedor de LLM: monta o prompt final,
    mede latência, e formata o resultado bruto do provider como
    InferenceResponse, pronto para devolver ao cliente.

    O provider chega por parâmetro em vez de ser criado aqui, para que o
    orquestrador dependa só do contrato LLMProvider (ADR-0002).
    """
    start_time = time.perf_counter()

    provider_response: ProviderResponse = await provider.generate(
        prompt=request.prompt,
        system_prompt=SYSTEM_PROMPT,
        max_tokens=request.max_tokens,
        temperature=request.temperature,
    )

    elapsed_ms = (time.perf_counter() - start_time) * 1000

    return InferenceResponse(
        response=provider_response.text,
        model=provider_response.model,
        input_tokens=provider_response.input_tokens,
        output_tokens=provider_response.output_tokens,
        latency_ms=elapsed_ms,
        temperature=request.temperature,
    )