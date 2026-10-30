FROM python:3.12-slim

ARG APP_VERSION=3.0.0
ENV APP_VERSION=${APP_VERSION} LOG_DIR=/var/log/lab3 PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /srv/app

COPY app/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt \
    && useradd --create-home --uid 10001 appuser \
    && mkdir -p /var/log/lab3 \
    && chown appuser:appuser /var/log/lab3
COPY app/ ./

USER appuser
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "4", "app:app"]
