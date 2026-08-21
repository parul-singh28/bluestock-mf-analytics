import pandas as pd
from pathlib import Path
root = Path('data')
paths = [root/'01_fund_master.csv', root/'02_nav_history.csv', root/'04_monthly_sip_inflows.csv', root/'07_scheme_performance.csv', root/'08_investor_transactions.csv']
for path in paths:
    df = pd.read_csv(path)
    print('\nFILE', path.name)
    print('shape', df.shape)
    print('columns', list(df.columns))
    print(df.head(2).to_string(index=False))
    print('---')
