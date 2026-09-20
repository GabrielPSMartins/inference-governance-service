# ADR-0007: Uso do retry nativo do SDK do Groq (supera o ADR-0005)

**Status:** Aceito (supera o ADR-0005)
**Data:** 2026-09-20

## Contexto
O ADR-0005 definiu uma estratégia de retry com exponential backoff
implementada manualmente, motivada por comportamentos de falha
transitória (cold start `503`) específicos da Hugging Face Inference API.
Com a troca de provider para Groq (ADR-0006), a biblioteca oficial `groq`
passou a ser usada — e sua documentação confirma que ela já implementa
retry automático com exponential backoff, por padrão, para erros de
conexão, timeout, `429` (rate limit) e `5xx`, configurável via
`max_retries`.

## Alternativas Consideradas
- **Manter retry customizado sobre o retry nativo do SDK:** Prós — controle
  total sobre a lógica. Contras — redundante; risco de compor atrasos
  (retry sobre retry) sem benefício real, já que o SDK oficial resolve o
  mesmo problema de forma testada pelo próprio mantenedor da biblioteca.
- **Usar apenas o retry nativo do SDK, configurando `max_retries`:** Prós
  — elimina código duplicado, confia em uma implementação testada
  diretamente contra a API real do provider, simplifica o
  `GroqProvider`. Contras — menos controle fino sobre o comportamento
  exato de espera entre tentativas, caso isso um dia seja necessário.

## Decisão
Remover a lógica de retry manual implementada para o Hugging Face
(ADR-0005) e utilizar o mecanismo de retry nativo da biblioteca `groq`,
configurando `max_retries` explicitamente na instanciação do cliente.

## Consequências
- O `GroqProvider` fica mais simples, sem loop de retry manual.
- O comportamento de retry passa a ser de responsabilidade da biblioteca
  oficial do provider — decisão consistente com o princípio de não
  reimplementar o que uma ferramenta já resolve de forma confiável.
- Caso surja necessidade futura de lógica de retry mais sofisticada
  (ex.: retry diferenciado por tipo de erro além do que o SDK oferece),
  esta decisão deve ser revisitada.