FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /opt/ufms
COPY bridge ./bridge
# age e age-keygen são necessários para backup/restauração dentro da imagem.
RUN apt-get update && apt-get install -y --no-install-recommends age ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system ufms \
    && useradd --system --gid ufms --home /opt/ufms ufms \
    && mkdir /data \
    && chown ufms:ufms /data \
    && chmod 0700 /data
USER ufms
CMD ["python", "-m", "bridge.gateway"]
