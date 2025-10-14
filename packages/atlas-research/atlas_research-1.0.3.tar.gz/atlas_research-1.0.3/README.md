<p align="center">
  <img src="https://raw.githubusercontent.com/engineer0427/Atlas/main/docs/AtlasImage.png" alt="Atlas Logo" width="400"/>
</p>

<p align="center">
  <a href="https://pypi.org/project/atlas-research/">
    <img src="https://img.shields.io/pypi/v/atlas-research?color=blue&style=for-the-badge" alt="PyPI version"/>
  </a>
  <a href="https://img.shields.io/badge/python-3.9+-brightgreen?style=for-the-badge&logo=python">
    <img src="https://img.shields.io/badge/python-3.9+-brightgreen?style=for-the-badge&logo=python" alt="Python"/>
  </a>
  <a href="https://github.com/engineer0427/Atlas/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/License-Apache%202.0-lightgrey?style=for-the-badge" alt="License"/>
  </a>
</p>

---

> 🧠 **AI로 그리는 지식의 지도.**  
> Atlas는 논문·코드·데이터셋을 연결하여 연구 네트워크를 시각화하고,  
> 핵심 인사이트를 도출하는 **AI 기반 연구 인사이트 소프트웨어 (SaaS)**입니다.

Atlas는 오픈소스 **AI Research Insight Software (SaaS)**로,  
연구자·개발자 누구나 논문, 코드, 데이터셋 간의 관계를 탐색하고  
AI가 도출한 **연구 인사이트를 시각적으로 확인**할 수 있습니다.  

---

## 🌐 Live Demo

> 📍 **Try Atlas Online:** [https://atlas.vercel.app](https://atlas.vercel.app)  
> 🧩 **Backend API:** [https://atlas-backend.onrender.com](https://atlas-backend.onrender.com)  
> 📦 **PyPI Package:** [https://pypi.org/project/atlas-research/](https://pypi.org/project/atlas-research/)

---

## 💡 Vision
> **From Framework to SaaS. From Knowledge to Insight.**

Atlas는 단순한 라이브러리가 아닌,  
AI가 연구 지식의 흐름을 자동으로 해석하는 **지식 탐색 소프트웨어**로 발전하고 있습니다.  
향후 버전에서는 연구 네트워크 분석, AI 논문 요약, 실시간 협업 기능이 통합될 예정입니다.

---

## 🚀 설치 (Installation)

### PyPI (Stable Release)
```bash
pip install atlas-research
```

### 개발 버전 (Local)
```bash
pip install -e .
```

---

## 🧠 주요 기능 (Key Features)

| 기능 | 설명 |
|------|------|
| 🔍 **AI Insight Engine** | arXiv 논문 분석 → 핵심 키워드 및 관련 논문 자동 추출 |
| 🌐 **Research Graph** | 논문·저자·코드·데이터셋 관계를 네트워크로 시각화 |
| ⚡ **End-to-End Pipeline** | Ingest → Link → Visualize → Export 전체 자동화 |
| 🧩 **CLI Interface** | `atlas run --query "<주제>"` 한 줄로 분석 실행 |
| ☁️ **SaaS Ready** | FastAPI 백엔드 + Next.js 프론트 통합 구조 |
| 🤖 **GitHub Actions CI/CD** | PyPI, Render, Vercel 자동 배포 파이프라인 내장 |

---

## ⚙️ 사용법 (CLI)

```bash
atlas run --query "Graph Neural Networks"
```

- 분석 결과는 `outputs/` 폴더에 저장됩니다.  
- 실행 로그는 `logs/atlas.log` 파일에 기록됩니다.  

---

## 📊 실행 결과 (Output)

| 결과물 | 설명 |
|---------|------|
| `outputs/graph_result.html` | 연구 네트워크 시각화 결과 (브라우저에서 탐색 가능) |
| `outputs/insight_report.json` | 핵심 키워드 및 관련 논문 요약 결과 |

---

## 🧩 CLI 명령어 (Commands)

| 명령어 | 설명 |
|--------|------|
| `atlas run --query "<주제>"` | 지정 주제의 연구 네트워크 분석 실행 |
| `atlas export` | 최근 분석 결과를 파일로 내보내기 |
| `atlas --version` | 현재 Atlas 버전 출력 |

---

## ⚙️ DevOps / CI Integration

Atlas는 완전 자동화된 SaaS 배포 구조를 갖습니다.

| 구성 요소 | 역할 |
|------------|------|
| 🧱 **GitHub Actions** | 테스트, 린트, PyPI 빌드, 배포 자동화 |
| ☁️ **Render** | FastAPI 백엔드 자동 배포 |
| 🌐 **Vercel** | Next.js 프론트엔드 자동 배포 |
| 🔐 **GitHub Secrets** | VERCEL / RENDER / PYPI 토큰 관리 |

> 💬 Push 한 번으로 Atlas 전체가 자동 빌드·배포됩니다.

---

## 💖 Support Atlas

Atlas는 연구자와 개발자가 **지식의 연결을 시각화**할 수 있도록 돕는 오픈소스 프로젝트입니다.  
당신의 후원은 Atlas의 **AI 인사이트 고도화, SaaS 고도화, UX 개선**을 가능하게 합니다.

<p align="center">
  <a href="https://github.com/sponsors/engineer0427">
    <img src="https://img.shields.io/badge/Sponsor-Atlas-blue?style=for-the-badge&logo=github-sponsors&logoColor=white" alt="Sponsor Atlas"/>
  </a>
</p>

> **Your support keeps Atlas evolving.**  
> 작은 후원이 연구 네트워크 혁신의 큰 힘이 됩니다. 💙

---

## ⚖️ License

이 프로젝트는 **Apache License 2.0** 하에 배포됩니다.  
자유롭게 복제, 수정, 배포, 상업적 이용이 가능하며,  
원저작자 명시만 유지하시면 됩니다.  
자세한 내용은 [LICENSE](./LICENSE) 파일을 참고하세요.
