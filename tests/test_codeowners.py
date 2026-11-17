"""Contrato do CODEOWNERS: cobre os arquivos de contrato e NÃO vira exigência de revisão para o resto do repositório."""
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import private_persistence_guard as guard  # noqa: E402

ARQUIVO = ROOT / ".github" / "CODEOWNERS"
DONO = "@" + guard.PUBLIC_REPOSITORY.split("/")[0]  # o proprietário do repositório
PROTEGIDOS = (
    "AGENTS.md", "PRODUCT.md", "settings.json",
    "agents/TUTOR.md", "agents/COACH.md", "agents/ZAPIA.md", "agents/README.md",
    "scripts/tool_gateway.py", "tests/test_tool_gateway.py",
    ".github/CODEOWNERS", ".github/copilot-instructions.md", ".github/workflows/validate.yml",
    ".github/workflows/monitor-fapec.yml",
    ".claude/settings.json", ".claude/hooks/perguntas_boas_praticas.py",
)
LIVRES = (  # o dia a dia de uma tarefa não pode depender de revisão por dono
    "ROADMAP.md", "memory/HANDOFF.md", "state/WORKFLOW.json", "state/CURRENT.json", "scripts/command_box.py",
    "scripts/promotion_runner.py", "tests/test_command_box.py", "docs/especificacoes/S6_EXECUCAO_CANAL.md", "config/modelos_fluxo/promover.yml",
    "config/agent_command_schema.json", "README.md",
)


def regras(texto):
    saida = []
    for linha in texto.splitlines():
        linha = linha.strip()
        if linha and not linha.startswith("#"):
            saida.append(linha.split())
    return saida


def donos_de(caminho, lista):
    """Semântica de CODEOWNERS para os padrões usados aqui: `/arquivo` exato e `/pasta/` por prefixo; o último que casa vence."""
    achado = None
    for padrao, *donos in lista:
        raiz = padrao.lstrip("/")
        if (padrao.endswith("/") and caminho.startswith(raiz)) or (not padrao.endswith("/") and caminho == raiz):
            achado = donos
    return achado


def tem_dono_universal(lista):
    return any(r[0] in ("*", "/*", "**", "/**") or r[0].lstrip("/") in ("", "./") for r in lista)


class CodeownersTest(unittest.TestCase):
    def setUp(self):
        self.texto = ARQUIVO.read_text(encoding="utf-8")
        self.regras = regras(self.texto)

    def test_cobre_todos_os_arquivos_de_contrato_com_o_proprietario(self):
        for caminho in PROTEGIDOS:
            self.assertEqual(donos_de(caminho, self.regras), [DONO], caminho)

    def test_nao_cobre_o_dia_a_dia_nem_cria_dono_universal(self):
        for caminho in LIVRES:
            self.assertIsNone(donos_de(caminho, self.regras), caminho)
        self.assertFalse(tem_dono_universal(self.regras))

    def test_cada_regra_tem_um_padrao_e_so_o_dono_e_aponta_para_caminho_que_existe(self):
        self.assertGreaterEqual(len(self.regras), 8)
        for padrao, *donos in self.regras:
            self.assertEqual(donos, [DONO], padrao)
            self.assertTrue(padrao.startswith("/"), padrao)  # ancorado na raiz
            self.assertIsNone(re.search(r"[*?\[\]!]", padrao), padrao)  # sem curinga: nada casa por acidente
            self.assertTrue((ROOT / padrao.lstrip("/")).exists(), padrao)

    def test_sem_outro_dono_nem_equipe(self):
        self.assertEqual(set(re.findall(r"@[\w./-]+", self.texto)), {DONO})

    def test_explica_que_a_exigencia_e_ato_do_proprietario(self):
        self.assertIn("Require review from Code Owners", self.texto)
        self.assertIn("ato dele", self.texto)

    def test_o_teste_detecta_regra_removida_ou_curinga_universal(self):
        sem_agents = regras("\n".join(l for l in self.texto.splitlines() if not l.startswith("/agents/")))
        self.assertIsNone(donos_de("agents/TUTOR.md", sem_agents))
        for universal in ("*", "/*", "**", "/**", "/"):
            self.assertTrue(tem_dono_universal(regras(self.texto + f"\n{universal} @Andraus35\n")), universal)
        self.assertFalse(tem_dono_universal(self.regras))
        outro_dono = regras(self.texto.replace("/AGENTS.md                      @Andraus35", "/AGENTS.md @outro"))
        self.assertNotEqual(donos_de("AGENTS.md", outro_dono), [DONO])


if __name__ == "__main__":
    unittest.main()
