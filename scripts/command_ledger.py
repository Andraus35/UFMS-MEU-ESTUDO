"""Registro DURÁVEL e atômico de nonce e idempotência dos comandos (S4-R3), em SQLite da biblioteca padrão.

Contrato igual ao de `agent_commands.CommandLedger.admit`: decide e registra numa só transação
(`BEGIN IMMEDIATE`), então duas execuções simultâneas do mesmo nonce não passam as duas. Sem rede.
Grava um arquivo local escolhido pelo chamador; nada de segredo é armazenado (só nonce, chave de
idempotência e hash do corpo). Limites: não faz expiração automática (use `prune`), não substitui o
controle de acesso ao arquivo e não prova que a Zapia use este registro.
"""
import sqlite3
from datetime import datetime, timezone

SCHEMA = """
CREATE TABLE IF NOT EXISTS nonces (nonce TEXT PRIMARY KEY, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS idempotency (key TEXT PRIMARY KEY, body_hash TEXT NOT NULL, created_at TEXT NOT NULL);
"""


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class SqliteLedger:
    def __init__(self, path, *, timeout=10.0):
        self.path = str(path)
        self.timeout = timeout
        with self._connect() as conn:
            conn.executescript(SCHEMA)

    def _connect(self):
        conn = sqlite3.connect(self.path, timeout=self.timeout, isolation_level=None)
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def admit(self, nonce: str, key: str, body_hash: str) -> str:
        """Devolve "ok", "duplicate", "nonce_repeated" ou "conflict"; só registra quando admite."""
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            try:
                if conn.execute("SELECT 1 FROM nonces WHERE nonce = ?", (nonce,)).fetchone():
                    verdict = "nonce_repeated"
                else:
                    row = conn.execute("SELECT body_hash FROM idempotency WHERE key = ?", (key,)).fetchone()
                    stamp = _now()
                    if row is None:
                        conn.execute("INSERT INTO nonces VALUES (?, ?)", (nonce, stamp))
                        conn.execute("INSERT INTO idempotency VALUES (?, ?, ?)", (key, body_hash, stamp))
                        verdict = "ok"
                    elif row[0] != body_hash:
                        verdict = "conflict"
                    else:
                        conn.execute("INSERT INTO nonces VALUES (?, ?)", (nonce, stamp))
                        verdict = "duplicate"
                conn.execute("COMMIT")
            except BaseException:
                conn.execute("ROLLBACK")
                raise
            return verdict
        finally:
            conn.close()

    def prune(self, *, nonces_before: str, keys_before: str) -> None:
        """Apaga registros anteriores aos instantes ISO informados (nonce deve durar mais que a janela de tempo)."""
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            conn.execute("DELETE FROM nonces WHERE created_at < ?", (nonces_before,))
            conn.execute("DELETE FROM idempotency WHERE created_at < ?", (keys_before,))
            conn.execute("COMMIT")
        finally:
            conn.close()
