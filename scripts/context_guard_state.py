"""Regras puras do estado do hook de passagem (claude_context_guard): quando a sessão deixa de estar "armada".

Problema (21/11/2026): `armed_at` e `sealed` ficavam permanentes. Depois de um falso alarme (janela de 200k em vez de 1M) o hook de perguntas
(`.claude/hooks/perguntas_boas_praticas.py`, que só lê `armed_at`) cedia para sempre, mesmo com a medição corrigida.

Regra: com uma medição REAL (a transcrição trouxe `usage`) abaixo do limite, a sessão é desarmada. O contexto só diminui por compactação,
limpeza, falso alarme ou mudança de configuração; nos quatro casos o aviso anterior deixou de valer. Sem medição, nada muda (na dúvida, não desarma).
Este módulo não lê nem grava arquivo: só transforma o dicionário de estado. Falha aberta e sem efeito externo.
"""
from __future__ import annotations

CAMPOS_DO_ARME = ("armed_at", "sealed", "sealed_at", "stop_blocks", "aviso_chave", "lote_pendente")


def desarmar_se_abaixo(st: dict, pct: float, threshold: float, tem_medida: bool) -> tuple[dict, bool]:
    """Devolve (estado, desarmou). Desarma só se estava armada, há medição real e a medição está abaixo do limite."""
    if not st.get("armed_at") or not tem_medida or pct >= threshold:
        return st, False
    novo = {k: v for k, v in st.items() if k not in CAMPOS_DO_ARME}
    novo["desarmes"] = int(st.get("desarmes", 0)) + 1
    return novo, True
