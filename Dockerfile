FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
RUN python -m pip install --no-cache-dir '.[mcp]' && \
    groupadd --gid 10001 ats && \
    useradd --uid 10001 --gid 10001 --home-dir /nonexistent --shell /usr/sbin/nologin ats
USER 10001:10001
ENV ATS_HOST=0.0.0.0 ATS_DEPLOYMENT_MODE=production
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3).read()" || exit 1
CMD ["ats-auditor-mcp"]
