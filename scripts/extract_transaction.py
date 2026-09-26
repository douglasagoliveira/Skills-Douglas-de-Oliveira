#!/usr/bin/env python3
"""
Nome do Script: extract_transaction.py
Descrição: Valida e normaliza um lançamento financeiro extraído de uma mensagem
do WhatsApp (áudio, imagem/print ou documento) para o schema mínimo exigido
pelo App Vínculo, gera o hash de deduplicação e sinaliza se o lançamento
precisa de confirmação humana antes de ser gravado em `transactions`.

Uso CLI:
  python extract_transaction.py --tipo <audio|imagem|documento> --valor <VALOR>
      --descricao <TEXTO> [--categoria <CATEGORIA>] [--confianca <0-1>]
      [--tipo-lancamento <gasto|recebimento>] [--compartilhado]

Este script NUNCA grava no banco — apenas valida/normaliza e devolve o
veredito de "pronto para confirmação" ou "precisa de esclarecimento".
"""

import sys
import json
import hashlib
import argparse
from datetime import datetime, timezone

LIMIAR_CONFIANCA = 0.7
ORIGENS_VALIDAS = {"audio", "imagem", "documento"}
TIPOS_VALIDOS = {"gasto", "recebimento"}


def gerar_hash_dedup(valor: float, data_iso: str) -> str:
    """Hash de deduplicação: valor + data truncada à janela de 10 minutos."""
    dt = datetime.fromisoformat(data_iso)
    janela = dt.replace(minute=(dt.minute // 10) * 10, second=0, microsecond=0)
    chave = f"{valor:.2f}|{janela.isoformat()}"
    return hashlib.sha256(chave.encode("utf-8")).hexdigest()[:16]


def validar_lancamento(
    origem: str,
    valor: float,
    descricao: str,
    categoria: str = "a_confirmar",
    confianca: float = 1.0,
    tipo_lancamento: str = "gasto",
    compartilhado: bool = False,
) -> dict:
    """Valida e normaliza um lançamento extraído para o schema padrão."""
    if origem not in ORIGENS_VALIDAS:
        raise ValueError(f"Origem inválida: {origem}. Use: {ORIGENS_VALIDAS}")
    if tipo_lancamento not in TIPOS_VALIDOS:
        raise ValueError(f"Tipo inválido: {tipo_lancamento}. Use: {TIPOS_VALIDOS}")
    if valor <= 0:
        raise ValueError("Valor deve ser positivo.")

    data_iso = datetime.now(timezone.utc).isoformat()
    hash_dedup = gerar_hash_dedup(valor, data_iso)
    precisa_confirmacao_extra = confianca < LIMIAR_CONFIANCA

    lancamento = {
        "valor": round(valor, 2),
        "tipo": tipo_lancamento,
        "categoria": categoria if confianca >= LIMIAR_CONFIANCA else "a_confirmar",
        "data": data_iso,
        "descricao": descricao,
        "origem": origem,
        "confianca_extracao": confianca,
        "compartilhado": compartilhado,
        "hash_dedup": hash_dedup,
    }

    status = "aguardando_esclarecimento" if precisa_confirmacao_extra else "pronto_para_confirmacao"

    return {
        "status": status,
        "lancamento": lancamento,
        "requer_pergunta_ao_utilizador": precisa_confirmacao_extra,
        "mensagem_sugerida": (
            f"Recebi um {origem} com valor R${valor:.2f}, mas a confiança da "
            f"extração ficou em {confianca:.0%}. Pode confirmar se está certo?"
            if precisa_confirmacao_extra
            else f"Confirma o lançamento de R${valor:.2f} ({tipo_lancamento}, "
                 f"categoria: {categoria})?"
        ),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Validador/normalizador de lançamentos vindos do WhatsApp — Vínculo"
    )
    parser.add_argument("--tipo", required=True, choices=sorted(ORIGENS_VALIDAS))
    parser.add_argument("--valor", required=True, type=float)
    parser.add_argument("--descricao", required=True)
    parser.add_argument("--categoria", required=False, default="a_confirmar")
    parser.add_argument("--confianca", required=False, type=float, default=1.0)
    parser.add_argument(
        "--tipo-lancamento", required=False, default="gasto", choices=sorted(TIPOS_VALIDOS)
    )
    parser.add_argument("--compartilhado", action="store_true")

    args = parser.parse_args()

    try:
        resultado = validar_lancamento(
            origem=args.tipo,
            valor=args.valor,
            descricao=args.descricao,
            categoria=args.categoria,
            confianca=args.confianca,
            tipo_lancamento=args.tipo_lancamento,
            compartilhado=args.compartilhado,
        )
        print(json.dumps(resultado, ensure_ascii=False, indent=2))
        sys.exit(0)
    except Exception as e:
        sys.stderr.write(f"[ERRO_DE_EXTRACAO] {str(e)}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
