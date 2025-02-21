import sys
import pandas as pd

if len(sys.argv) < 2:
    print("Usage: python coverage.py <output_req> <output_selenium>")
    sys.exit(1)

output_req = sys.argv[1]
output_selnium = sys.argv[2]

print(f"Argument [output_req]: {output_req}")
print(f"Argument [output_selnium]: {output_selnium}")

df_req = pd.read_csv(output_req)
df_selenium = pd.read_csv(output_selnium)

df_req.replace('', pd.NA, inplace=True)
df_selenium.replace('', pd.NA, inplace=True)

empty_df_req = df_req.isna().sum()
num_rows_df_req = df_req.shape[0]
average_non_empty_df_req = (1 - (empty_df_req / num_rows_df_req))
print("Coverage for Request APPROACH:\n", average_non_empty_df_req)

empty_df_selenium = df_selenium.isna().sum()
num_rows_df_selenium = df_selenium.shape[0]
average_non_empty_df_selenium= (1 - (empty_df_selenium / num_rows_df_selenium))
print("Coverage for Selenium APPROACH:\n", average_non_empty_df_selenium)
