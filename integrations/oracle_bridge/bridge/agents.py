"""Respostas conversacionais Tutor/Coach, desativadas por padrão.

A API recebe apenas a mensagem atual e instruções do papel; não há recuperação
autorizada de histórico do GitHub ou do Google Agenda nesta versão. Sem ferramentas
externas no modelo: o texto gerado NUNCA executa operações de calendário/estado.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from urllib import error, request

UTC = timezone.utc

INSTRUCTIONS = {
    "tutor": (
        "Você é o Tutor UFMS para cargos 523 e 324 do edital 152/2026. "
        "Ajude a compreender, recuperar e aplicar conhecimentos por questões. "
        "Não invente trechos de edital, resultados do aluno, questões, links, "
        "notas, acesso TEC/Qconcursos, agenda ou estado persistido. "
        "Sem dados verificados, exponha incerteza e solicite o mínimo necessário. "
        "Recomende próxima intervenção de maneira flexível, sem cronograma imposto. "
        "Você NÃO tem ferramentas para alterar calendário, GitHub ou disparar alertas. "
        "Responda em português, diretamente, em até cerca de 150 palavras."
    ),
    "coach": (
        "Você é o Coach UFMS de acompanhamento de concursos, cargos 523 e 324. "
        "Ajude em autorregulação, obstáculos à execução, organização e decisões "
        "estratégicas, de modo não coercitivo. Não invente compromissos, "
        "desempenho, motivos de pausa, eventos de agenda ou histórico do aluno. "
        "Não diagnostique questões de saúde nem substitua o Tutor no conteúdo. "
        "Sem dados verificados, faça perguntas breves e explícitas. "
        "Não imponha calendário, metas rígidas ou notificações compulsórias. "
        "Você NÃO tem ferramentas para alterar calendário, GitHub ou disparar alertas. "
        "Responda em português, diretamente, em até cerca de 150 palavras."
    ),
}


class AgentBridge:
    """Isola os papéis e controla custo sem guardar conversas ou respostas."""

    def __init__(self, api_key: str, model: str, store, max_per_day: int = 30):
        if not api_key or not model:
            raise ValueError("API key e modelo são obrigatórios")
        if not 1 <= max_per_day <= 200:
            raise ValueError("Quota inválida")
        self._api_key = api_key
        self.provider = "openai"
        self.model = model
        self.store = store
        self.max_per_day = max_per_day
        with store.connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS llm_requests(
                request_key TEXT PRIMARY KEY,
                role TEXT NOT NULL,
                created_utc TEXT NOT NULL
            )""")

    def _reserve(self, role: str, key: str, now: datetime) -> str | None:
        stamp = now.astimezone(UTC).isoformat()
        start = now.astimezone(UTC).date().isoformat() + "T00:00:00+00:00"
        with self.store.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            consent = db.execute(
                "SELECT value FROM settings WHERE key='llm_consent'"
            ).fetchone()
            if consent is None or consent["value"] != "1":
                return "Conversa com IA desativada. Use /ativar_ia para autorizar."
            if self.provider == "gemini":
                permission = db.execute(
                    "SELECT value FROM settings WHERE key='gemini_data_consent'"
                ).fetchone()
                if permission is None or permission["value"] != "1":
                    return "Envio ao Google desativado; consulte /politica_gemini e use /ativar_gemini."
            # Armazenar apenas ID e data, nunca o texto nem a resposta.
            db.execute("DELETE FROM llm_requests WHERE created_utc<?",
                       ((now - timedelta(days=30)).astimezone(UTC).isoformat(),))
            if db.execute("SELECT 1 FROM llm_requests WHERE request_key=?", (key,)).fetchone():
                return "Essa mensagem já foi processada; envie uma nova mensagem para repetir."
            used = db.execute("SELECT COUNT(*) AS n FROM llm_requests WHERE created_utc>=?",
                              (start,)).fetchone()["n"]
            if used >= self.max_per_day:
                return "Limite diário de conversas com IA atingido; os lembretes continuam ativos."
            db.execute("INSERT INTO llm_requests(request_key,role,created_utc) VALUES(?,?,?)",
                       (key, role, stamp))
            return None

    def _request_response(self, payload: dict) -> dict:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = request.Request(
            "https://api.openai.com/v1/responses", data=body, method="POST",
            headers={"Content-Type": "application/json",
                     "Authorization": "Bearer " + self._api_key}
        )
        # Não expor exceção ou URL/headers em logs, especialmente com token.
        with request.urlopen(req, timeout=30) as response:
            return json.load(response)

    @staticmethod
    def extract_text(result: dict) -> str:
        if result.get("status") not in (None, "completed"):
            raise RuntimeError("A IA não confirmou conclusão")
        contents = []
        for item in result.get("output", []):
            if item.get("type") != "message":
                continue
            for block in item.get("content", []):
                if block.get("type") == "output_text":
                    contents.append(block.get("text", ""))
        text = "\n".join(contents).strip()
        if not text:
            raise RuntimeError("Resposta de IA vazia")
        return text[:3500]

    def answer(self, role: str, text: str, request_key: str,
               now: datetime | None = None) -> str:
        if role not in INSTRUCTIONS:
            raise PermissionError("Papel inválido")
        if not isinstance(text, str) or not 1 <= len(text.strip()) <= 2500:
            return "Envie uma mensagem de até 2.500 caracteres."
        if not isinstance(request_key, str) or not request_key.startswith(role + ":"):
            raise PermissionError("Chave de requisição inválida")
        quota = self._reserve(role, request_key, now or datetime.now(UTC))
        if quota is not None:
            return quota
        result = self._request_response(self._make_payload(role, text.strip()))
        return self.extract_text(result)

    def _make_payload(self, role: str, text: str) -> dict:
        return {
            "model": self.model,
            "instructions": INSTRUCTIONS[role],
            "input": [{"role": "user", "content": text}],
            "max_output_tokens": 600,
            "store": False,
        }


class GeminiAgentBridge(AgentBridge):
    """Somente modelo com documentação de Free Tier e texto simples."""

    FREE_MODEL_ALLOWLIST = frozenset({"gemini-3.5-flash-lite"})

    def __init__(self, api_key: str, model: str, store, max_per_day: int = 10):
        if model not in self.FREE_MODEL_ALLOWLIST:
            raise ValueError("Modelo Gemini não aprovado para teste gratuito")
        super().__init__(api_key, model, store, max_per_day=max_per_day)
        self.provider = "gemini"

    def _make_payload(self, role: str, text: str) -> dict:
        return {
            "systemInstruction": {"parts": [{"text": INSTRUCTIONS[role]}]},
            "contents": [{"role": "user", "parts": [{"text": text}]}],
            "generationConfig": {"maxOutputTokens": 512, "temperature": 0.4},
        }

    def _request_response(self, payload: dict) -> dict:
        req = request.Request(
            "https://generativelanguage.googleapis.com/v1beta/models/"
            + self.model + ":generateContent",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            method="POST",
            headers={"Content-Type": "application/json",
                     "x-goog-api-key": self._api_key},
        )
        try:
            with request.urlopen(req, timeout=20) as response:
                return json.load(response)
        except (error.HTTPError, error.URLError, TimeoutError, OSError,
                ValueError, KeyError, TypeError):
            raise RuntimeError("Gemini indisponível ou cota atingida; entrega não confirmada") from None

    @staticmethod
    def extract_text(result: dict) -> str:
        if not isinstance(result, dict) or not result.get("candidates"):
            raise RuntimeError("Gemini não retornou uma resposta confirmada")
        first = result["candidates"][0]
        if not isinstance(first, dict) or first.get("finishReason") not in (None, "STOP"):
            raise RuntimeError("Resposta Gemini interrompida ou bloqueada")
        parts = (first.get("content") or {}).get("parts") or []
        blocks = [item["text"] for item in parts
                  if isinstance(item, dict) and isinstance(item.get("text"), str)]
        message = "\n".join(blocks).strip()
        if not message:
            raise RuntimeError("Resposta Gemini vazia")
        return message[:3500]


def configured_agent(store):
    """Custo zero: nunca instancia a API OpenAI paga pela configuração."""
    if os.getenv("UFMS_LLM_ENABLED", "") != "1":
        return None
    if os.getenv("UFMS_LLM_PROVIDER", "") != "gemini":
        return None
    if (os.getenv("UFMS_GEMINI_FREE_PROJECT_ATTESTED", "") != "1"
            or os.getenv("UFMS_GEMINI_PRIVACY_REVIEWED", "") != "1"):
        return None
    key = os.getenv("UFMS_GEMINI_API_KEY", "")
    model = os.getenv("UFMS_GEMINI_MODEL", "")
    limit = os.getenv("UFMS_LLM_DAILY_LIMIT", "10")
    if not key or model not in GeminiAgentBridge.FREE_MODEL_ALLOWLIST:
        return None
    if not limit.isdecimal() or not 1 <= int(limit) <= 20:
        return None
    return GeminiAgentBridge(key, model, store, max_per_day=int(limit))
