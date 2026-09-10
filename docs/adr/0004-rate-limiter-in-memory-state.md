# ADR-0004: Estado do Rate Limiter em memória local do processo

**Status:** Aceito
**Data:** 2026-08-20

## Contexto
A Camada de Validação/Segurança precisa impedir abuso por volume de
requisições (rate limiting), o que exige manter estado compartilhado entre
chamadas — quantas requisições um determinado `user_id` fez dentro de uma
janela de tempo recente. É necessário decidir onde esse estado vive.

O ambiente de execução atual do projeto é um único processo Uvicorn,
rodando localmente, sem Docker, Redis ou qualquer infraestrutura externa
disponível.

## Alternativas Consideradas
- **Memória local do processo (estrutura de dados em Python, ex.
  dicionário):** Prós — nenhuma dependência externa nova, implementação
  simples, resolve o problema real nesta fase do projeto. Contras — o
  estado se perde a cada reinicialização do processo; não é compartilhado
  entre múltiplas instâncias do serviço, caso o sistema venha a escalar
  horizontalmente.
- **Armazenamento externo compartilhado (ex. Redis):** Prós — estado
  persistente e compartilhado entre múltiplas instâncias, robusto para
  ambientes de produção com escala horizontal. Contras — adiciona uma
  dependência de infraestrutura externa que o ambiente atual não possui,
  complexidade desnecessária para os objetivos didáticos desta fase.

## Decisão
Implementar o rate limiter com estado mantido em memória local do
processo (um dicionário Python, com janela deslizante por timestamps),
sem dependências externas.

## Consequências
- O histórico de requisições é perdido a cada reinicialização do servidor.
- Caso o serviço seja executado em múltiplas instâncias simultâneas
  (ex. atrás de um load balancer), cada instância mantém seu próprio
  estado isolado — um usuário poderia contornar o limite sendo roteado
  para instâncias diferentes. Essa limitação exigiria migração para um
  armazenamento externo compartilhado (ex. Redis) caso o projeto evolua
  para esse cenário.
- A implementação atual **não é thread-safe**: em cenários de alta
  concorrência real, existe risco teórico de condição de corrida (race
  condition) na leitura/escrita do estado compartilhado. O risco prático
  é considerado baixo no estágio atual do projeto, mas não é adequado
  para produção sob alta concorrência sem revisão.
> **TODO registrado:** avaliar migração para Redis (ou solução
> equivalente) caso o projeto evolua para múltiplas instâncias ou
> ambiente de produção com concorrência real relevante.