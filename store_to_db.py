import sys
import psycopg2
from sec_api import QueryApi

queryApi = QueryApi(api_key="a5b85fb6bed33a7a1ec24fe6f17b982c51a382807a4fd797da380a3f1ea7f321")

conn = psycopg2.connect(host="localhost", database="postgres", user="postgres", password="example",port="5432")

def get_13f_filings(start=0, period="2024-06-30"):
    print(f"Getting next 13F batch starting at {start}, {period}")

    query = {
        "query": {
            "query_string": {
                "query": f'formType:"13F-HR" AND NOT formType:"13F-HR/A" AND periodOfReport:"{period}"'
            }
        },
        "from": start,
        "size": "10",
        "sort": [{"filedAt": {"order": "desc"}}],
    }

    response = queryApi.get_filings(query)

    return response["filings"]
    
 
def save_to_db(filings):
    cur = conn.cursor()

    for filing in filings:
        # Skip if there are no holdings
        if len(filing["holdings"]) == 0:
            continue

        filing_id = filing["id"]  # Extract filing_id

        # Check if filing_id already exists in the filings table
        cur.execute("SELECT 1 FROM filings WHERE filing_id = %s", (filing_id,))
        if cur.fetchone():  # If the filing_id exists, skip to the next filing
            continue

        # Insert into filings table
        filing_values = (
            filing_id,
            filing["cik"],
            filing["companyName"].upper(),
            filing["periodOfReport"],
        )

        cur.execute("""
            INSERT INTO filings (
                filing_id, 
                cik, 
                filer_name, 
                period_of_report
            ) 
            VALUES (%s, %s, %s, %s)
        """, filing_values)

        # Insert holdings for the current filing
        for holding in filing["holdings"]:
            holding_values = (
                filing_id,  # Reference the filing_id
                holding["nameOfIssuer"].upper(),
                holding["cusip"],
                holding.get("titleOfClass", ""),  # Use get for optional fields
                holding["value"],
                holding["shrsOrPrnAmt"]["sshPrnamt"],
                holding.get("putCall", "")  # Use get for optional fields
            )


            cur.execute("""
                INSERT INTO holdings (
                    filing_id, 
                    name_of_issuer, 
                    cusip, 
                    title_of_class, 
                    value, 
                    shares, 
                    put_call
                ) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, holding_values)

    cur.close()
    conn.commit()
    
    
def fill_database():
    start = 0
    period = sys.argv[1]
    

    while start < 10000:
        filings = get_13f_filings(start, period)
        
        if len(filings) == 0:
            break
            
        save_to_db(filings)
        start = start + 10

    print("Done")
       

fill_database()