# Pipeline de Ingestão Financeira via WhatsApp

## Sumário
- [1. Visão Geral do Fluxo](#1-visão-geral-do-fluxo)
- [2. Roteamento por Tipo de Mídia](#2-roteamento-por-tipo-de-mídia)
- [3. Schema de Extração Padrão](#3-schema-de-extração-padrão)
- [4. Fluxo de Confirmação Obrigatória](#4-fluxo-de-confirmação-obrigatória)
- [5. Deduplicação](#5-deduplicação)
- [6. Categorização com Aprendizado por Casal](#6-categorização-com-aprendizado-por-casal)
- [7. Casos de Baixa Confiança](#7-casos-de-baixa-confiança)

---

## 1. Visão Geral do Fluxo

```
Mensagem WhatsApp → Identificação do tipo de mídia → Pipeline específico
→ Extração estruturada (schema §3) → Deduplicação (§5) → Categorização (§6)
→ Resumo de confirmação ao utilizador (§4) → Gravação em `transactions` (Supabase)
```

Nenhuma etapa grava direto no banco sem passar pela confirmação — ver §4.

---

## 2. Roteamento por Tipo de Mídia

| Tipo recebido | Pipeline | Saída esperada antes da extração |
| :--- | :--- | :--- |
| **Áudio** (nota de voz) | Transcrição de fala → interpretação de linguagem natural do valor/categoria | Texto transcrito + nível de confiança da transcrição |
| **Imagem/Print** (comprovante PIX, print de app bancário, foto de recibo) | OCR + localização de campos-chave (valor, data, favorecido) | Texto extraído por região da imagem + confiança do OCR por campo |
| **Documento** (PDF de fatura de cartão, extrato bancário) | Parsing estruturado do documento (tabela ou texto), podendo gerar múltiplos lançamentos de uma vez | Lista de lançamentos candidatos, um por linha identificada |

Cada pipeline é tratado separadamente — nunca escreva um único parser "genérico" para as três modalidades, pois a origem do ruído (fala, imagem, texto de documento) é diferente e cada uma erra de forma diferente.

---

## 3. Schema de Extração Padrão

Todo lançamento, independentemente da origem, deve ser normalizado para este formato mínimo antes de seguir no fluxo:

```json
{
  "valor": "decimal, obrigatório",
  "tipo": "gasto | recebimento, obrigatório",
  "categoria": "string, obrigatório (pode vir como 'a_confirmar')",
  "data": "ISO 8601, obrigatório (usar data de envio da mensagem se não identificada)",
  "descricao": "string curta, obrigatório",
  "autor_id": "UUID do membro do casal que enviou a mensagem, obrigatório",
  "family_id": "UUID da família, obrigatório",
  "origem": "audio | imagem | documento, obrigatório",
  "confianca_extracao": "float 0-1, obrigatório",
  "compartilhado": "boolean — lançamento visível para os dois membros ou só para o autor"
}
```

Este é o mesmo formato que `scripts/extract_transaction.py` valida e devolve.

---

## 4. Fluxo de Confirmação Obrigatória
Antes de qualquer `INSERT` em `transactions`:
1. Monte um resumo curto e legível em linguagem natural do lançamento extraído.
2. Envie de volta pelo WhatsApp pedindo confirmação (ex.: reação com 👍 ou resposta "sim").
3. Só grave após confirmação explícita. Se o utilizador corrigir algum campo, use a correção — não a extração original.

Isso existe porque lançamento financeiro errado e silencioso é o principal motivo de abandono em apps financeiros: o utilizador perde confiança nos números assim que percebe um erro que ele não autorizou.

---

## 5. Deduplicação
- Gere um hash de deduplicação a partir de `valor + data + family_id + janela de 10 minutos`.
- Se um comprovante for enviado duas vezes (ex.: reencaminhado sem querer), o segundo envio deve ser sinalizado como possível duplicata antes da confirmação, não depois.
- Se o lançamento também aparecer via importação automática de extrato bancário (quando essa integração existir), o lançamento manual/WhatsApp deve ser o que perde no conflito — o extrato do banco é a fonte de verdade.

---

## 6. Categorização com Aprendizado por Casal
- Sugira uma categoria inicial com base em palavras-chave da descrição/OCR.
- Se o utilizador corrigir a categoria sugerida, registre a correção como preferência daquele `family_id` para casos semelhantes futuros.
- Nunca aplique uma categoria com confiança abaixo do limiar sem marcar como "a confirmar".

---

## 7. Casos de Baixa Confiança
Quando `confianca_extracao` < 0.7 (ou qualquer campo obrigatório não puder ser preenchido):
- Não grave nem pré-preencha um valor adivinhado.
- Devolva uma pergunta objetiva e específica sobre o campo ambíguo (nunca "não entendi", sempre "foi R$45 ou R$145?").
- Se a origem for um documento com múltiplos lançamentos candidatos, isole apenas os campos ambíguos — não descarte o documento inteiro por causa de uma linha problemática.
