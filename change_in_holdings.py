from datetime import datetime
import pandas as pd
import numpy as np
def calculate_holding_changes(df):
    from datetime import datetime
    import pandas as pd

    # Define the dates for comparison
    date_2023_09_30 = datetime.strptime('2023-09-30', '%Y-%m-%d').date()
    date_2023_06_30 = datetime.strptime('2023-06-30', '%Y-%m-%d').date()
    holding_changes = []  # Initialize an empty list to store holding changes

    # Filter the dataset for holdings with the 'PeriodOfReport' = 2023-09-30
    subset = df[df['PeriodOfReport'] == date_2023_09_30]

    # Create a mask to select holdings for the 2023-06-30 period
    mask_1 = df['PeriodOfReport'] == date_2023_06_30

    for index, holding_2023_09_30 in subset.iterrows():
        # Create a mask to select holdings with the same 'CUSIP'
        mask_2 = df['CUSIP'] == holding_2023_09_30['CUSIP']

        # Merge the masks to get the holdings for the 2023-06-30 period
        holdings_2023_06_30 = df[(mask_1 & mask_2)]

        if len(holdings_2023_06_30) != 0:
            # If the holding existed in the 2023-06-30 filing
            holding_2023_06_30 = holdings_2023_06_30.iloc[0]

            share_delta_absolute = holding_2023_09_30['Shares'] - holding_2023_06_30['Shares']
            # Check if `holding_2023_06_30['Shares']` is non-zero to avoid division errors
            if holding_2023_06_30['Shares'] != 0:
                share_delta_relative = (share_delta_absolute / holding_2023_06_30['Shares']) * 100
            else:
                share_delta_relative = float('inf')  # Handle division by zero case
            shares_2023_09_30 = holding_2023_09_30['Shares']
            shares_2023_06_30 = holding_2023_06_30['Shares']

        else:
            # If the holding didn't exist in the 2023-06-30 filing
            share_delta_absolute = holding_2023_09_30['Shares']
            share_delta_relative = 100  # Assume 100% change for new holdings
            shares_2023_09_30 = holding_2023_09_30['Shares']
            shares_2023_06_30 = 0

        # Append the result as a tuple to the list
        holding_changes.append((holding_2023_09_30['CUSIP'], 
                                holding_2023_09_30['Ticker'], 
                                holding_2023_09_30['SecurityName'], 
                                shares_2023_06_30,
                                shares_2023_09_30,
                                share_delta_absolute, 
                                share_delta_relative))

    # Convert the list of tuples into a DataFrame
    holding_changes = pd.DataFrame(holding_changes, columns=['CUSIP',
                                                             'Ticker',
                                                             'SecurityName',
                                                             'Shares2023_06_30',
                                                             'Shares2023_09_30',
                                                             'DeltaAbsolute', 
                                                             'DeltaRelative'])
    
    # Save the DataFrame to a CSV file
    holding_changes.to_csv('holding_changes.csv', index=False)
    print("CSV file 'holding_changes.csv' has been generated.")
    return holding_changes

