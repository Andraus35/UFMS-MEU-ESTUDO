"""Produtor determinístico de check-ins genéricos, opt-in e sem dados pessoais.

Não consulta histórico do aluno e não presume desempenho. Horários locais
configurados (18h Tutor, 19h Coach). Requer DUAS autorizações:
- habilitar UFMS_GENERIC_CHECKINS=1 na Oracle; e
- /ativar_alertas enviado pelo próprio estudante no Telegram.
"""
from __future__ import annotations

from datetime import datetime, timezone
from .proactive import LOCAL

UTC = timezone.utc
SLOTS = (
    ("tutor", 18, "checkin",
     "Tutor UFMS: deseja trabalhar uma dúvida ou fazer uma recuperação curta? "
     "Se enviar o assunto ou resultado, posso orientar a próxima atividade."),
    ("coach", 19, "checkin",
     "Coach UFMS: como foi a viabilidade do seu estudo hoje? "
     "Se quiser, podemos ajustar prioridades sem impor uma rotina rígida."),
)


def generate_generic_checkins(outbox, *, enabled: bool = False,
                              now: datetime | None = None) -> int:
    if not enabled or not outbox.enabled() or outbox.store.paused():
        return 0
    now = now or datetime.now(UTC)
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("Data precisa de fuso")
    local = now.astimezone(LOCAL)
    # Sem catch-up: não criar eventos de check-in atrasados após reinício.
    if local.minute >= 10:
        return 0
    count = 0
    for bot, hour, category, body in SLOTS:
        if local.hour != hour:
            continue
        key = f"generic:{bot}:{local.date().strftime('%Y%m%d')}"
        try:
            outbox.enqueue(
                bot=bot,
                user_id=outbox.allowed_user_id,
                category=category,
                due=now,
                body=body,
                reason="Check-in genérico voluntário; sem evidência individual",
                source_ref="scheduler:generic-v1",
                request_key=key,
                now=now,
            )
            count += 1
        except ValueError:
            # Chave incompatível ou dados inválidos: não substituir existente.
            continue
        except PermissionError:
            # Revogação pode ocorrer enquanto o scheduler está rodando.
            return count
    return count
