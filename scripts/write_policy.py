"""Gate fail-closed de resultados individuais para o harness UFMS.

Fase atual: a habilitação de dados pessoais NÃO pode ocorrer apenas pela troca
de uma flag no settings.json. Este gate protege validação e reconstrução locais.
Uma liberação futura requer aprovação humana, verificação autenticada do
repositório e revisão independente deste controle. Não consulta rede.
"""
import argparse
from pathlib import Path

try:
    from core import ROOT, event_rows, load_json
except ModuleNotFoundError:
    from scripts.core import ROOT, event_rows, load_json

PERSONAL_RESULT_TYPES = frozenset({"resultado_recebido", "resultado_corrigido"})


def verify_write_policy(root=ROOT):
    root = Path(root)
    cfg = load_json(root / "settings.json")
    storage = cfg.get("storage")
    if not isinstance(storage, dict):
        raise ValueError("Política de armazenamento ausente ou inválida")
    if storage.get("repository_must_be_private_for_personal_results") is not True:
        raise ValueError("Obrigatoriedade de repositório privado não pode ser removida")
    if storage.get("personal_results_writes_enabled") is not False:
        raise ValueError(
            "Gravação de resultados individuais permanece bloqueada; "
            "configuração local não é prova de privacidade ou autorização"
        )
    for event in event_rows(root):
        if event.get("type") in PERSONAL_RESULT_TYPES:
            raise ValueError(
                "Resultado individual encontrado sem habilitação homologada: "
                + str(event.get("event_id", "<sem-id>"))
            )
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", required=True)
    args = parser.parse_args()
    if args.check:
        verify_write_policy()
        print("OK: bloqueio de resultados individuais ativo; nenhuma escrita realizada")


if __name__ == "__main__":
    main()
