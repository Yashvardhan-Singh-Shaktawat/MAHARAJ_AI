import pandas as pd
import os

# --- CONFIGURATION ---
EXISTING_FILE = 'world_recipes.csv'
NEW_FILE = 'diet_planner_205.csv'

print("--- 🚀 SCRIPT STARTED: MERGING DIET DATA ---")

# 1. Check if files exist
if os.path.exists(EXISTING_FILE) and os.path.exists(NEW_FILE):
    print(f"✅ Found files:\n   - {EXISTING_FILE}\n   - {NEW_FILE}")
    
    # 2. Load Dataframes
    df_main = pd.read_csv(EXISTING_FILE)
    df_new = pd.read_csv(NEW_FILE)
    
    print(f"📊 Original Recipe Count: {len(df_main)}")
    print(f"📊 New Diet Recipes to Add: {len(df_new)}")

    # 3. Generate New IDs
    # Start IDs from where the main file ends to prevent conflicts
    if not df_main.empty:
        start_id = df_main['recipe_id'].max() + 1
    else:
        start_id = 1
        
    df_new['recipe_id'] = range(int(start_id), int(start_id) + len(df_new))

    # 4. Align Columns (Prevent Crashes)
    # Ensure the new data has every column the main file has
    for col in df_main.columns:
        if col not in df_new.columns:
            # Fill missing columns with defaults
            if 'g' in col or 'mg' in col or 'cal' in col:
                df_new[col] = 0
            else:
                df_new[col] = "Global"
    
    # 5. Merge Data
    combined_df = pd.concat([df_main, df_new], ignore_index=True)
    
    # 6. Save back to the main file
    combined_df.to_csv(EXISTING_FILE, index=False)
    
    print("\n" + "="*40)
    print(f"🎉 SUCCESS! Data Merged.")
    print(f"📈 Total Recipes in Database: {len(combined_df)}")
    print("👉 ACTION: Please restart your Django server now.")
    print("="*40 + "\n")

else:
    print("\n❌ ERROR: FILES NOT FOUND!")
    print(f"Checked folder: {os.getcwd()}")
    print(f"Looking for: {EXISTING_FILE} (Found? {os.path.exists(EXISTING_FILE)})")
    print(f"Looking for: {NEW_FILE} (Found? {os.path.exists(NEW_FILE)})")
    print("👉 Please make sure 'diet_planner_205.csv' is inside the 'recommendations/data/' folder.")