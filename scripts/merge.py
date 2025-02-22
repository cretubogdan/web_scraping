import sys
import pandas as pd

if len(sys.argv) < 3:
    print("Usage: python merge.py <crawled_dataset> <websites-company-names> <output>")
    sys.exit(1)

output_dataset = sys.argv[1]
to_add = sys.argv[2]
output = sys.argv[3]

print(f"Argument [output_dataset]: {output_dataset}")
print(f"Argument [websites-company-names]: {to_add}")

df = pd.read_csv(output_dataset)
df_to_add = pd.read_csv(to_add)

merged_df = pd.merge(df_to_add, df, on=df_to_add.columns[0], how='left')

merged_df = merged_df.fillna('')
merged_df.to_csv(output, index=False)
