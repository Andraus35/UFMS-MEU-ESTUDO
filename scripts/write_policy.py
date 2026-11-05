"""Gate fail-closed de resultados individuais para o harness UFMS.

Fase atual: a habilitação de dados pessoais NÃO pode ocorrer apenas pela troca
de uma flag no settings.json. Este gate protege validação e reconstrução locais.
Uma liberação futura requer aprovação humana, verificação autenticada do
repositório e revisão independente deste controle. Não consulta rede.
"""
import argparse
import csv
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
    # Bloqueio adicional dos arquivos derivados, inclusive em commits que
    # tentem inserir contagens sem um evento resultado_recebido.
    current_path = root / "state/CURRENT.json"
    if current_path.is_file():
        current = load_json(current_path)
        if not isinstance(current, dict):
            raise ValueError("Estado derivado inválido; escrita pessoal bloqueada")
        if (type(current.get("results_count")) is not int
                or current["results_count"] != 0
                or current.get("last_result_caderno_id") is not None):
            raise ValueError("Estado derivado contém resultado pessoal proibido")
    progress_path = root / "state/PROGRESS.csv"
    if progress_path.is_file():
        with progress_path.open(encoding="utf-8", newline="") as stream:
            reader = csv.DictReader(stream)
            required = {"topic_id", "attempted", "correct", "accuracy", "revision_due_at"}
            if reader.fieldnames is None or not required.issubset(reader.fieldnames):
                raise ValueError("Projeção de progresso inválida; escrita bloqueada")
            for row in reader:
                if (row.get("attempted") != "0" or row.get("correct") != "0"
                        or row.get("accuracy") not in ("", None)
                        or row.get("revision_due_at") not in ("", None)):
                    raise ValueError("Progresso individual não pode ir para repositório público")
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
