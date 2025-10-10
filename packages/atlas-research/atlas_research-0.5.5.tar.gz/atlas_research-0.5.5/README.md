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
> Atlas는 논문·코드·데이터셋을 연결하여 연구 네트워크를 시각화하고, 핵심 인사이트를 도출하는 오픈소스 프레임워크입니다.

Atlas는 **AI 기반 연구 인사이트 탐색 및 네트워크 시각화**를 지원하는 Python 패키지입니다.  
arXiv 등 학술 데이터를 분석해 논문, 코드, 데이터셋 간의 관계를 **지도로 시각화**하고,  
자동으로 핵심 키워드와 유사 논문을 도출합니다.

---

## 💡 Vision
Atlas는 논문·코드·데이터를 연결해  
**AI가 연구 네트워크 속 인사이트를 찾아주는 지식 탐색 플랫폼**으로 발전하고 있습니다.

---

## 🚀 설치 (Installation)

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
| ⚡ **End-to-End Pipeline** | 검색 → 분석 → 인사이트 → 시각화까지 일괄 처리 |
| 🪶 **Lightweight CLI** | `atlas run "query"` 한 줄로 분석 실행 |
| 🎨 **White Signature Theme** | 화이트 팔레트 기반, 가독성 높은 레이아웃 |

---

## 📊 실행 결과 (Output)

- 시각화 결과: `outputs/graph_*.html`  
  → 브라우저에서 열어 **연구 네트워크 탐색 가능**  
- 인사이트 결과: `outputs/insight_*.json`  
  → 상위 키워드 및 유사 논문 목록 자동 요약

---

## ⚙️ 사용법 (Usage)

```bash
atlas run "graph neural networks"
```

- 분석 결과는 `outputs/` 폴더에 저장됩니다.  
- 실행 로그는 `logs/atlas.log` 파일에 기록됩니다.

---

## 🧩 CLI 명령어 (Commands)

| 명령어 | 설명 |
|--------|------|
| `atlas run "<query>"` | 지정한 주제에 대한 분석 수행 |
| `atlas export` | 최근 분석 결과를 파일로 내보내기 |

---

## 💾 로깅 (Logging)

Atlas는 실행 시 자동으로 로그를 생성합니다.

```
logs/atlas.log
```

모든 실행 기록이 시간순으로 저장되어,  
분석 재현성과 디버깅에 유용합니다.

---

## 💖 Support Atlas

Atlas는 연구자와 개발자가 **지식의 연결을 시각화**할 수 있도록 돕는 오픈소스 프로젝트입니다.  
당신의 후원은 Atlas의 **AI 인사이트 고도화, SaaS 전환, UX 개선**을 가능하게 합니다.

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
