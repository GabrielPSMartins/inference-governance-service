# ADR-0002: Abstração do provedor de LLM via interface (Dependency Inversion)

**Status:** Aceito
**Data:** 2026-08-20

## Contexto
A decisão registrada no ADR-0001 fixa a Hugging Face Inference API como
provedor atual, mas essa escolha pode mudar no futuro (ex.: adicionar
Ollama local, OpenAI, ou outro provedor). Se a Camada de Orquestração
chamar diretamente o SDK/API da Hugging Face, todo o restante do sistema
(validação, observabilidade, saída) ficaria acoplado a esse provedor
específico, exigindo reescrita em caso de troca ou expansão.

## Alternativas Consideradas
- **Chamada direta ao provedor:** Prós — mais simples e rápido de
  implementar agora. Contras — forte acoplamento; trocar ou adicionar
  um provedor exigiria alterar código em várias camadas do sistema.
- **Interface/abstração de provedor (Protocol ou ABC):** Prós — a
  Camada de Orquestração depende apenas de um contrato abstrato
  (ex.: método `generate`), não de uma implementação concreta;
  novos provedores são adicionados como novas classes que respeitam
  o mesmo contrato, sem alterar as demais camadas. Contras — introduz
  uma camada extra de abstração e complexidade inicial, mesmo havendo
  apenas um provedor real no momento.

## Decisão
Adotar uma interface abstrata (via `Protocol` ou `ABC` do Python) definindo
o contrato que qualquer provedor de LLM deve seguir. A implementação
concreta inicial (Hugging Face) será uma classe que satisfaz esse contrato,
mantendo as demais camadas do sistema desacopladas de detalhes específicos
do provedor.

## Consequências
- Adicionar um novo provedor no futuro (Ollama, OpenAI etc.) exige apenas
  criar uma nova classe compatível com o contrato, sem modificar as
  Camadas de Entrada, Validação, Observabilidade ou Saída.
- Aplica o Princípio da Inversão de Dependência (SOLID), decisão
  consciente de qualidade arquitetural em vez de simplicidade imediata.
- Exige que o desenvolvedor entenda o conceito de `Protocol`/`ABC` antes
  de implementar a primeira versão concreta do provedor — o que será
  abordado com calma quando chegarmos na Camada de Orquestração.