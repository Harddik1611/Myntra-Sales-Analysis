import pandas as pd

def load_data(data):
    """Load dataset from a excel file."""
    return pd.read_excel(data)

if __name__ == "__main__":
    df = load_data("data\Online Retail.xlsx")
    print("Data Loaded Successfully! ✅")