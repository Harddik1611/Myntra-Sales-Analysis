import pandas as pd

def create_rfm_features(df):
    """Create RFM (Recency, Frequency, Monetary) features."""
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    reference_date = df["InvoiceDate"].max()

    rfm = df.groupby("CustomerID").agg({
        "InvoiceDate": lambda x: (reference_date - x.max()).days,  # Recency
        "InvoiceNo": "count",  # Frequency
        "Total_Sales": "sum"  # Monetary
    }).rename(columns={"InvoiceDate": "Recency", "InvoiceNo": "Frequency", "Total_Sales": "Monetary"})

    return rfm

if __name__ == "__main__":
    df = pd.read_excel("data\Online Retail.xlsx",engine='openpyxl')
    rfm = create_rfm_features(df)
    print("Feature Engineering Completed! ✅")
