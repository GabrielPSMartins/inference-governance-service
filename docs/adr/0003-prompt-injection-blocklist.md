# ADR-0003: Detecção de prompt injection via blocklist de padrões

**Status:** Aceito
**Data:** 2026-08-20

## Contexto
A Camada de Validação/Segurança precisa detectar tentativas de manipulação
do sistema através do conteúdo do prompt (prompt injection). Existem
abordagens de complexidade e robustez variadas para esse problema, desde
heurísticas simples até modelos classificadores dedicados.

## Alternativas Consideradas
- **Blocklist de padrões (heurística):** Prós — simples, rápida, sem
  dependências externas, sem custo de inferência adicional, fácil de
  auditar. Contras — contornável por variações do ataque (sinônimos,
  outro idioma, ofuscação de texto).
- **Modelo classificador dedicado:** Prós — significativamente mais
  robusto, generaliza melhor. Contras — adiciona latência (mais uma
  chamada de inferência antes da chamada principal), mais uma
  dependência externa a gerenciar, complexidade prematura para a fase
  atual do projeto.
- **Abordagem híbrida (blocklist + classificador):** Prós — equilibra
  custo e robustez. Contras — complexidade de implementação prematura
  para os objetivos didáticos atuais do projeto.

## Decisão
Implementar a detecção via blocklist de padrões conhecidos nesta fase do
projeto, priorizando simplicidade e ausência de dependências externas.

## Consequências
- A proteção contra prompt injection é básica e **contornável** por
  ataques mais sofisticados — não deve ser considerada suficiente para
  um ambiente de produção real.
- Não há custo ou latência adicional de inferência para essa validação.
> **TODO registrado:** avaliar, em fase futura, upgrade para um modelo
> classificador dedicado de prompt injection, quando o projeto justificar
> esse nível de robustez.