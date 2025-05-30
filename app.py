import streamlit as st
from google.cloud import bigquery
import pandas as pd
import os

# 환경 변수에서 프로젝트 ID 로드 (배포 시 활용)
project_id = os.environ.get('GCP_PROJECT_ID', 'sunny-mountain-461400-r5')

st.set_page_config(layout="wide") # 넓은 레이아웃 사용

# BigQuery 클라이언트 초기화
# Compute Engine VM 인스턴스에 적절한 IAM 권한이 부여되어 있다면 별도의 인증 파일 없이 동작
# 로컬에서 테스트할 때는 gcloud auth application-default login 명령어를 실행하거나,
# 서비스 계정 키 파일을 환경 변수 GOOGLE_APPLICATION_CREDENTIALS에 설정해야 함
# VM에서는 BigQuery 읽기 권한만 있으면 됨.
client = bigquery.Client(project=project_id)

@st.cache_data(ttl=600) # 10분마다 데이터 캐싱. 데이터 빈번하게 바뀌는 경우 ttl 조정
def get_upbit_data():
    """
    BigQuery에서 Upbit 거래 데이터를 가져오는 함수
    """
    query = f"""
    SELECT market, price, timestamp
    FROM `{project_id}.crypto_data.upbit_trades`
    ORDER BY timestamp DESC
    LIMIT 100
    """
    try:
        query_job = client.query(query)
        df = query_job.to_dataframe()
        
        if 'timestamp' in df.columns:
            # BigQuery TIMESTAMP 필드는 Pandas datetime으로 직접 변환될 수 있음
            # 만약 로드된 데이터의 timestamp가 object 타입 등으로 이상하게 보인다면,
            # pd.to_datetime(df['timestamp'], unit='ms') 또는 다른 형식으로 변환 고려.
            # 하지만 BigQuery에서 정상적으로 가져오면 바로 datetime 타입일 가능성이 높음.
            df['timestamp'] = pd.to_datetime(df['timestamp'])

            # 만약 BigQuery에 저장된 시간이 UTC이고, 대시보드에서는 KST로 보여주고 싶다면:
            df['timestamp'] = df['timestamp'].dt.tz_localize('UTC').dt.tz_convert('Asia/Seoul')
            # 이 코드는 데이터가 BigQuery에 UTC로 저장되어 있다고 가정하고 KST로 변환
            
        return df
    except Exception as e:
        st.error(f"BigQuery에서 데이터를 가져오는 데 실패했습니다: {e}")
        return pd.DataFrame() # 에러 발생 시 빈 DataFrame 반환

st.title("Upbit Trading Dashboard")

upbit_df = get_upbit_data()

if not upbit_df.empty:
    st.write("### 최근 Upbit 거래 데이터")
    st.dataframe(upbit_df)

    if 'timestamp' in upbit_df.columns and 'price' in upbit_df.columns:
        st.write("### 가격 추이 (최근 100개 데이터)")
        
        # 라인 차트 생성 시 timestamp를 인덱스로 설정
        st.line_chart(upbit_df.set_index('timestamp')['price'])
    else:
        st.warning("가격 추이를 표시할 수 있는 컬럼(timestamp, price)이 없습니다.")
else:
    st.info("BigQuery에서 데이터를 가져오지 못했거나, 데이터가 없습니다. BigQuery 테이블에 샘플 데이터가 있는지 확인해주세요.")

st.sidebar.header("설정")
if st.sidebar.button("데이터 새로고침"):
    st.cache_data.clear() # 캐시 삭제
    st.rerun() # 앱 재실행