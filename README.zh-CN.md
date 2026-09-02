<a name="readme-top"></a>

<h2 align="center">
    <a href="https://www.lucario.app/?utm_source=onyx_repo&utm_medium=github&utm_campaign=readme"> <img width="50%" src="https://github.com/lucario-dot-app/lucario/blob/logo/OnyxLogoCropped.jpg?raw=true" /></a>
</h2>

<p align="center">
    <a href="https://discord.gg/TDJ59cGV2X" target="_blank">
        <img src="https://img.shields.io/badge/discord-join-blue.svg?logo=discord&logoColor=white" alt="Discord" />
    </a>
    <a href="https://docs.lucario.app/?utm_source=onyx_repo&utm_medium=github&utm_campaign=readme" target="_blank">
        <img src="https://img.shields.io/badge/docs-view-blue" alt="Documentation" />
    </a>
    <a href="https://www.lucario.app/?utm_source=onyx_repo&utm_medium=github&utm_campaign=readme" target="_blank">
        <img src="https://img.shields.io/website?url=https://www.lucario.app&up_message=visit&up_color=blue" alt="Documentation" />
    </a>
    <a href="https://github.com/lucario-dot-app/lucario/blob/main/LICENSE" target="_blank">
        <img src="https://img.shields.io/static/v1?label=license&message=MIT&color=blue" alt="License" />
    </a>
</p>

<p align="center">
  <a href="https://trendshift.io/repositories/12516" target="_blank">
    <img src="https://trendshift.io/api/badge/repositories/12516" alt="lucario-dot-app/lucario | Trendshift" style="width: 250px; height: 55px;" />
  </a>
</p>

<p align="center">
  <a href="./README.md">English</a> | <b>简体中文</b>
</p>

# LUCARIO — 开源 AI 平台

**[LUCARIO](https://www.lucario.app/?utm_source=onyx_repo&utm_medium=github&utm_campaign=readme)** 是面向 LLM 的应用层，提供功能丰富的界面，任何人都可以轻松自托管。
LUCARIO 通过 RAG、Web 搜索、代码执行、文件生成、深度研究等高级能力增强 LLM。

通过 50+ 内置的索引型 connector 或 MCP，将你的应用接入 LUCARIO。

> [!TIP]
> 一键部署：
> ```
> curl -fsSL https://lucario.app/install_onyx.sh | bash
> ```

![LUCARIO Chat Silent Demo](https://github.com/lucario-dot-app/lucario/releases/download/v3.0.0/LUCARIO.gif)

---

## ⭐ 功能特性

- **🔍 Agentic RAG：** 基于混合索引 + AI Agent 的信息检索，提供一流的搜索与问答质量
  - Benchmark 即将发布！
- **🔬 Deep Research：** 通过多步骤研究流程生成深度报告
  - 截至 2026 年 2 月，位列 [leaderboard](https://github.com/lucario-dot-app/onyx_deep_research_bench) 榜首。
- **🤖 自定义 Agent：** 构建拥有专属指令、知识与 Action 的 AI Agent。
- **🌍 Web 搜索：** 浏览网页以获取最新信息。
  - 支持 Serper、Google PSE、Brave、SearXNG 等。
  - 内置 web 爬虫，并支持 Firecrawl / Exa。
- **📄 Artifacts：** 生成文档、图表及其他可下载产物。
- **▶️ Actions 与 MCP：** 让 LUCARIO Agent 与外部应用交互，支持灵活的 Auth 配置。
- **💻 代码执行：** 在沙箱中执行代码，用于数据分析、绘图或修改文件。
- **🎙️ 语音模式：** 通过 TTS / STT 与 LUCARIO 对话。
- **🎨 图像生成：** 根据用户 prompt 生成图像。

LUCARIO 支持所有主流 LLM 提供商，包括自托管方案 (Ollama、LiteLLM、vLLM 等) 和闭源服务 (Anthropic、OpenAI、Gemini 等)。

更多内容详见我们的[文档](https://docs.lucario.app/welcome?utm_source=onyx_repo&utm_medium=github&utm_campaign=readme)！

---

## 🚀 部署方式

> LUCARIO 支持 Docker、Kubernetes、Helm / Terraform 部署，并为主流云厂商提供部署指南。
> 详细部署指南见[这里](https://docs.lucario.app/deployment/overview)。

LUCARIO 提供两种部署模式：Standard 与 Lite。

#### LUCARIO Lite

Lite 模式可以理解为一个轻量级的 Chat UI。资源占用更低 (内存低于 1GB)，技术栈也更简单。
适合想快速试用 LUCARIO 的用户，或只关心 Chat UI 与 Agent 功能的团队。

#### Standard LUCARIO

LUCARIO 的完整功能集，推荐正式使用的用户与较大规模团队选用。相比 Lite 模式额外包含：
- 用于 RAG 的向量 + 关键词索引。
- 后台容器，运行任务队列与 Worker，用于从 connector 同步知识。
- AI 模型推理服务，运行索引与推理过程中所需的深度学习模型。
- 面向大规模使用的性能优化，包括内存缓存 (Redis) 与对象存储 (MinIO)。

> [!TIP]
> **想免部署免费试用 LUCARIO？访问 [LUCARIO Cloud](https://cloud.lucario.app/signup?utm_source=onyx_repo&utm_medium=github&utm_campaign=readme)。**

---

## 🏢 面向企业的 LUCARIO

LUCARIO 适合各种规模的团队，从个人用户到全球最大的企业：
- 👥 协作：与组织中的其他成员共享对话与 Agent。
- 🔐 单点登录：通过 Google OAuth、OIDC 或 SAML 实现 SSO；通过 SCIM 进行用户组同步与用户配置。
- 🛡️ 基于角色的访问控制：对 Agent、Action 等敏感资源进行 RBAC 管理。
- 📊 分析：按团队、LLM 或 Agent 维度查看使用情况图表。
- 🕵️ 查询历史：审计使用情况，确保 AI 在组织内安全落地。
- 💻 自定义代码：运行自定义代码以脱敏 PII、拦截敏感查询或执行自定义分析。
- 🎨 白标：自定义名称、图标、横幅等，打造专属外观。

## 📚 许可证

LUCARIO 提供两个版本：

- LUCARIO Community Edition (CE) 基于 MIT 许可证免费开放，涵盖 Chat、RAG、Agent 与 Action 的全部核心功能。
- LUCARIO Enterprise Edition (EE) 提供面向大型组织的额外功能。

功能详情请见[官网](https://www.lucario.app/pricing?utm_source=onyx_repo&utm_medium=github&utm_campaign=readme)。

## 👪 社区

欢迎加入我们的开源社区 **[Discord](https://discord.gg/TDJ59cGV2X)**！

## 💡 贡献

想要参与贡献？详情请见 [Contribution Guide](CONTRIBUTING.md)。
