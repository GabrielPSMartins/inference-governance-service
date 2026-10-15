# ADR-0009: `request_id` gerado por middleware e propagado por `contextvar`

**Status:** Aceito
**Data:** 2026-10-15

## Contexto
O `request_id` era criado pelo `default_factory` do `InferenceResponse`,
ou seja, só existia quando a inferência dava certo. As respostas 400, 422,
429 e 500 saíam sem ID, e não havia como ligar um log, uma resposta ao
cliente e uma chamada ao provider à mesma requisição. Além disso, o
campo `latency_ms` era descrito como tempo "total", mas media só a
chamada ao provider.

## Alternativas Consideradas
- **Gerar o ID no router e repassá-lo por parâmetro:** Prós — explícito.
  Contras — não cobre os erros que acontecem antes da rota (422 da
  validação) nem as exceções não tratadas; obriga a passar o ID por todas
  as funções.
- **`BaseHTTPMiddleware` do Starlette:** Prós — API simples
  (`call_next`). Contras — historicamente teve problemas de propagação de
  `contextvars` e de tratamento de exceções, por executar a aplicação em
  outra task.
- **Middleware ASGI puro + `contextvar`:** Prós — roda na mesma task da
  rota, então a `contextvar` é vista em toda a requisição sem passar o ID
  por parâmetro; envolve também os 422 e os erros inesperados. Contras —
  API de mais baixo nível (mensagens ASGI).
- **Aceitar um `X-Request-ID` enviado pelo cliente:** Prós — permite
  rastrear a partir de um sistema chamador. Contras — sem autenticação, o
  cliente poderia forjar ou repetir IDs e poluir a auditoria.

## Decisão
Um middleware ASGI puro (`app/core/middleware.py`) gera um UUID4 para cada
requisição HTTP, o guarda em uma `contextvar` (`app/core/context.py`) e:
- devolve os headers `X-Request-ID` e `X-Process-Time-Ms` em toda
  resposta, inclusive nas de erro;
- converte exceções não tratadas em 500 com mensagem genérica, logando o
  traceback no evento `request_failed`;
- emite o evento `request_completed` com status e latência total.

O ID sempre nasce no servidor; um `X-Request-ID` vindo do cliente é
ignorado. O `InferenceResponse.request_id` passa a ler a `contextvar`, e
um filtro de logging anexa o mesmo ID a todo log.

Latências:
- `latency_ms` no corpo da resposta = tempo da chamada ao provider
  (descrição corrigida no schema).
- `X-Process-Time-Ms` = tempo do serviço até o início da resposta.
- `total_latency_ms` no `request_completed` = tempo até o fim da resposta.

## Consequências
- Corpo, header e logs compartilham o mesmo ID, e qualquer resposta,
  inclusive de erro, pode ser rastreada até seus logs.
- Verificado com 20 requisições concorrentes: cada uma recebeu um ID
  distinto, e seus eventos de log carregaram o ID correto.
- Os erros 500 deixam de passar pelo `ServerErrorMiddleware` do Starlette
  (exceto se a resposta já tiver começado a ser enviada, caso em que a
  exceção é relançada).
- Para encadear com um sistema chamador no futuro, a decisão de ignorar o
  header do cliente pode ser revista junto com a autenticação.
