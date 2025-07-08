<p align="right">
  🇬🇧 <a href="./README.ko.md">한국어</a>
</p>

# 📈 Crypto Keyword Price Dashboard

> "If words influence prices, where would we see the trace?"

This project visualizes the correlation between the frequency of crypto-related keywords and the price fluctuation of assets like Bitcoin, collected from various sources.

## Description

This project collects and analyzes what people are saying about specific cryptocurrencies like Bitcoin from various sources. It visualizes the relationship between the number of keyword mentions and actual price movements through an interactive dashboard.

## Objective

Bitcoin prices are difficult to explain with traditional indicators such as earnings or interest rates. This project is based on the hypothesis that public sentiment—expressed through keywords in news, tweets, or online communities—might influence the market.

It aims to build a system that visualizes the timeline of frequently mentioned keywords alongside price trends, making issue-reaction patterns intuitive.

## Key Features

- Automatic collection of crypto price data
- Extraction of top 10 frequently mentioned keywords from various sources
- Visualization of keyword-price relationships on a timeline
- Timeline highlights of keyword emergence and corresponding price movements
- Planned implementation using Streamlit dashboard

## Tech Stack

| Function         | Technologies                           |
|------------------|-----------------------------------------|
| Keyword Mining   | APIs                                    |
| Price Data       | Upbit API                               |
| Data Processing  | Python, Google Pub/Sub                  |
| Storage          | Google Cloud Storage → BigQuery       |
| Visualization    | Streamlit                               |
| Workflow         | Apache Airflow                          |

## Architecture Diagram

![Image](https://github.com/user-attachments/assets/f96b069d-0f1a-4efc-8d37-7b9180fdfda3)

## Getting Started

### Prerequisites

- Python 3.10+
- Streamlit
- Google Cloud SDK (if running end-to-end pipeline)

### Installation

```bash
git clone https://github.com/your-id/crypto-keyword-price-dashboard.git
cd crypto-keyword-price-dashboard
pip install -r requirements.txt
```

### Run Dashboard

```bash
streamlit run app.py
```

## Demo Screenshot

*To be added...*

<!-- Example -->
<!-- ![dashboard screenshot](./assets/screenshot.png) -->

## References

- [Upbit API Docs](https://docs.upbit.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Google Cloud BigQuery](https://cloud.google.com/bigquery)
- [Apache Airflow Docs](https://airflow.apache.org/docs/)
