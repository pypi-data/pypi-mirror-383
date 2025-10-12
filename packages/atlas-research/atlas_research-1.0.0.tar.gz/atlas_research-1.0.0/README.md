<p align="center">
  <img src="https://raw.githubusercontent.com/engineer0427/Atlas/main/docs/AtlasImage.png" alt="Atlas Logo" width="400"/>
</p>

<p align="center">
  <a href="https://pypi.org/project/atlas-research/">
    <img src="https://img.shields.io/pypi/v/atlas-research?color=blue&style=for-the-badge" alt="PyPI version"/>
  </a>
  <a href="https://github.com/sponsors/engineer0427">
    <img src="https://img.shields.io/badge/Sponsor-❤-pink?style=for-the-badge&logo=github" alt="Sponsor Atlas"/>
  </a>
</p>

---

> 🧠 **AI로 그리는 지식의 지도.**  
> Atlas는 논문·코드·데이터셋을 연결하여 연구 네트워크를 시각화하고,  
> 핵심 인사이트를 도출하는 **AI 기반 연구 인사이트 소프트웨어 (SaaS)**입니다.

Atlas는 오픈소스 **AI Research Insight Software (SaaS)**로,  
연구자·개발자 누구나 논문, 코드, 데이터셋 간의 관계를 탐색하고  
AI가 도출한 **연구 인사이트를 시각적으로 확인**할 수 있습니다.  

또한 Python 기반의 **확장형 프레임워크 엔진**으로,  
Atlas의 파이프라인(수집 → 연결 → 분석 → 시각화)을  
자신의 프로젝트나 SaaS 환경에 맞게 통합할 수 있습니다.

---

## 💡 Vision

> **From Framework to SaaS. From Knowledge to Insight.**

Atlas는 단순한 라이브러리가 아닌,  
AI가 연구 지식의 흐름을 자동으로 해석하는 **지식 탐색 소프트웨어**로 발전하고 있습니다.  
향후 버전에서는 연구 네트워크 분석, AI 논문 요약, 실시간 협업 기능이 통합될 예정입니다.

---

## 🚀 설치 (installation)

### 개발 버전 (로컬 실행)
```bash
pip install -e .
```

### PyPI 배포 버전
```bash
pip install atlas-research
```

---

## 🧠 주요 기능 (Key Features)

| 기능 | 설명 |
|------|------|
| 🔍 **AI Insight Engine** | arXiv 논문 분석 → 핵심 키워드 및 관련 논문 자동 추출 |
| 🌐 **Research Graph** | 논문·저자·코드·데이터셋 관계를 네트워크로 시각화 |
| ⚡ **End-to-End Pipeline** | Ingest → Link → Visualize → Export 전체 자동화 |
| 🧩 **CLI Interface** | `atlas run --query "<주제>"` 한 줄로 분석 실행 |
| 🎨 **White Signature Theme** | 가독성 높은 화이트 팔레트 기반 UI |
| ☁️ **SaaS Ready** | FastAPI 백엔드 및 Next.js UI 기반 SaaS 구조 내장 |

---

## ⚙️ 사용법 (Usage)

```bash
atlas run --query "Graph Neural Networks"
```

- 분석 결과는 `outputs/` 폴더에 저장됩니다.  
- 실행 로그는 `logs/atlas.log` 파일에 기록됩니다.  
- CLI를 통해 **End-to-End 분석**이 자동으로 수행됩니다.

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
| `atlas run --query "<주제>"` | 지정한 주제의 연구 네트워크 분석 실행 |
| `atlas export` | 최근 분석 결과를 파일로 내보내기 |
| `atlas --version` | 현재 Atlas 버전 출력 |

---

## 💖 Support Atlas

Atlas는 연구자와 개발자가 **지식의 연결을 시각화**할 수 있도록 돕는 오픈소스 프로젝트입니다.  
당신의 후원은 Atlas의 **AI 인사이트 고도화, SaaS 고도화, UX 개선**을 가능하게 합니다.

<p align="center">
  <a href="https://github.com/sponsors/engineer0427">
    <img src="https://img.shields.io/badge/Become a Sponsor-Atlas-blue?style=for-the-badge&logo=github-sponsors&logoColor=white" alt="Sponsor Atlas"/>
  </a>
</p>

> **Your support keeps Atlas evolving.**  
> 작은 후원이 연구 네트워크 혁신의 큰 힘이 됩니다. 💙

---

## ⚖️ 라이선스 (License)

이 프로젝트는 **Apache License 2.0** 하에 배포됩니다.  
사용자는 자유롭게 복제, 수정, 배포, 상업적 이용이 가능합니다.  
단, 다음 조건을 따라야 합니다:

1. `LICENSE` 사본을 포함해야 합니다.  
2. 원저작자 명시: `Based on Atlas Software by Han Jeongwoo`  
3. 수정한 경우, 변경 사실을 명시해야 합니다.  
4. 특허권은 Apache-2.0 조항에 따라 부여됩니다.  

자세한 내용은 [LICENSE](./LICENSE) 파일을 참고하세요.
