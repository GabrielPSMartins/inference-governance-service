# ADR-0005: Retry com Exponential Backoff na chamada ao provedor de LLM

**Status:** Aceito
**Data:** 2026-09-20

## Contexto
A documentação oficial da Hugging Face Serverless Inference API confirma
que, quando um modelo não está carregado em memória no momento da
requisição (cold start), a API retorna inicialmente um erro `503`,
recomendando nova tentativa após alguns instantes — sem especificar um
tempo exato de espera. Além disso, o free tier está sujeito a rate limits
não documentados com precisão (variam por popularidade do modelo e carga
atual). A Camada de Orquestração precisa lidar com essas falhas
transitórias de forma resiliente, sem sobrecarregar ainda mais um serviço
já instável.

## Alternativas Consideradas
- **Sem retry (falha imediata ao cliente):** Prós — implementação trivial,
  comportamento previsível. Contras — cold starts são um erro esperado e
  recuperável; expor isso diretamente ao cliente degrada a experiência
  sem necessidade.
- **Retry com espera fixa entre tentativas:** Prós — simples de
  implementar e entender. Contras — se o serviço externo está sobrecarregado,
  tentativas repetidas em intervalo curto e constante pioram a situação
  em vez de dar tempo de recuperação.
- **Retry com Exponential Backoff:** Prós — cada tentativa espera
  progressivamente mais tempo (ex.: 1s, 2s, 4s), reduzindo a carga sobre
  um serviço já sobrecarregado e aumentando a chance de sucesso conforme
  o tempo passa. Padrão reconhecido de mercado para falhas transitórias
  em serviços externos. Contras — aumenta a latência total percebida pelo
  cliente em caso de falhas repetidas; exige definir um número máximo de
  tentativas para evitar espera indefinida.

## Decisão
Implementar retry com exponential backoff na chamada ao provedor de LLM,
limitado a um número máximo de tentativas, aplicado especificamente para
erros transitórios recuperáveis (ex.: `503` de cold start). Erros não
recuperáveis (ex.: erro de autenticação, prompt rejeitado pelo modelo)
não acionam retry.

## Consequências
- Falhas transitórias (cold start) tornam-se, na maioria dos casos,
  transparentes para o cliente final, à custa de latência adicional.
- É necessário definir um número máximo de tentativas e um tempo base de
  espera — valores iniciais escolhidos de forma didática, sujeitos a
  ajuste com observação real de comportamento do provedor.
- Erros persistentes após todas as tentativas ainda devem ser propagados
  ao cliente de forma clara, não silenciada.