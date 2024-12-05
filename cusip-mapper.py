import psycopg2
import requests

# connect to database
conn = psycopg2.connect(
    host="localhost", database="postgres", user="postgres", password="example",port="5432"
)

def get_all_cusips():
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT cusip FROM holdings WHERE NOT cusip LIKE '000%'")
    rows = cur.fetchall()
    return[row[0] for row in rows]



def cusip_to_query(cusip):
    return {"idType": "ID_CUSIP", "idValue": str(cusip)}





def format_response(response):
    if "data" in response and len(response["data"]) != 0:
        match = response["data"][0]
        return match["ticker"], match["name"], match["securityType"]

    return "", "", ""


def cusips_to_tickers(cusips):
    api_endpoint = "https://api.openfigi.com/v3/mapping"
    headers = {"X-OPENFIGI-APIKEY": "5b581962-aaa6-4ee3-9cfe-5309d6d897c8"}
    query = [cusip_to_query(cusip) for cusip in cusips]

    try:
        response = requests.post(api_endpoint, json=query, headers=headers)
        
        # Print status code and response text for debugging
        print("Status Code:", response.status_code)
        print("Response Text:", response.text)

        # Check for error status codes
        response.raise_for_status()

        matches = response.json()
        tmp = [format_response(match) for match in matches]
        return [(tpl[0],) + tpl[1] for tpl in list(zip(cusips, tmp))]

    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
        return []
    except ValueError as e:
        print(f"JSON Decode Error: {e}")
        return []


def insert_into_db(rows):
    cur = conn.cursor()

    insert_command = """
        INSERT INTO holding_infos (
            cusip,
            ticker,
            security_name,
            security_type
        )
        VALUES (%s, %s, %s, %s)
         """

    try:
        cur.executemany(insert_command, rows)
        cur.close()
        conn.commit()
    finally:
        conn.commit()


def run():
    cusips = get_all_cusips()

    start = 0
    stop = 100

    while start < len(cusips):
        print(start, stop)
        if stop <= len(cusips):
            cusip_batch = cusips[start:stop]
        else:
            cusip_batch = cusips[start:]

        cusips_map = cusips_to_tickers(cusip_batch)

        insert_into_db(cusips_map)

        start = start + 100
        stop = stop + 100

        if start >= len(cusips):
            break

    print("Done")



run()