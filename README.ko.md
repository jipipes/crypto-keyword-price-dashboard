<p align="right">
  <a href="./README.md">English</a>
</p>

# 📈 크립토 키워드 가격 대시보드

> “사람들의 말이 가격에 영향을 미친다면, 그 흔적은 어디서 드러날까?”

이 프로젝트는 비트코인과 같은 암호화폐에 대해 사람들이 어떤 이야기를 많이 하고 있는지를 다양한 경로로 수집하고, 그 언급량과 가격 변동 간의 상관관계를 시각화하여 보여주는 대시보드입니다.

## 프로젝트 설명

이 프로젝트는 트위터, 뉴스, 커뮤니티 등 다양한 출처에서 비트코인 관련 키워드를 수집하고, 해당 키워드의 언급량과 가격 변화 간의 상관관계를 분석하여 대시보드에 시각화합니다.

## 프로젝트 목적

비트코인의 가격은 기업 실적이나 금리 같은 전통적인 지표로는 설명하기 어렵습니다. 대신 뉴스, 트윗 등에서 나타나는 사람들의 ‘심리’가 시장에 영향을 줄 수 있다는 가설에 기반합니다.

이 프로젝트는 자주 언급되는 키워드와 가격 흐름을 타임라인에 함께 시각화함으로써 이슈와 반응의 흐름을 한눈에 보여주는 시스템을 구축하는 것을 목표로 합니다.

## 주요 기능

- 암호화폐 가격 데이터 자동 수집
- 다양한 소스에서 가장 많이 언급된 키워드 10개 추출
- 키워드 언급량과 가격 변화를 타임라인 형태로 시각화
- 키워드 등장 시점과 가격 흐름을 연결하여 시각적 이해 제공
- 향후 Streamlit 기반 대시보드 형태로 구현 예정

## 기술 스택

| 기능            | 사용 기술                               |
|-----------------|------------------------------------------|
| 키워드 수집     | API                                      |
| 가격 데이터      | Upbit API                                |
| 데이터 처리      | Python, Google Pub/Sub                   |
| 저장소           | Google Cloud Storage → BigQuery         |
| 시각화           | Streamlit                                |
| 워크플로우 관리  | Apache Airflow                           |

## 아키텍처 구조

![Image](https://github.com/user-attachments/assets/f96b069d-0f1a-4efc-8d37-7b9180fdfda3)

## 설치

### 필수 조건

- Python 3.10 이상
- Streamlit
- Google Cloud SDK (엔드투엔드 실행 시 필요)

### 설치 방법

```bash
git clone https://github.com/your-id/crypto-keyword-price-dashboard.git
cd crypto-keyword-price-dashboard
pip install -r requirements.txt
```

### 대시보드 실행

```bash
streamlit run app.py
```

## 대시보드 스크린샷

*추후 추가 예정...*

## 참고 자료

- [Upbit API 문서](https://docs.upbit.com/)
- [Streamlit 공식 문서](https://docs.streamlit.io/)
- [Google Cloud BigQuery](https://cloud.google.com/bigquery)
- [Apache Airflow 공식 문서](https://airflow.apache.org/docs/)
