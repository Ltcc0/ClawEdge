为了让你的 GitHub 仓库看起来非常专业，我编写了这份最终版的 `README.md`。

**⚠️ 操作建议**：
1. 请将你刚才发给我的工作流图片下载下来。
2. 在你的 GitHub 项目根目录下创建一个文件夹叫 `docs`，将图片重命名为 `workflow.png` 放入其中。
3. 这样文档中的图片引用 `![ClawEdge Workflow](./docs/workflow.png)` 就能正常显示了。

---

# 🦀 ClawEdge

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)

**ClawEdge** is a professional **Human-in-the-Loop (HITL)** monitoring middleware for AI Agents. It acts as a security guardrail that intercepts user commands, analyzes intentions via **OpenRouter**, and decomposes them into manageable subtasks. The core mission of ClawEdge is to ensure that no autonomous action is taken on your server without explicit human approval.

---

## 📊 System Workflow

![ClawEdge Workflow](G:\workflow.jpg)

The ClawEdge architecture ensures a strict separation between **Planning** and **Execution**:

1.  **User Message**: Sent via Chat Apps (Telegram, Feishu, etc.).
2.  **Analyze Intent**: ClawEdge intercepts the webhook and prompts the LLM (via OpenRouter) to evaluate the request.
3.  **Subtasks Plan**: The LLM generates a step-by-step execution plan in JSON format.
4.  **Approve/Reject**: The plan is sent back to the user as an interactive card. The system waits for a "GO" signal.
5.  **Local/Ubuntu Agent**: Only after approval, the local Agent is triggered to perform the actual work.
6.  **Context & Skills**: The Agent utilizes its memory and tools to execute the specific subtasks.
7.  **Final Result**: The execution outcome is summarized and sent back to the user.

---

## ✨ Key Features

-   🌍 **Multi-Platform Support**: Ready-to-use adapters for **Telegram** (Inline Buttons) and **Feishu/Lark** (Interactive Cards).
-   🛡️ **Safety Guardrails**: Prevents "Agent Hallucinations" and accidental command execution (like `rm -rf`).
-   🧠 **OpenRouter Powered**: Seamlessly switch between DeepSeek, Claude 3.5, GPT-4o, or Llama 3 for planning.
-   ⚡ **Asynchronous Logic**: Built on FastAPI for high-concurrency webhook handling.

---

## 🚀 Getting Started

### 1. Installation (Local)
```bash
git clone https://github.com/your-username/ClawEdge.git
cd ClawEdge

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configuration (`.env`)
Create a `.env` file with your credentials:
```ini
BASE_URL=https://your-agent-domain.com
OPENAI_API_KEY=sk-or-v1-xxxxxx # Your OpenRouter Key
OPENAI_MODEL=deepseek/deepseek-chat
TELEGRAM_BOT_TOKEN=xxxxxx
FEISHU_APP_ID=cli_xxxx
FEISHU_APP_SECRET=xxxx
```

### 3. Ubuntu Server Deployment (Production)
For a stable 24/7 setup, use Nginx and Systemd:

#### A. Create Systemd Service
`sudo nano /etc/systemd/system/clawedge.service`
```ini
[Unit]
Description=ClawEdge FastAPI Service
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/ClawEdge
Environment="PATH=/var/www/ClawEdge/venv/bin"
ExecStart=/var/www/ClawEdge/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker --bind unix:clawedge.sock main:app

[Install]
WantedBy=multi-user.target
```

#### B. Nginx & SSL
Map your domain and use Certbot for HTTPS:
```bash
# Set up Nginx config pointing to the .sock file
sudo certbot --nginx -d your-agent-domain.com
```

---

## 🤝 Contributing (Standards)

We welcome developers to help us make AI Agents safer! Please follow these standards:

### Development Workflow
1.  **Fork** the repo and branch from `develop`.
2.  **Conventional Commits**: Use `feat:`, `fix:`, or `docs:` prefixes.
3.  **Linting**: We recommend using `ruff` to maintain code quality.

### Pull Request Rules
-   Describe the specific changes and the reasoning behind them.
-   Update documentation if new platform adapters are added.
-   PRs require at least one maintainer's approval before merging to `main`.

---

## 🗺️ Roadmap
- [ ] **Redis Backend**: Support persistent session state for scaling.
- [ ] **Slack & Discord Adapters**: Expand the HITL interface.
- [ ] **Web Dashboard**: Real-time visualization of Agent subtask execution.
- [ ] **Multi-Agent Orchestration**: Managing multiple agents under one ClawEdge sentinel.

---

## 📄 License
This project is licensed under the **MIT License**.

## 🙌 Acknowledgments
- Inspired by the **HKUDS Nanobot** workflow.
- Special thanks to the **OpenRouter** team for the unified API.

---
**ClawEdge** - *The edge of control for your AI Agents.*