"""Arquive os bytes obtidos DIRETAMENTE da URL institucional em pasta externa.

Não promove o edital remoto a versão normativa, não modifica o repositório,
não faz merge e não registra automaticamente retificações.
  python scripts/archive_pdf_ufms.py --live --out-dir /tmp/ufms-evidencias
  python scripts/archive_pdf_ufms.py --verify /tmp/ufms-evidencias/ufms152-2026-HASH.json
"""
import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, build_opener

from probe_pdf_ufms import ROOT, URL, BlockExternalRedirect, probe

HEX64 = re.compile(r"^[0-9a-f]{64}$")
NAME = re.compile(r"^ufms152-2026-([0-9a-f]{64})\.pdf$")


class CaptureReader:
    def __init__(self, original, sink):
        self.original = original
        self.sink = sink
        self.status = original.status
        self.headers = original.headers

    def read(self, size):
        piece = self.original.read(size)
        if isinstance(piece, bytes):
            self.sink.write(piece)
        return piece


def evidence_dir(out_dir):
    target = Path(out_dir).expanduser()
    if not target.is_absolute() or target.is_symlink() or not target.is_dir():
        raise ValueError("Diretório de evidências deve ser absoluto, existente e não ser symlink")
    target = target.resolve()
    if target.is_relative_to(ROOT.resolve()):
        raise ValueError("Não armazenar PDF externo na árvore do repositório")
    return target


def verify_archive(receipt_path):
    receipt = Path(receipt_path)
    if receipt.is_symlink() or not receipt.is_file():
        raise ValueError("Recibo de evidência inválido ou symlink")
    d = json.loads(receipt.read_text(encoding="utf-8"))
    name = d.get("archived_pdf_filename")
    if not isinstance(name, str) or not NAME.fullmatch(name):
        raise ValueError("Nome do PDF arquivado inválido")
    if receipt.name != name[:-4] + ".json":
        raise ValueError("Nome do recibo não corresponde ao PDF")
    sha = NAME.fullmatch(name).group(1)
    if d.get("sha256_remote_bytes") != sha or not HEX64.fullmatch(str(d.get("sha256_expected", ""))):
        raise ValueError("Recibo não corresponde à identidade dos bytes")
    if d.get("source_document_url") != URL or d.get("normative_revision_verified") is not False:
        raise ValueError("Proveniência ou status normativo inválido")
    if d.get("acquisition") == "direct_https":
        original_sha = json.loads((ROOT/"edital/manifest.json").read_text(encoding="utf-8"))["source_pdf_sha256"]
        if d["sha256_expected"] != original_sha:
            raise ValueError("SHA-256 de referência diverge do manifesto canônico")
    pdf = receipt.parent / name
    if pdf.is_symlink() or not pdf.is_file():
        raise ValueError("Bytes arquivados ausentes ou symlink")
    length = 0
    digest = hashlib.sha256()
    first = b""
    tail = b""
    with pdf.open("rb") as stream:
        while True:
            part = stream.read(65536)
            if not part:
                break
            if not first:
                first = part[:8]
            length += len(part)
            digest.update(part)
            tail = (tail + part)[-2048:]
    if (digest.hexdigest() != sha or length != d.get("bytes_read") or
        not first.startswith(b"%PDF-") or b"%%EOF" not in tail):
        raise ValueError("Arquivo de evidência adulterado ou truncado")
    expected_status = "digest_match" if sha == d["sha256_expected"] else "digest_mismatch"
    if (d.get("comparison_status") != expected_status or
        d.get("acquisition") not in ("offline_fixture", "direct_https") or
        d.get("archived_pdf_bytes") is not True or
        d.get("archived_official_pdf") is not (d["acquisition"] == "direct_https")):
        raise ValueError("Recibo de comparação inconsistente")
    return d


def archive_response(response, expected_sha, out_dir, acquisition="offline_fixture"):
    """Copia bytes do stream já aberto e devolve recibo com readback independente.

    acquisition='direct_https' só deve ser escolhido pelo entrypoint live, embora
    o recibo local continue NÃO sendo uma atestação criptográfica de procedência.
    """
    folder = evidence_dir(out_dir)
    if acquisition not in ("offline_fixture", "direct_https"):
        raise ValueError("Modo de aquisição desconhecido")
    tmp = None
    receipt_tmp = None
    created_pdf = None
    created_receipt = None
    try:
        with tempfile.NamedTemporaryFile(dir=folder, prefix=".ufms-pdf-", suffix=".partial",
                                         delete=False) as stream:
            tmp = Path(stream.name)
            info = probe(CaptureReader(response, stream), expected_sha)
            stream.flush()
            os.fsync(stream.fileno())
        sha = info["sha256_observed"]
        filename = "ufms152-2026-" + sha + ".pdf"
        pdf_final = folder / filename
        receipt_final = folder / (filename[:-4] + ".json")
        record = {
            "schema_version": "1.0",
            "source_document_url": URL,
            "acquisition": acquisition,
            "observed_at_utc": datetime.now(timezone.utc).isoformat(),
            "sha256_expected": info["sha256_expected"],
            "sha256_remote_bytes": sha,
            "bytes_read": info["bytes_read"],
            "comparison_status": "digest_match" if info["status"] == "digest_match_unarchived"
                                 else "digest_mismatch",
            "archived_pdf_filename": filename,
            "archived_pdf_bytes": True,
            "archived_official_pdf": acquisition == "direct_https",
            "normative_revision_verified": False,
            "provenance_limit": "Recibo local e hash reproduzível; não é atestação independente de TLS/origem.",
        }
        # Criação por hard link é atômica e não sobrescreve arquivos anteriores.
        os.link(tmp, pdf_final)
        created_pdf = pdf_final
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=folder,
                                         prefix=".ufms-receipt-", suffix=".partial",
                                         delete=False) as stream:
            receipt_tmp = Path(stream.name)
            json.dump(record, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.link(receipt_tmp, receipt_final)
        created_receipt = receipt_final
        verified = verify_archive(receipt_final)
        return {"status": "archived_"+verified["comparison_status"],
                "receipt_path": str(receipt_final), "pdf_path": str(pdf_final),
                "sha256": sha, "bytes_read": info["bytes_read"],
                "normative_revision_verified": False}
    except Exception:
        # Rollback apenas de arquivos que esta chamada criou, nunca de artefatos
        # de terceiros já existentes no diretório de evidências.
        if created_receipt is not None:
            created_receipt.unlink(missing_ok=True)
        if created_pdf is not None:
            created_pdf.unlink(missing_ok=True)
        raise
    finally:
        for temp in (tmp, receipt_tmp):
            if temp is not None:
                temp.unlink(missing_ok=True)


def live(out_dir, timeout=15, opener=None):
    expected = json.loads((ROOT/"edital/manifest.json").read_text(encoding="utf-8"))["source_pdf_sha256"]
    if not isinstance(expected, str) or not HEX64.fullmatch(expected):
        raise ValueError("SHA-256 de referência inválido")
    opener = opener or build_opener(BlockExternalRedirect())
    request = Request(URL, headers={"User-Agent": "UFMS-MEU-ESTUDO-documental/1.0"})
    with opener.open(request, timeout=timeout) as response:
        if response.geturl() != URL:
            raise ValueError("Redirecionamento ou URL divergente")
        return archive_response(response, expected, out_dir, "direct_https")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--live", action="store_true")
    mode.add_argument("--verify", type=Path)
    parser.add_argument("--out-dir", type=Path)
    args = parser.parse_args()
    if args.live and args.out_dir is None:
        parser.error("--live exige --out-dir")
    try:
        if args.live:
            result = live(args.out_dir)
            rc = 0 if result["status"] == "archived_digest_match" else 2
        else:
            result = {"status": "archive_integrity_valid", **verify_archive(args.verify)}
            rc = 0
    except (OSError, ValueError, KeyError, TypeError, HTTPError, URLError, json.JSONDecodeError) as exc:
        result = {"status": "unverifiable", "error_type": type(exc).__name__,
                  "reason": str(exc)[:200], "normative_revision_verified": False}
        rc = 3
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return rc


if __name__ == "__main__":
    sys.exit(main())
