#!/usr/bin/env python3
"""
Nome do Script: utility.py
Descrição: Utilitário para cálculo determinístico de pontos de carga mental (Mental Load Score) no App Vínculo.
Uso CLI: python utility.py --input <TIPO_DE_TAREFA> [--option <COMPLEXIDADE>]
"""

import sys
import json
import argparse

def calcular_pontos(tarefa: str, complexidade: str = "baixa") -> dict:
    """Calcula pontos baseados na carga mental da tarefa financeira."""
    tabela_base = {
        "registro_despesa": 10,
        "pagamento_conta": 20,
        "reuniao_casal": 30,
        "planejamento_mensal": 50
    }
    
    multiplicador = {"baixa": 1, "media": 1.5, "alta": 2.0}
    
    try:
        pontos_base = tabela_base.get(tarefa.lower(), 5)
        fator = multiplicador.get(complexidade.lower(), 1)
        pontos_finais = int(pontos_base * fator)
        
        return {
            "status": "sucesso",
            "dados_processados": {
                "tarefa": tarefa,
                "pontos_gerados": pontos_finais,
                "feedback": f"Esforço recompensado! +{pontos_finais} pts para a meta familiar."
            },
            "configuracao_aplicada": complexidade
        }
    except Exception as e:
        raise RuntimeError(f"Falha no cálculo de carga mental: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="Calculadora de Carga Mental - Vínculo")
    parser.add_argument("--input", required=True, help="Tipo de tarefa (ex: registro_despesa)")
    parser.add_argument("--option", required=False, default="baixa", help="baixa, media ou alta")
    
    args = parser.parse_args()

    try:
        dados_saida = calcular_pontos(args.input, args.option)
        print(json.dumps(dados_saida, ensure_ascii=False, indent=2))
        sys.exit(0)
    except Exception as e:
        sys.stderr.write(f"[ERRO_DE_EXECUCAO] {str(e)}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
