from src.data_loader import load_data
from src.data_cleaning import clean_data, remove_outliers
from src.feature_engineering import create_rfm_features

def main():
    """Execute full data pipeline."""
    print("🔹 Loading data...")
    df = load_data("data\Online Retail.xlsx")

    print("🔹 Cleaning data...")
    df = clean_data(df)
    df = remove_outliers(df, ["Total_Sales", "Recency", "Frequency"])

    print("🔹 Creating features...")
    rfm = create_rfm_features(df)

    print("🔹 Saving processed data...")
    rfm.to_csv("data/processed_data.csv", index=True)
    print("✅ Data processing completed!")

if __name__ == "__main__":
    main()
