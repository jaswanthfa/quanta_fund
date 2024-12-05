import psycopg2
import requests
import pandas as pd
# connect to database
conn = psycopg2.connect(
    host="localhost", database="postgres", user="postgres", password="example",port="5432"
)
conn.commit()
cur = conn.cursor()

cur.execute("""
SELECT shares, holdings.cusip, security_name, ticker, period_of_report, holdings.filing_id
FROM "holdings"
INNER JOIN filings
ON filings.filing_id = holdings.filing_id
INNER JOIN holding_infos
ON holdings.cusip = holding_infos.cusip
WHERE (period_of_report = '2024-06-30') and cik = '1067983'
""")

rows = cur.fetchall()    

cur.close()

buffet_holdings = pd.DataFrame(rows, columns =['Shares', 
                                               'CUSIP', 
                                               'SecurityName', 
                                               'Ticker', 
                                               'PeriodOfReport', 
                                               'FilingId'])

print(len(buffet_holdings))