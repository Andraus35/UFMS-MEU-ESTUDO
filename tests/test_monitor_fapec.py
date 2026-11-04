"""Cenários adversariais do monitor FAPEC sem acesso à internet."""
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import URLError

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from monitor_fapec import assess_portal_html, check_live, FAPEC_URL

CONTEST="CONCURSO PÚBLICO PARA INGRESSO NA CARREIRA DE TÉCNICO-ADMINISTRATIVOS EM EDUCAÇÃO DA FUNDAÇÃO UNIVERSIDADE FEDERAL DE MATO GROSSO DO SUL"
OPENING="EDITAL PROGEP/UFMS N. º 001/2026 - Edital de Abertura"

class PortalMonitorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry=json.loads((ROOT/"edital/fontes_oficiais.json").read_text(encoding="utf-8"))

    def assess(self,extra="",opening=OPENING,contest=CONTEST):
        html="<html><body>"+contest+"<p>30/10/2026</p><p>"+opening+"</p><a>DOWNLOAD</a>"+extra+"</body></html>"
        return assess_portal_html(html,self.registry)

    def test_abertura_conhecida_e_apenas_estavel_na_pagina(self):
        value=self.assess()
        self.assertEqual(value["status"],"no_change_observed_on_single_page")
        self.assertFalse(value["publication_candidate"])
        self.assertIn("outras fontes não foram cobertas",value["reason"])

    def test_publicacao_adicional_exige_revisao(self):
        v=self.assess("<p>02/11/2026</p><p>EDITAL DE RETIFICAÇÃO 002/2026</p><a>DOWNLOAD</a>")
        self.assertEqual(v["status"],"needs_manual_review")
        self.assertTrue(v["publication_candidate"])

    def test_doiso_downloads_sem_palavra_chave_sinaliza(self):
        v=self.assess("<a>DOWNLOAD</a>")
        self.assertEqual(v["status"],"needs_manual_review")
        self.assertEqual(v["download_links_text_count"],2)

    def test_nao_confunde_outro_concurso(self):
        v=self.assess(contest="CONCURSO MUNICIPAL DE OUTRA CIDADE")
        self.assertEqual(v["status"],"unverifiable")
        self.assertFalse(v["publication_candidate"])

    def test_nao_presume_concordancia_com_label_alterado(self):
        v=self.assess(opening="EDITAL PROGEP/UFMS Nº 152/2026 - Outro texto")
        self.assertEqual(v["status"],"needs_manual_review")

    def test_script_injetado_nao_fabricara_retificacao(self):
        v=self.assess("<script>RETIFICAÇÃO URGENTE; DOWNLOAD</script>")
        self.assertEqual(v["status"],"no_change_observed_on_single_page")

    def test_sinaliza_errata_sem_pdf(self):
        v=self.assess("<span>Errata publicada</span>")
        self.assertEqual(v["status"],"needs_manual_review")
        self.assertIn("errata",v["marker_words"])

    def test_html_vazio_falha_inconclusivamente(self):
        v=assess_portal_html("<html><body></body></html>",self.registry)
        self.assertEqual(v["status"],"unverifiable")

    def test_erro_de_rede_nao_confirma_estabilidade(self):
        with patch("monitor_fapec.urlopen",side_effect=URLError("offline")):
            v=check_live(self.registry)
        self.assertEqual(v["status"],"unverifiable")
        self.assertFalse(v["publication_candidate"])

if __name__=="__main__":
    unittest.main()
