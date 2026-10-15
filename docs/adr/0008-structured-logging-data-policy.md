# ADR-0008: Logs estruturados em JSON e política de dados nos logs

**Status:** Aceito
**Data:** 2026-10-15

## Contexto
Até aqui o serviço não registrava nada além do log de acesso do uvicorn.
Não havia como responder perguntas básicas de operação: quantos tokens um
usuário consumiu, por que uma requisição foi bloqueada, quanto tempo o
provider levou, ou por que uma resposta veio vazia. Ao mesmo tempo, o
serviço trafega prompts e respostas de usuários, que podem conter dados
pessoais ou sensíveis, e não devem parar em arquivos de log.

## Alternativas Consideradas
- **Texto livre (`logging` padrão com f-strings):** Prós — zero esforço.
  Contras — difícil de filtrar e agregar; cada mensagem tem um formato.
- **Biblioteca de logging estruturado (ex.: `structlog`, `loguru`):** Prós
  — API mais ergonômica, processadores prontos. Contras — dependência nova
  para resolver algo que a stdlib já resolve com um `Formatter` de poucas
  linhas.
- **JSON com a stdlib (`logging` + `Formatter` próprio):** Prós — sem
  dependência, uma linha JSON por evento, pronta para qualquer coletor
  (Loki, CloudWatch, ELK). Contras — um pouco de código próprio
  (formatter, filtro e helper).
- **Persistir eventos em banco:** Prós — consultas ricas sobre uso.
  Contras — infraestrutura nova, fora do escopo deste estágio.

## Decisão
Usar o `logging` da stdlib com um `JsonFormatter` próprio
(`app/core/logging.py`), configurado só no logger `app`, sem mexer na
configuração de logs do uvicorn. Cada log é um **evento** nomeado, emitido
via `log_event(logger, level, event, **campos)`:

| Evento | Onde | Campos principais |
|---|---|---|
| `inference_completed` | orquestrador | `user_id`, `model`, `input_tokens`, `output_tokens`, `reasoning_tokens`, `finish_reason`, `provider_latency_ms` |
| `provider_error` | orquestrador | `user_id`, `error_type`, `detail`, `upstream_status_code`, `status_code`, `provider_latency_ms` |
| `request_blocked` | router | `reason` (`rate_limit` ou `prompt_injection`), `user_id`, `status_code` |
| `request_failed` | middleware | `method`, `path`, `exception` (traceback) |
| `request_completed` | middleware | `method`, `path`, `status_code`, `total_latency_ms` |

Todo evento tem `timestamp` (ISO 8601, UTC), `level`, `logger`, `event` e
`request_id` (ADR-0009), que liga os eventos de uma mesma requisição.

**Política de dados:** os logs guardam só metadados. O conteúdo do prompt
e o da resposta do modelo **nunca** são logados. O `user_id` é logado,
por ser um identificador opaco necessário para auditoria de uso.

## Consequências
- Cada requisição gera ao menos o `request_completed`, e as de inferência
  geram também o evento de domínio correspondente; a latência total e o
  status HTTP ficam no `request_completed`, pois só o middleware os conhece.
- Respostas vazias de modelos de raciocínio passam a ser diagnosticáveis
  pelo `finish_reason="length"` e pelos `reasoning_tokens`.
- O `detail` do `provider_error` é a mensagem do SDK. Ela descreve o erro
  do upstream e não inclui o prompt, mas, se um provider futuro ecoar o
  conteúdo da requisição no erro, esta política deve ser revista.
- A política depende de disciplina: nada impede tecnicamente que alguém
  passe o prompt para `log_event`. Os testes (Etapa 4) devem verificar que
  o prompt não aparece nos logs.
- Os eventos ficam só no stdout; persistência e métricas agregadas ficam
  como trabalho futuro.
