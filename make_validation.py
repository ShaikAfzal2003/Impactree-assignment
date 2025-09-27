import pandas as pd
df = pd.read_csv("dataset.csv")
df.to_csv("validation.csv", index=False)
print("validation.csv created with", len(df), "rows")
