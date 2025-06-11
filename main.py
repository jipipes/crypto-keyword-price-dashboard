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


def get_latest_timestamp_from_bigquery():
    """
    BigQuery 테이블에서 가장 최신 데이터의 timestamp를 가져옵니다.
    """
    query = f"""
    SELECT MAX(timestamp)
    FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`
    """
    try:
        query_job = client.query(query)
        results = query_job.result()
        for row in results:
            latest_timestamp_str = row[0]
            if latest_timestamp_str:
                # BigQuery의 TIMESTAMP 타입은 ISO 8601 문자열로 반환됩니다.
                # 이를 datetime 객체로 파싱합니다.
                # UTC 시간을 명시적으로 지정합니다.
                return datetime.fromisoformat(latest_timestamp_str.replace('Z', '+00:00')).astimezone(timezone.utc)
            return None
    except Exception as e:
        print(f"Error fetching latest timestamp from BigQuery: {e}")
        return None

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

def insert_data_to_bigquery(df_processed):
    """
    전처리된 Pandas DataFrame을 BigQuery upbit_hourly_candles 테이블에 행 단위로 삽입합니다.
    """
    if df_processed.empty:
        print("No data to insert.")
        return

    rows_to_insert = []
    for _, row in df_processed.iterrows():
        timestamp_str = row['timestamp_utc'].isoformat(timespec='microseconds')
    # Upbit API 응답 필드와 BigQuery 테이블 스키마 매핑
        try:
            row_data = {
                'timestamp': timestamp_str,
                'market': row['market'],
                'opening_price': row['opening_price'],
                'high_price': row['high_price'],
                'low_price': row['low_price'],
                'closing_price': row['trade_price'], # Upbit에서는 종가가 trade_price로 제공
                'trade_volume': row['candle_acc_trade_volume']
            }
            rows_to_insert.append(row_data)
        except Exception as e:
            print(f"Error processing row for BigQuery insertion: {row.get('candle_date_time_utc', 'N/A')} - {e}")
            continue

    if not rows_to_insert:
        print("No valid rows to insert after processing.")
        return

    try:
        errors = client.insert_rows_json(table_ref, rows_to_insert)
        if errors:
            for error in errors:
                if 'timestamp' in error['errors'][0]['message'] and 'duplicate' in error['errors'][0]['message'].lower():
                    # 중복 오류 메시지는 무시하거나 별도 처리할 수 있습니다.
                    print(f"INFO: Duplicate row detected and skipped: {error}")
                else:
                    print(f"ERROR: Errors occurred while inserting rows: {error}")
        else:
            print(f"Successfully loaded {len(rows_to_insert)} rows into {PROJECT_ID}:{DATASET_ID}.{TABLE_ID} using insert_rows_json.")
    except Exception as e:
        print(f"An error occurred during BigQuery insert_rows_json: {e}")


def ingest_upbit_candles_function(request):
    print("Starting Upbit hourly candle ingestion...")
    try:
        last_timestamp_utc = get_latest_timestamp_from_bigquery()

        to_fetch_date = None

        if last_timestamp_utc:
            to_fetch_date = datetime.now(timezone.utc)
             # TODO: 나중에 이 부분을 last_timestamp_utc를 활용하여 누락 데이터를 더 효율적으로 채우도록 개선할 수 있습니다.
            pass

        # 비트코인(KRW-BTC) 시간봉 200개를 가져옵니다.
        upbit_raw_data = get_upbit_hourly_candles(market_code='KRW-BTC', count=200, to_date=to_fetch_date) 

        if upbit_raw_data:
            df = pd.DataFrame(upbit_raw_data)
            # 데이터 중복 방지 (선택 사항):
            # BigQuery에 이미 있는 시간대의 데이터는 추가하지 않도록
            # 삽입 전에 DataFrame에서 중복된 timestamp를 가진 행을 제거하는 로직을 추가할 수 있습니다.
            # 그러나, 지금은 단순화를 위해 생략하며, cronjob으로 자주 실행 시 중복이 발생할 수 있습니다.
            # 정확한 중복 제거는 데이터베이스에 이미 존재하는 timestamp를 확인하는 쿼리가 필요합니다.

            df['timestamp_utc'] = pd.to_datetime(df['candle_date_time_utc'], utc=True).dt.floor('us')
            df['opening_price'] = pd.to_numeric(df['opening_price'], errors='coerce')
            df['high_price'] = pd.to_numeric(df['high_price'], errors='coerce')
            df['low_price'] = pd.to_numeric(df['low_price'], errors='coerce')
            df['trade_price'] = pd.to_numeric(df['trade_price'], errors='coerce') # closing_price용
            df['candle_acc_trade_volume'] = pd.to_numeric(df['candle_acc_trade_volume'], errors='coerce')

            print(f"DEBUG: DataFrame head:\n{df.head()}")
            print(f"DEBUG: DataFrame dtypes:\n{df.dtypes}")
 
            insert_data_to_bigquery(df)
        else:
            print("No data received from Upbit API.")
    except requests.exceptions.RequestException as req_e:
        print(f"Network or API request error: {req_e}")
        return f"Network or API request error: {req_e}", 500
    except Exception as e:
        print(f"An unexpected error occurred during ingestion: {e}")
        return f"An unexpected error occurred during ingestion: {e}", 500

    print("Upbit hourly candle ingestion completed.")
    return "Upbit hourly candle ingestion completed successfully.", 200

if __name__ == "__main__":
    ingest_upbit_candles_function(None)
