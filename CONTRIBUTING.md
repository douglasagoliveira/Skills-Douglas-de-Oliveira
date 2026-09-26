# Contribuindo

Obrigado pelo interesse em melhorar esta skill! Algumas orientações rápidas:

## Estrutura de uma skill

Antes de propor mudanças, vale entender o padrão:
- `SKILL.md` — sempre curto (idealmente < 500 linhas), contém os gatilhos, o fluxo de execução e as regras de negócio.
- `references/` — documentação detalhada, carregada apenas quando necessária. Arquivos com mais de ~300 linhas devem ter um sumário no topo.
- `scripts/` — código determinístico (CLI, `argparse`, saída em JSON). Use para qualquer cálculo que não deva depender de interpretação do modelo.
- `assets/` — templates e schemas usados na saída final.
- `tests/evals.json` — casos de teste de acionamento (a skill dispara quando deveria?) e de corretude (a saída está certa?).

## Como propor uma mudança

1. Abra uma *issue* descrevendo o problema ou a melhoria antes de um PR grande — evita retrabalho.
2. Se estiver adicionando uma nova modalidade de ingestão (ex.: um novo tipo de mídia do WhatsApp), siga o padrão de `references/whatsapp-ingestion.md`: uma seção própria, com schema de saída explícito e critério de confiança mínima.
3. Todo script novo em `scripts/` deve:
   - Ser executável via CLI com `argparse`;
   - Nunca gravar dados diretamente — apenas validar/normalizar e devolver JSON;
   - Falhar de forma explícita (`sys.exit(1)` + mensagem em stderr), nunca silenciosamente.
4. Adicione ao menos um caso em `tests/evals.json` cobrindo o comportamento novo (acionamento correto e, se fizer sentido, um gatilho negativo).
5. Rode `python -m json.tool` (ou equivalente) nos arquivos JSON alterados antes de abrir o PR.

## Escopo

Esta skill é deliberadamente **B2C e doméstica**. Pedidos de funcionalidades de contabilidade empresarial (DRE, centro de custos, CNPJ) estão fora do escopo por design — não são bugs, são decisão de produto.

## Código de conduta

Seja gentil. O objetivo do próprio produto é reduzir tensão financeira em casais — o mesmo espírito vale para quem contribui aqui.
