# 🔗 Arquiteto-Mentor Vínculo

Uma skill do Claude que combina três papéis num só: **engenheiro mobile sénior** (React Native Expo + Supabase), **engenheiro de ingestão de dados** (transforma mensagens de WhatsApp em lançamentos financeiros) e **mentor financeiro comportamental** para casais.

> Construída para o [App Vínculo](#) — um app financeiro B2C para casais que reduz a carga mental da gestão doméstica em vez de só mostrar números.

## Por que essa skill existe

Apps financeiros de casal morrem por dois motivos: (1) ninguém tem paciência de abrir o app e digitar cada gasto, e (2) quando um lançamento sai errado, a confiança no app cai e as pessoas voltam pro caderninho.

Essa skill resolve os dois problemas ao mesmo tempo:
- **Zero digitação**: o casal manda um áudio, um print de comprovante ou o PDF da fatura pelo WhatsApp — a skill projeta o pipeline que extrai e estrutura o lançamento.
- **Zero erro silencioso**: nenhum lançamento é gravado sem antes ser confirmado pelo utilizador, e qualquer extração de baixa confiança vira uma pergunta objetiva em vez de um "chute".

## O que a skill sabe fazer

| Área | O que ela projeta |
| :--- | :--- |
| 📱 Mobile (React Native Expo) | Componentes, navegação e integração com Supabase, sempre em React Native — nunca React Web |
| 🗄️ Banco de dados (Supabase) | Modelagem de tabelas, políticas de Row Level Security (RLS) por família |
| 💬 Ingestão via WhatsApp | Pipeline separado por tipo de mídia — áudio, imagem/print, documento/PDF — com schema de extração padrão, deduplicação e fluxo de confirmação obrigatória |
| 🎮 Gamificação | Cálculo determinístico de pontos por carga mental (`scripts/utility.py`), com recompensas coletivas do casal |
| 🧠 Economia comportamental | *Nudges* positivos em vez de alertas, sempre enquadrados como redução de carga mental |

## Estrutura do repositório

```
.
├── SKILL.md                          # Definição da skill (gatilhos, fluxo, regras)
├── references/
│   ├── REFERENCE.md                  # Domínio geral, schema de dados, gamificação
│   └── whatsapp-ingestion.md         # Pipeline completo de ingestão via WhatsApp
├── scripts/
│   ├── utility.py                    # Calculadora de pontos de gamificação
│   └── extract_transaction.py        # Validador/normalizador de lançamentos extraídos
├── assets/
│   └── template-schema.json          # Schema JSON da resposta estruturada da skill
└── tests/
    └── evals.json                    # Casos de teste de acionamento e corretude
```

## Exemplo rápido

```bash
python scripts/extract_transaction.py \
  --tipo imagem --valor 45.90 --descricao "Mercado Extra" \
  --categoria alimentacao --confianca 0.92
```

```json
{
  "status": "pronto_para_confirmacao",
  "lancamento": { "valor": 45.9, "tipo": "gasto", "categoria": "alimentacao", "...": "..." },
  "requer_pergunta_ao_utilizador": false,
  "mensagem_sugerida": "Confirma o lançamento de R$45.90 (gasto, categoria: alimentacao)?"
}
```

Quando a confiança da extração é baixa, o script nunca inventa um valor — ele sinaliza `aguardando_esclarecimento` e devolve a pergunta certa para o utilizador.

## Como usar

1. Copie a pasta desta skill para o diretório de skills do seu ambiente Claude.
2. A skill aciona automaticamente quando o pedido envolve código mobile do Vínculo, modelagem Supabase, gamificação ou ingestão de lançamentos via WhatsApp.
3. Para rodar os casos de teste, veja `tests/evals.json` e a skill `skill-creator`.

## Roadmap / ideias em aberto

- [ ] Conciliação automática entre lançamento manual/WhatsApp e importação de extrato bancário
- [ ] Suporte a múltiplas moedas
- [ ] Exportação de `references/whatsapp-ingestion.md` como diagrama de sequência

## Contribuindo

Contribuições são bem-vindas — veja [CONTRIBUTING.md](CONTRIBUTING.md).

## Licença

Distribuído sob a licença MIT — veja [LICENSE](LICENSE).
