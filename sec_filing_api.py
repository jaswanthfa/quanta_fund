from sec_api import QueryApi
import pandas as pd

# initialize the query API
queryApi = QueryApi(api_key="d44cc5e530e1ec63a835f6531073b01ee6ba1fbdf83fc599a4f71d0d41dd2fc5")

def get_13f_filings(start=0):
    print(f"Getting next 13F batch starting at {start}")
    
    query = {
      "query": { "query_string": { 
          "query": "formType:\"13F-HR\" AND NOT formType:\"13F-HR/A\" AND periodOfReport:\"2021-06-30\"" 
        } },
      "from": start,
      "size": "10",
      "sort": [{ "filedAt": { "order": "desc" } }]
    }

    response = queryApi.get_filings(query)

    return response['filings']

# fetch the 10 most recent 13F filings
filings_batch = get_13f_filings(10)
# print(filings_batch[0]['holdings'])

# load all holdings of the first 13F filing into a pandas dataframe 
holdings_example = pd.json_normalize(filings_batch[0]['holdings'])

print(holdings_example)
    