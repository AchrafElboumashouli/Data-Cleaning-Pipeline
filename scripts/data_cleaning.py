
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
import os


def load_data(path: str) -> pd.DataFrame:
    """Load dataset from a CSV file."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ File not found: {path}")
    print("📂 Loading data...")
    df = pd.read_csv(path, low_memory=False)
    print(f"✅ Data loaded successfully! Shape: {df.shape}")
    return df


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Handle missing values for numeric and categorical columns."""
    print("🧩 Handling missing values...")
    df.columns = df.columns.str.strip()
    df = df.dropna(axis=1, how='all')
    
    # Identify numeric columns
    potential_num_cols = ['RATING', 'VOTES', 'RunTime', 'Gross']
    num_cols = [col for col in potential_num_cols if col in df.columns]
    
    # Identify categorical columns
    cat_cols = ['MOVIES', 'YEAR', 'GENRE', 'ONE-LINE', 'STARS']
    cat_cols = [col for col in cat_cols if col in df.columns]
    
    for col in num_cols:
        if col in df.columns:
            if col == 'VOTES':
                df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce')
            else:
                df[col] = pd.to_numeric(df[col], errors='coerce')
    
    for col in num_cols:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].median())
    
    for col in cat_cols:
        if col in df.columns:
            if df[col].isna().all():
                df[col] = 'Unknown'
            else:
                df[col] = df[col].fillna('Unknown')
    
    print("✅ Missing values handled.")
    return df


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Remove duplicate rows."""
    print("🔁 Removing duplicates...")
    before = df.shape[0]
    df = df.drop_duplicates()
    after = df.shape[0]
    print(f"✅ Removed {before - after} duplicate rows.")
    return df


def remove_outliers(df: pd.DataFrame) -> pd.DataFrame:
    """Detect and remove outliers using IQR for numeric columns only."""
    print("📉 Removing outliers...")
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    before = df.shape[0]
    
    if len(numeric_cols) > 0:
        mask = pd.Series([True] * len(df))
        
        for col in numeric_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            
            if IQR > 0:
                col_mask = (df[col] >= Q1 - 1.5 * IQR) & (df[col] <= Q3 + 1.5 * IQR)
                mask = mask & col_mask
        
        df = df[mask]
    
    print(f"✅ Removed {before - df.shape[0]} outlier rows.")
    return df


def extract_year_info(df: pd.DataFrame) -> pd.DataFrame:
    """Extract and clean year information from YEAR column."""
    print("📅 Processing year information...")
    
    if 'YEAR' in df.columns:
        df['YEAR_CLEANED'] = df['YEAR'].astype(str).str.extract(r'(\d{4})')
        df['YEAR_CLEANED'] = pd.to_numeric(df['YEAR_CLEANED'], errors='coerce')
        
        missing_years = df['YEAR_CLEANED'].isna()
        if missing_years.any():
            df.loc[missing_years, 'YEAR_CLEANED'] = df.loc[missing_years, 'MOVIES'].astype(str).str.extract(r'\((\d{4})')
            df['YEAR_CLEANED'] = pd.to_numeric(df['YEAR_CLEANED'], errors='coerce')
    
    print("✅ Year information processed.")
    return df


def encode_categorical(df: pd.DataFrame) -> pd.DataFrame:
    """Encode categorical columns using LabelEncoder."""
    print("🔠 Encoding categorical features...")
    
    cat_cols = df.select_dtypes(exclude=[np.number]).columns
    cat_cols = [col for col in cat_cols if col not in ['MOVIES']]
    
    le = LabelEncoder()
    for col in cat_cols:
        if df[col].nunique() > 1:
            df[col] = le.fit_transform(df[col].astype(str))
        else:
            df = df.drop(columns=[col])
    
    print("✅ Encoding completed.")
    return df


def scale_features(df: pd.DataFrame) -> pd.DataFrame:
    """Scale numeric features using StandardScaler."""
    print("📏 Scaling numeric features...")
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    cols_to_scale = [col for col in numeric_cols if not col.endswith('_ENCODED')]
    
    if len(cols_to_scale) > 0:
        scaler = StandardScaler()
        df[cols_to_scale] = scaler.fit_transform(df[cols_to_scale])
    
    print("✅ Scaling done.")
    return df


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and standardize column names."""
    print("🔄 Cleaning column names...")
    
    df.columns = (df.columns
                  .str.strip()
                  .str.upper()
                  .str.replace(' ', '_')
                  .str.replace('-', '_')
                  .str.replace(r'[^\w_]', '', regex=True))
    
    print("✅ Column names cleaned.")
    return df


def save_cleaned_data(df: pd.DataFrame, output_path: str):
    """Save cleaned DataFrame to CSV."""
    df.to_csv(output_path, index=False)
    print(f"💾 Cleaned data saved to {output_path}")

# Main execution flow
def main():
    print("🚀 Starting Data Cleaning Pipeline...")
    input_path = "movies.csv"
    output_path = "cleaned_movies_data.csv"

    try:
        df = load_data(input_path)
        df = clean_column_names(df)
        df = handle_missing_values(df)
        df = extract_year_info(df)
        df = remove_duplicates(df)
        df = remove_outliers(df)
        df = encode_categorical(df)
        df = scale_features(df)
        save_cleaned_data(df, output_path)
        
        print(f"🏁 Data cleaning completed successfully!")
        print(f"📊 Final dataset shape: {df.shape}")
        print(f"📋 Columns: {list(df.columns)}")
        
    except Exception as e:
        print(f"❌ Error during data cleaning: {e}")
        raise


if __name__ == "__main__":
    main()
