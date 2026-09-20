# ADR-0006: Troca de provider — de Hugging Face Inference Providers para Groq direto

**Status:** Aceito (supera o ADR-0001)
**Data:** 2026-09-20

## Contexto
A implementação do provider via Hugging Face Inference Providers (ADR-0001)
esbarrou em obstáculos práticos reais durante o desenvolvimento: (1) modelos
gated exigindo aprovação de licença, (2) modelos não implantados por nenhum
Inference Provider, (3) necessidade de habilitar explicitamente parceiros
terceiros na conta, e (4) exigência de cartão de crédito registrado para o
modo de cobrança "Routed by HF", mesmo dentro do crédito gratuito mensal.
Essa complexidade acumulada não se justifica para os objetivos didáticos do
projeto.

## Alternativas Consideradas
- **Persistir com Hugging Face, cadastrando cartão de crédito:** Prós —
  mantém a decisão original, acesso a milhares de modelos. Contras — exige
  fornecer dado de pagamento para um projeto de estudo/portfólio, decisão
  que o desenvolvedor optou por não tomar.
- **Persistir com Hugging Face, usando Custom Provider Key do Groq:**
  Prós — evita cartão na HF. Contras — mantém uma camada de indireção
  (HF como roteador) sem necessidade real, já que o Groq pode ser
  chamado diretamente.
- **Groq como provider direto (biblioteca oficial `groq`):** Prós — tier
  gratuito genuinamente sem cartão de crédito, biblioteca cliente oficial
  simples, API compatível com o padrão OpenAI já estudado, sem a
  complexidade de roteamento multi-provider da HF. Contras — cardápio de
  modelos gratuitos mais limitado e sujeito a mudança (modelos já saíram
  do tier gratuito do Groq no passado), sem acesso ao catálogo amplo do
  Hugging Face Hub.

## Decisão
Substituir o provider Hugging Face por uma implementação direta usando a
biblioteca oficial `groq` (`AsyncGroq`), mantendo a abstração `LLMProvider`
definida no ADR-0002 — a troca de provider não exige alteração em nenhuma
outra camada do sistema.

## Consequências
- O `HuggingFaceProvider`, `app/providers/huggingface.py`, e a dependência
  `huggingface_hub` são removidos do projeto.
- O catálogo de modelos gratuitos disponíveis é menor e muda com
  frequência; o modelo configurado deve ser verificado periodicamente em
  `console.groq.com/docs/models`.
- A abstração de provider (ADR-0002) se provou valiosa na prática: a troca
  de provider não exigiu nenhuma alteração na Camada de Entrada, Validação,
  ou na estrutura da Camada de Orquestração — apenas a criação de uma nova
  classe concreta.