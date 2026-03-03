import pandas as pd
import glob
import os
import logging

# --- 1. SETUP LOGGING ---
# This creates a file named 'etl_log.txt' to record what happens
logging.basicConfig(
    filename='etl_log.txt', 
    level=logging.INFO, 
    format='%(asctime)s - %(message)s'
)

print("Starting ETL Process...")
logging.info("--- ETL JOB STARTED ---")

try:
    # --- 2. EXTRACT (Read Data) ---
    # We use a list to hold data from different files before combining them
    all_data_frames = []
    
    # Get a list of all files in the 'input_data' folder
    # We look for files ending in .csv OR .json
    files = glob.glob("input_data/*")
    
    print(f"Found {len(files)} files to process.")

    for file in files:
        # Check if it is a CSV file
        if file.endswith(".csv"):
            print(f"Reading CSV file: {file}")
            df = pd.read_csv(file)
            all_data_frames.append(df)
            logging.info(f"Successfully read CSV: {file}")

        # Check if it is a JSON file
        elif file.endswith(".json"):
            print(f"Reading JSON file: {file}")
            df = pd.read_json(file)
            all_data_frames.append(df)
            logging.info(f"Successfully read JSON: {file}")

    # Combine all the little dataframes into one big dataframe
    if len(all_data_frames) > 0:
        combined_df = pd.concat(all_data_frames, ignore_index=True)
        print("Data extraction successful.")
    else:
        raise ValueError("No valid CSV or JSON files found in 'input_data/'")


    # --- 3. TRANSFORM (Clean Data) ---
    print("Starting data cleaning...")

    # A. Fix the product names (Make them Title Case: 'mouse' -> 'Mouse')
    combined_df['product'] = combined_df['product'].str.title()

    # B. Handle missing Price (Drop rows where price is missing)
    # We can't sell something if we don't know the price!
    if combined_df['price'].isnull().sum() > 0:
        rows_before = len(combined_df)
        combined_df.dropna(subset=['price'], inplace=True)
        rows_after = len(combined_df)
        print(f"Dropped {rows_before - rows_after} rows with missing prices.")
        logging.warning(f"Dropped {rows_before - rows_after} rows due to missing price.")

    # C. Handle missing Quantity (Fill empty spots with 0)
    combined_df['quantity'] = combined_df['quantity'].fillna(0)

    # D. Create a new column: Total Value
    combined_df['total_value'] = combined_df['quantity'] * combined_df['price']

    # E. Remove duplicates (if the exact same row exists twice)
    combined_df.drop_duplicates(inplace=True)

    print("Data transformation complete.")
    logging.info("Data transformation complete.")


    # --- 4. LOAD (Save Data) ---
    
    # Check if 'output_data' folder exists, if not, create it
    if not os.path.exists("output_data"):
        os.makedirs("output_data")

    # Save to CSV
    output_file = "output_data/clean_data.csv"
    combined_df.to_csv(output_file, index=False)

    print(f"SUCCESS: Data saved to {output_file}")
    logging.info(f"--- JOB FINISHED SUCCESS: Saved to {output_file} ---")

except Exception as e:
    # If anything crashes, this block runs
    print(f"ERROR: Something went wrong: {e}")
    logging.error(f"ETL Failed: {e}")