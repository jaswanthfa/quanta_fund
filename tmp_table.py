import psycopg2
import pandas as pd
from change_in_holdings import calculate_holding_changes
from datetime import datetime
# connect to database

conn = psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",  # default user is 'postgres' in the official PostgreSQL image
        password="example",
        port="5432"  # explicitly specify the port
    )
cur = conn.cursor()


cur.execute("""
SELECT SUM(tmp_table.shares), tmp_table.cusip, ticker, security_name, tmp_table.period_of_report
FROM
( 
  SELECT shares, cusip, filings.period_of_report
  FROM holdings
  INNER JOIN filings
  ON filings.filing_id = holdings.filing_id
  WHERE (filings.period_of_report = '2023-09-30' or filings.period_of_report = '2023-06-30') and not cusip LIKE '000%'
) tmp_table
INNER JOIN holding_infos
ON tmp_table.cusip = holding_infos.cusip
WHERE LENGTH(ticker) <= 5 and LENGTH(ticker) >= 1 and not (LENGTH(ticker)= 5 and ticker LIKE '%W')
GROUP BY tmp_table.cusip, ticker, security_name, tmp_table.period_of_report
""")
 

rows = cur.fetchall()    

cur.close()

all_holdings = pd.DataFrame(rows, columns =['Shares', 'CUSIP', 'Ticker', 'SecurityName', 'PeriodOfReport'])
all_holdings.to_csv("all_holdings.csv",index=False)



calculate_holding_changes(all_holdings)