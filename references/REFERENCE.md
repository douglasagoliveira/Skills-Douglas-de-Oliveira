# Documentação de Referência: App Vínculo (Arquitetura e Gamificação)

## Sumário
- [1. Visão Geral do Domínio](#1-visão-geral-do-domínio)
- [2. Esquemas e Dicionário de Dados](#2-esquemas-e-dicionário-de-dados)
- [3. Regras de Gamificação e Carga Mental](#3-regras-de-gamificação-e-carga-mental)
- [4. Exemplos de Nudges Comportamentais](#4-exemplos-de-nudges-comportamentais)

> Para o pipeline de captura de lançamentos via WhatsApp (áudio, imagem, documento), ver `references/whatsapp-ingestion.md`.

---

## 1. Visão Geral do Domínio
Plataforma B2C focada em famílias. Transforma a gestão financeira de um peso para uma atividade colaborativa e gamificada usando React Native Expo e Supabase.

---

## 2. Esquemas e Dicionário de Dados
### Entidade Base: `transactions`

| Campo | Tipo de Dado | Obrigatório | Descrição e Restrições |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | Sim | Chave primária. |
| `family_id` | `UUID` | Sim | RLS usa este campo para isolamento de dados: `auth.uid()` deve pertencer a esta família. |
| `amount` | `Decimal` | Sim | Valor da transação. |
| `origem` | `Enum` | Sim | `manual` \| `audio` \| `imagem` \| `documento`. Ver `references/whatsapp-ingestion.md` para o pipeline das três últimas. |
| `hash_dedup` | `String` | Não | Preenchido apenas quando `origem` != `manual`. Usado para detectar reenvios duplicados de comprovantes. |
| `autor_id` | `UUID` | Sim | Membro do casal que originou o lançamento. RLS também restringe por este campo quando `compartilhado = false`. |

---

## 3. Regras de Gamificação e Carga Mental
1. **Pontuação Dinâmica:** O esforço mental dita a pontuação, gerida pelo script `utility.py`.
2. **Recompensas Coletivas:** Os pontos vão para um pote familiar, nunca individual.

---

## 4. Exemplos de Nudges Comportamentais
*   **Fazer:** "Vocês estão quase a atingir o limite. Que tal um desafio de cozinhar em casa hoje?"
