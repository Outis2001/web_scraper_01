# import pandas as pd

# category_names = ['Advertising', 'Agriculture', 'Baby Goods', 'Banking', 'Beauty Culture', 'Computers', 'Constructions',
#                   'Education', 'Electrical', 'Embassies', 'Emergency', 'Entertainment', 'Essential Services',
#                   'Financing', 'Food', 'Government', 'Hardware', 'Health', 'Home', 'Hotels', 'Industrial', 'Insurance',
#                   'Interior', 'Media', 'Office', 'Pets', 'Professional Services', 'Religious', 'Repair',
#                   'Shopping', 'Short Codes', 'Sport', 'Telecommunication', 'Transport', 'Travel', 'Vehicle', 'Weddings']
#
# link_list = []
#
# for category in category_names:
#     link_list.extend(pd.read_csv(f"../Datasets/scraper_02/links/{category}.csv").business_link.tolist())
#
# print(f"Number of links: {len(link_list)}")
# print(f"Number of unique links: {len(set(link_list))}")
#
# new_df = pd.DataFrame(set(link_list), columns=["business_link"])
# new_df.to_csv(f"../Datasets/scraper_02/links/All_links.csv", index=False)

import pandas as pd
import glob
import os

# Path to your CSV files
folder_path = "../Datasets/scraper_02/details"  # Update this if needed

# Get all CSV files that match the pattern
csv_files = glob.glob(os.path.join(folder_path, "All_links_*.csv"))

# Filter only files with numeric ranges
def is_numeric_range_file(filename):
    basename = os.path.basename(filename)
    parts = basename.replace(".csv", "").replace("All_links_", "").split("_to_")
    return all(part.isdigit() for part in parts)

numeric_csv_files = [f for f in csv_files if is_numeric_range_file(f)]

# Sort numerically
def extract_number_start(filename):
    basename = os.path.basename(filename)
    start = basename.replace(".csv", "").replace("All_links_", "").split("_to_")[0]
    return int(start)

numeric_csv_files.sort(key=extract_number_start)

# Combine CSVs into a single DataFrame
df_combined = pd.concat((pd.read_csv(file) for file in numeric_csv_files), ignore_index=True)

final_async_file = os.path.join(folder_path, "All_links_final_async.csv")
if os.path.exists(final_async_file):
    df_final = pd.read_csv(final_async_file)
    df_combined = pd.concat([df_combined, df_final], ignore_index=True)

print(f"Combined dataframe shape: {df_combined.shape}")

# Remove duplicate rows
df_combined = df_combined.drop_duplicates()

# Optional: Reset the index after removing duplicates
df_combined.reset_index(drop=True, inplace=True)

# Print shape after removing duplicates
print(f"DataFrame shape after removing duplicates: {df_combined.shape}")

df_combined.to_csv("Rainbowpages_details.csv", index=False, header=True)

