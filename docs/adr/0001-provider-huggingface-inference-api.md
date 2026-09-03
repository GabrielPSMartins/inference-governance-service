# ADR-0001: Uso da Hugging Face Inference API como provedor de LLM

**Status:** Aceito
**Data:** 2026-08-20

## Contexto
O projeto exige a integração com um provedor de modelo de linguagem (LLM) para
gerar respostas de inferência. Provedores comerciais como OpenAI e Anthropic
possuem custo por uso, o que não é desejável nesta fase de aprendizado e
portfólio. Além disso, o ambiente de desenvolvimento local não possui Docker
ou Ollama instalados, o que eliminaria a opção de rodar modelos localmente
sem uma etapa adicional de setup.

## Alternativas Consideradas
- **OpenAI / Anthropic API:** Prós — qualidade de resposta e documentação
  excelentes. Contras — custo por uso, incompatível com o objetivo de um
  projeto de portfólio sem custo.
- **Ollama (modelo local):** Prós — sem custo, sem rate limit externo,
  controle total. Contras — exige instalação e configuração adicional
  (não disponível no ambiente atual); esconde problemas reais de rede,
  latência e falhas remotas que o projeto pretende justamente treinar.
- **Hugging Face Inference API:** Prós — gratuita (com rate limit),
  não exige setup local, expõe os mesmos desafios de engenharia que uma
  API comercial (latência de rede, timeouts, cold start, falhas HTTP).
  Contras — rate limits mais agressivos, qualidade de resposta inferior
  a modelos comerciais, possível indisponibilidade momentânea do modelo.

## Decisão
Utilizar a Hugging Face Inference API como provedor de LLM nesta fase do
projeto, iniciando com um modelo de chat leve disponível no free tier
(a ser validado empiricamente na Camada de Orquestração, já que a
disponibilidade de modelos gratuitos muda com frequência).

## Consequências
- O projeto fica sujeito aos rate limits e eventual instabilidade do
  free tier da Hugging Face, o que reforça a necessidade real de uma
  Camada de Orquestração robusta (retries, tratamento de erro).
- A contagem de tokens não pode usar `tiktoken` (específico da OpenAI);
  será necessário usar o tokenizer específico do modelo escolhido,
  via biblioteca `transformers`.
- Não há custo financeiro associado ao desenvolvimento e testes.