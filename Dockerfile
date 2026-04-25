FROM python:3.12-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.12-slim AS runtime
RUN groupadd -r app && useradd -r -g app -d /home/app -s /bin/bash app \
    && mkdir -p /home/app && chown -R app:app /home/app
WORKDIR /home/app
COPY --from=builder /root/.local /home/app/.local
COPY --chown=app:app app/ ./app/
ENV PATH=/home/app/.local/bin:$PATH PYTHONUNBUFFERED=1
USER app
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --retries=3 CMD python -c "import httpx; httpx.get('http://localhost:8000/health').raise_for_status()"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]