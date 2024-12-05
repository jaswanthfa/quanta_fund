import pandas as pd
import numpy as np
holding_changes=pd.read_csv("holding_changes.csv")
mask_1 = holding_changes['DeltaRelative'] > 0
mask_2 = holding_changes['DeltaRelative'] != np.inf

bought_all = holding_changes[(mask_1 & mask_2)].sort_values(by=['DeltaRelative'], ascending=False)

top_100_bought = bought_all[bought_all['Shares2023_06_30'] > 500000][:100].reset_index()
top_100_bought.to_csv("top_100_holdings.csv",index=False)