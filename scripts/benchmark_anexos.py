"""Diagnóstico determinístico de distinção entre Anexos III, IV e V."""
import json
from search_edital import ROOT, search

def run(root=ROOT):
    source=json.loads((root/"edital/manifest.json").read_text(encoding="utf-8"))
    cases=json.loads((root/"tests/fixtures/annex_cases.json").read_text(encoding="utf-8"))["cases"]
    correct=0
    positive=0
    conflicts=0
    failures=[]
    for case in cases:
        query=case["query"]
        if case["kind"]=="conflict":
            conflicts+=1
            try:
                search(query,root=root)
            except ValueError as exc:
                if "mistura" in str(exc):
                    correct+=1
                else:
                    failures.append({"query":query,"reason":"wrong_exception","detail":str(exc)})
            else:
                failures.append({"query":query,"reason":"missing_conflict_rejection"})
            continue
        positive+=1
        try:
            results=search(query,root=root)
            if len(results)!=1:
                raise AssertionError("Quantidade diferente de um")
            result=results[0]
            if result.get("cargo")!=case["cargo"] or result.get("annex")!=case["annex"]:
                raise AssertionError("Cargo/anexo errado")
            if result.get("source_sha")!=source["source_git_blob_sha"]:
                raise AssertionError("Fonte divergente")
            if case["annex"]=="V" and result.get("area")!=case["area"]:
                raise AssertionError("Escopo do programa divergente")
            correct+=1
        except (AssertionError,ValueError,IndexError,KeyError) as exc:
            failures.append({"query":query,"reason":str(exc)})
    return {"kind":"annex_intent_diagnostic_not_universal_recall",
            "cases":len(cases),"positives":positive,"conflicts":conflicts,
            "correct":correct,"accuracy":f"{correct}/{len(cases)}",
            "failures":failures}

if __name__=="__main__":
    result=run()
    print(json.dumps(result,ensure_ascii=False,indent=2))
    if result["failures"]:raise SystemExit(1)
