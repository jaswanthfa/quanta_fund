import psycopg2
from sec_api import QueryApi
from datetime import datetime, timedelta


queryApi = QueryApi(api_key="a5b85fb6bed33a7a1ec24fe6f17b982c51a382807a4fd797da380a3f1ea7f321")


conn = psycopg2.connect(host="localhost", database="postgres", user="postgres", password="example", port="5432")

def get_13f_filings(start=0, period="2024-09-30"):
    """Fetch a batch of filings from SEC API for a given period."""
    print(f"Getting next 13F batch starting at {start}, {period}")

    query = {
        "query": {
            "query_string": {
                "query": f'formType:"13F-HR" AND NOT formType:"13F-HR/A" AND periodOfReport:"{period}"'
            }
        },
        "from": start,
        "size": "50",
        "sort": [{"filedAt": {"order": "desc"}}],
    }

    response = queryApi.get_filings(query)
    return response.get("filings", [])

def save_to_db(filings):
    cur = conn.cursor()

    for idx, filing in enumerate(filings, start=1):
        print(f"Processing filing {idx}/{len(filings)}: {filing['id']}")

        if len(filing["holdings"]) == 0:
            print(f"Skipping empty filing: {filing['id']}")
            continue

        filing_id = filing["id"]

        # Check if filing_id already exists
        cur.execute("SELECT 1 FROM filings WHERE filing_id = %s", (filing_id,))
        if cur.fetchone():
            print(f"Filing already exists: {filing_id}")
            continue
            breakpoint
        # Insert filing details
        try:
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

            for holding in filing["holdings"]:
                value = holding.get("value", 0)
                shares = holding["shrsOrPrnAmt"]["sshPrnamt"]

                if value > 9223372036854775807 or shares > 9223372036854775807:
                    print(f"Skipping oversized holding: value={value}, shares={shares}")
                    continue

                holding_values = (
                    filing_id,
                    holding["nameOfIssuer"].upper(),
                    holding["cusip"],
                    holding.get("titleOfClass", ""),
                    value,
                    shares,
                    holding.get("putCall", "")
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

        except Exception as e:
            print(f"Error in filing {filing_id}: {e}")
            conn.rollback()  # Rollback if an error occurs
            continue

    cur.close()
    conn.commit()

def fill_database():
    end_date = datetime(2018,6,30)
    quarters_back = 40

    for i in range(quarters_back):
       
        period = (end_date - timedelta(days=i * 90)).strftime("%Y-%m-%d")
        start = 0  
        
        while True:
            filings = get_13f_filings(start, period)
            
            if len(filings) == 0:
                break 
            
            save_to_db(filings)
            start += 10  
    print("All filings from the past 40 quarters have been processed.")


fill_database()
