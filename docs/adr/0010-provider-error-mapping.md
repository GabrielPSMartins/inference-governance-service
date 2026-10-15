# ADR-0010: Mapeamento de erros do provider para HTTP 502, 503 e 504

**Status:** Aceito
**Data:** 2026-10-15

## Contexto
As exceções do SDK do Groq não eram tratadas: um modelo inexistente, por
exemplo, gerava um 500 com `groq.NotFoundError` no log. O cliente não
conseguia distinguir "o serviço tem um bug" de "o provider está fora", e
o restante do código ficaria acoplado ao SDK se passasse a capturar as
exceções dele diretamente. O SDK usava ainda o timeout padrão de 60 s por
tentativa, o que, com `max_retries=3`, permitia esperas de mais de 4
minutos.

## Alternativas Consideradas
- **Capturar as exceções do SDK no router:** Prós — direto. Contras —
  acopla a camada HTTP ao SDK, contrariando a abstração do ADR-0002.
- **Repassar o status do upstream ao cliente (ex.: 401 → 401):** Prós —
  mais informação. Contras — engana o cliente: um 401 do Groq é falha de
  configuração **nossa**, não credencial inválida do cliente.
- **Exceções de domínio traduzidas no provider + handler global:** Prós —
  o SDK fica isolado no `GroqProvider`; o resto do serviço conhece só a
  hierarquia de domínio; mensagens genéricas ao cliente. Contras — uma
  camada a mais de exceções.

## Decisão
O `GroqProvider` traduz as exceções do SDK (`groq.APIError`) para a
hierarquia de `app/providers/errors.py`, e um exception handler em
`app/main.py` as converte em resposta HTTP:

| Exceção do SDK | Exceção de domínio | HTTP |
|---|---|---|
| `APITimeoutError` | `ProviderTimeoutError` | 504 |
| `APIConnectionError` | `ProviderUnavailableError` | 503 |
| `RateLimitError` (429) ou status 503 | `ProviderUnavailableError` | 503 |
| demais (`401`, `404`, `500`, resposta inválida…) | `ProviderError` | 502 |

A ordem dos testes importa: `APITimeoutError` é subclasse de
`APIConnectionError`. Essas exceções só chegam ao nosso código depois de o
SDK esgotar os retries (ADR-0007).

O cliente recebe só uma mensagem genérica por categoria. O detalhe
(classe da exceção, status do upstream, mensagem do SDK) vai para o
evento `provider_error` (ADR-0008).

O timeout do cliente Groq passa a ser explícito: 20 s por tentativa.

## Consequências
- Erros de provider deixam de aparecer como 500; o 500 fica reservado para
  bugs do próprio serviço.
- 503 sinaliza ao cliente que tentar de novo depois faz sentido; 502 e 504
  indicam falha ou lentidão do upstream.
- Um novo provider só precisa implementar a própria tradução para a mesma
  hierarquia.
- Com 20 s por tentativa e 3 retries, o pior caso de espera fica perto de
  1min30s; reduzir mais exigiria diminuir os retries ou criar um prazo
  total (deadline), decisão adiada.
- Os 503 ainda não enviam o header `Retry-After`.
