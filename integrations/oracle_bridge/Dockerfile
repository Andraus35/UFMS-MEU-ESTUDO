FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /opt/ufms
COPY bridge ./bridge
RUN groupadd --system ufms && useradd --system --gid ufms --home /opt/ufms ufms && mkdir /data && chown ufms:ufms /data
USER ufms
CMD ["python", "-m", "bridge.gateway"]
