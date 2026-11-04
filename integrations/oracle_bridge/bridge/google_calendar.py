"""Google Agenda opcional: calendário isolado, OAuth offline e eventos idempotentes.

A conexão Google Calendar feita dentro do ChatGPT NÃO fornece tokens a este serviço.
O usuário deve conceder OAuth separadamente para esta aplicação Oracle.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import threading
from datetime import datetime, timedelta, timezone
from urllib import error, parse, request


class GoogleCalendar:
    TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
    API = "https://www.googleapis.com/calendar/v3"

    def __init__(self, client_id: str, client_secret: str, refresh_token: str,
                 calendar_id: str = ""):
        if not (client_id and client_secret and refresh_token):
            raise ValueError("Credenciais OAuth ausentes")
        self.client_id = client_id
        self._client_secret = client_secret
        self._refresh_token = refresh_token
        self.calendar_id = calendar_id
        self._access_token = ""
        self._expires_at = datetime.min.replace(tzinfo=timezone.utc)
        self._lock = threading.Lock()

    def _token(self) -> str:
        with self._lock:
            if self._access_token and datetime.now(timezone.utc) + timedelta(seconds=60) < self._expires_at:
                return self._access_token
            body = parse.urlencode({
                "client_id": self.client_id,
                "client_secret": self._client_secret,
                "refresh_token": self._refresh_token,
                "grant_type": "refresh_token",
            }).encode()
            req = request.Request(self.TOKEN_ENDPOINT, data=body, method="POST")
            with request.urlopen(req, timeout=15) as reply:
                payload = json.load(reply)
            self._access_token = payload["access_token"]
            self._expires_at = datetime.now(timezone.utc) + timedelta(
                seconds=int(payload.get("expires_in", 3600)))
            return self._access_token

    def _post(self, path: str, payload: dict):
        req = request.Request(self.API + path, data=json.dumps(payload).encode(),
                              headers={"Authorization": "Bearer " + self._token(),
                                       "Content-Type": "application/json"}, method="POST")
        with request.urlopen(req, timeout=20) as reply:
            return json.load(reply)

    def create_study_calendar(self) -> str:
        # Deve ser chamado explicitamente UMA VEZ, com OAuth no proprietário.
        result = self._post("/calendars", {
            "summary": "UFMS MEU ESTUDO",
            "timeZone": "America/Campo_Grande",
            "description": "Compromissos de estudo administrados por Tutor e Coach UFMS.",
        })
        return result["id"]

    def _get_event(self, event_id: str) -> dict:
        path = ("/calendars/" + parse.quote(self.calendar_id, safe="") +
                "/events/" + parse.quote(event_id, safe=""))
        req = request.Request(self.API + path, headers={
            "Authorization": "Bearer " + self._token()
        }, method="GET")
        with request.urlopen(req, timeout=20) as reply:
            return json.load(reply)

    @staticmethod
    def _matching_event(existing: dict, expected: dict) -> bool:
        """Trata equivalência de instantes, mesmo com offsets diferentes."""
        def utc_time(value: str):
            return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
        try:
            return (
                existing.get("id") == expected["id"] and
                existing.get("status", "confirmed") != "cancelled" and
                existing.get("summary") == expected["summary"] and
                utc_time(existing["start"]["dateTime"]) == utc_time(expected["start"]["dateTime"]) and
                utc_time(existing["end"]["dateTime"]) == utc_time(expected["end"]["dateTime"])
            )
        except (KeyError, TypeError, ValueError, AttributeError):
            return False

    def create_event(self, start: datetime, end: datetime, title: str, key: str) -> str:
        if not self.calendar_id or self.calendar_id == "primary":
            raise ValueError("ID explícito do calendário UFMS obrigatório")
        if any(x.tzinfo is None or x.utcoffset() is None for x in (start, end)):
            raise ValueError("Datas de eventos exigem fuso")
        if not start < end or end - start > timedelta(hours=12):
            raise ValueError("Intervalo de evento inválido")
        if not isinstance(title, str) or not 1 <= len(title.strip()) <= 160:
            raise ValueError("Título de evento inválido")
        if not isinstance(key, str) or not 1 <= len(key) <= 160:
            raise ValueError("Chave do evento inválida")
        # Google exige base32hex: 0-9 e a-v. Hex SHA256 puro contém w-z.
        digest = hashlib.sha256(("ufms:" + key).encode()).digest()
        event_id = base64.b32hexencode(digest).decode("ascii").lower().rstrip("=")[:32]
        payload = {
            "id": event_id,
            "summary": title.strip(),
            "start": {"dateTime": start.isoformat()},
            "end": {"dateTime": end.isoformat()},
            "reminders": {"useDefault": False, "overrides": [
                {"method": "popup", "minutes": 15}
            ]},
        }
        path = "/calendars/" + parse.quote(self.calendar_id, safe="") + "/events"
        try:
            result = self._post(path, payload)
            return result["id"]
        except error.HTTPError as exc:
            if exc.code == 409:
                # 409 sozinho não prova identidade: conferir evento efetivamente existente.
                existing = self._get_event(event_id)
                if self._matching_event(existing, payload):
                    return event_id
                raise RuntimeError("Conflito de evento sem equivalência de conteúdo") from None
            raise


def configured_calendar():
    env = os.environ
    required = ("UFMS_GOOGLE_CLIENT_ID", "UFMS_GOOGLE_CLIENT_SECRET",
                "UFMS_GOOGLE_REFRESH_TOKEN", "UFMS_GOOGLE_CALENDAR_ID")
    if not all(env.get(k) for k in required):
        return None
    return GoogleCalendar(env[required[0]], env[required[1]],
                          env[required[2]], env[required[3]])
