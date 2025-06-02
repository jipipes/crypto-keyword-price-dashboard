import requests
import pandas as pd
from google.cloud import bigquery
import os
from datetime import datetime, timezone, timedelta

# GCP 프로젝트 ID 설정
PROJECT_ID = os.environ.get('GCP_PROJECT_ID', 'sunny-mountain-461400-r5')
DATASET_ID = 'price_data'
TABLE_ID = 'upbit_hourly_candles'

# BigQuery 클라이언트 초기화
client = bigquery.Client(project=PROJECT_ID)
table_ref = client.dataset(DATASET_ID).table(TABLE_ID)

def get_upbit_hourly_candles(market_code='KRW-BTC', count=200, to_date=None):
    """
    Upbit API에서 시간봉(Hourly Candles, 60분 캔들) 데이터를 가져옵니다.
    :param market_code: 시장 코드 (예: 'KRW-BTC')
    :param count: 가져올 캔들 개수 (최대 200개)
    :param to_date: ISO 8601 형식의 UTC 시간 (이 시간까지의 캔들을 가져옴). 기본값은 현재 UTC 시간.
    :return: 캔들 데이터 (JSON)
    """
    # API 엔드포인트를 분봉 (minutes)의 60분 단위로 변경
    url = f"https://api.upbit.com/v1/candles/minutes/60"
    params = {
        'market': market_code,
        'count': count
    }
    if to_date:
        params['to'] = to_date # 특정 시점까지의 데이터를 가져올 때 사용

    headers = {"Accept": "application/json"}
    print(f"Fetching hourly candles from: {url} with params: {params}")
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status() # HTTP 오류가 발생하면 예외 발생
    return response.json()

def insert_data_to_bigquery(df):
    """
    Pandas DataFrame을 BigQuery upbit_hourly_candles 테이블에 삽입합니다.
    """
    if df.empty:
        print("No data to insert.")
        return

    # Upbit API 응답 필드와 BigQuery 테이블 스키마 매핑
    df['timestamp'] = pd.to_datetime(df['candle_date_time_utc'], utc=True)

    df_to_insert = pd.DataFrame({
        'timestamp': df['timestamp'],
        'market': df['market'],
        'opening_price': df['opening_price'],
        'high_price': df['high_price'],
        'low_price': df['low_price'],
        'closing_price': df['trade_price'], # Upbit에서는 종가가 trade_price로 제공
        'trade_volume': df['candle_acc_trade_volume']
    })

    # BigQuery LoadJobConfig 설정
    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND, # 기존 테이블에 데이터 추가
    )

    try:
        job = client.load_table_from_dataframe(
            df_to_insert, table_ref, job_config=job_config
        )
        job.result() # 작업 완료 대기
        print(f"Successfully loaded {job.output_rows} rows into {PROJECT_ID}:{DATASET_ID}.{TABLE_ID}")
    except Exception as e:
        print(f"Error inserting data into BigQuery: {e}")
        if hasattr(job, 'errors') and job.errors:
            for error in job.errors:
                print(f"BigQuery Error Detail: {error.get('message', 'No message')}")

if __name__ == "__main__":
    print("Starting Upbit hourly candle ingestion...")
    try:
        # 비트코인(KRW-BTC) 시간봉 200개를 가져옵니다.
        upbit_raw_data = get_upbit_hourly_candles(market_code='KRW-BTC', count=200) 

        if upbit_raw_data:
            df = pd.DataFrame(upbit_raw_data)
            # 데이터 중복 방지 (선택 사항):
            # BigQuery에 이미 있는 시간대의 데이터는 추가하지 않도록
            # 삽입 전에 DataFrame에서 중복된 timestamp를 가진 행을 제거하는 로직을 추가할 수 있습니다.
            # 그러나, 지금은 단순화를 위해 생략하며, cronjob으로 자주 실행 시 중복이 발생할 수 있습니다.
            # 정확한 중복 제거는 데이터베이스에 이미 존재하는 timestamp를 확인하는 쿼리가 필요합니다.

            insert_data_to_bigquery(df)
        else:
            print("No data received from Upbit API.")
    except requests.exceptions.RequestException as req_e:
        print(f"Network or API request error: {req_e}")
    except Exception as e:
        print(f"An unexpected error occurred during ingestion: {e}")

    print("Upbit hourly candle ingestion completed.")
