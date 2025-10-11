# 🥒➡📄 cuke2conf — Publish Cucumber Reports to Confluence

[![Build](https://github.com/sjacobs/cuke2conf/actions/workflows/build.yml/badge.svg)](https://github.com/sjacobs/cuke2conf/actions/workflows/build.yml)
[![PyPI](https://img.shields.io/pypi/v/cuke2confluence.svg)](https://pypi.org/project/cuke2confluence/)
[![Docker Pulls](https://img.shields.io/docker/pulls/lukian/cuke2confluence.svg)](https://hub.docker.com/r/lukian/cuke2confluence)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**cuke2conf** is a lightweight tool that converts [Cucumber JSON reports](https://cucumber.io/docs/cucumber/reporting/) into [Confluence](https://www.atlassian.com/software/confluence) pages — including feature summaries, scenario details, and embedded screenshots/files.

It’s designed for teams who want their automated **BDD test results** to show up in **Confluence automatically**, without copy-pasting or manual formatting.

---

## 📦 Get it

🐍 Python (PyPI)
```bash
pip install cuke2confluence[publish]
```

🐳 Docker (Docker Hub)

```
docker pull lukian/cuke2confluence:latest
```

## 🚀 Use it
1️⃣ Convert Cucumber JSON to Confluence XML
```bash
cuke2conf \
  --json target/cucumber-reports/cucumber.json \
  --title "Smoke Test Results" \
  --out page-storage.xml
```

2️⃣ Publish directly to Confluence
```bash
export CONFLUENCE_BASE_URL="https://your-domain.atlassian.net/wiki"
export CONFLUENCE_USER="user@example.com"
export CONFLUENCE_TOKEN="your_api_token"

cuke2conf \
  --json target/cucumber-reports/cucumber.json \
  --title "Smoke Test Results" \
  --space QA \
  --parent 123456789 \
  --publish
```

🐳 Use it with Docker - No Python needed
```bash
docker run --rm \
  -v "$PWD:/work" \
  <your-user>/cuke2confluence:latest \
  --json /work/target/cucumber-reports/cucumber.json \
  --title "Smoke Test Results" \
  --out /work/page-storage.xml
```

Or publish directly:
```bash
docker run --rm \
  -e CONFLUENCE_BASE_URL="https://your-domain.atlassian.net/wiki" \
  -e CONFLUENCE_USER="user@example.com" \
  -e CONFLUENCE_TOKEN="your_api_token" \
  -v "$PWD:/work" \
  <your-user>/cuke2confluence:latest \
  --json /work/target/cucumber-reports/cucumber.json \
  --title "Smoke Test Results" \
  --space QA \
  --parent 123456789 \
  --publish
```

## Links

🐍 PyPI: https://pypi.org/project/cuke2confluence

🐳 Docker Hub: https://hub.docker.com/r/lukian/cuke2confluence

📄 Cucumber JSON Format: https://cucumber.io/docs/cucumber/reporting/

📚 Confluence REST API: https://developer.atlassian.com/cloud/confluence/rest/

## License
MIT License © 2025 — sjacobs
