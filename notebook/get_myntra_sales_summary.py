import pandas as pd
import sqlite3
import logging
import time

# Setup Logging
logging.basicConfig(
    filename="logs/get_sales_summary.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S',
    filemode="a"
)

def ingest_db(df, table_name, engine):
    '''Ingests the DataFrame into SQLite DB'''
    df.to_sql(table_name, con=engine, if_exists='replace', index=False)
    logging.info(f"Data ingested to table '{table_name}' successfully.")

def create_myntra_sales_summary(conn):
    '''Creates a summary DataFrame from raw table'''
    query = '''
        SELECT 
            InvoiceNo,
            StockCode,
            Description,
            Quantity,
            InvoiceDate,
            UnitPrice,
            CustomerID,
            Country,
            SUM(Quantity) AS Total_Quantity,
            SUM(UnitPrice) AS Total_UnitPrice,
            SUM(Quantity * UnitPrice) AS Total_Revenue
        FROM "Online_Retail.csv"
        WHERE Quantity > 0 AND UnitPrice > 0 AND CustomerID IS NOT NULL
        GROUP BY InvoiceNo, StockCode, Description, CustomerID, Country
        ORDER BY Total_Revenue 
    '''
    return pd.read_sql_query(query, conn)

def clean_data(df):
    '''Cleans and enriches the sales DataFrame'''
    # extracted new date attributes from 'InvoiceDate'
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    df['Quantity']=pd.to_numeric(df['Quantity'])
    df['CustomerID'] = df['CustomerID'].astype(str)

    df['Year'] = df['InvoiceDate'].dt.year.astype('object')
    df['Month'] = df['InvoiceDate'].dt.month.astype('object')
    df['Quarter'] = df['InvoiceDate'].dt.quarter.astype("object")
    df['Weekend'] = df['InvoiceDate'].dt.weekday.astype("object")
    df['InvoiceHour'] = df['InvoiceDate'].dt.hour
    df['DayOfWeek'] = df['InvoiceDate'].dt.dayofweek.astype('object')
    df['IsWeekend'] = df['DayOfWeek'].isin([5, 6])

    df['PartOfDay'] = pd.cut(
        df['InvoiceHour'],
        bins=[0, 6, 8, 12, 24],
        labels=['Night', 'Morning', 'Afternoon', 'Evening'],
        right=False,
        include_lowest=True
    )

    # created new column for better analysis
    df['Avg_Price_Per_Item'] = df['Total_Revenue'] / df['Total_Quantity']
    df['Items_Per_Invoice'] = df.groupby('InvoiceNo')['Quantity'].transform('sum')

    return df

if __name__ == '__main__':
    try:
        conn = sqlite3.connect('myntra_sales.db')

        logging.info('Creating Myntra Sales Summary...')
        summary_df = create_myntra_sales_summary(conn)
        logging.info("Summary Data Preview:\n" + summary_df.head().to_string(index=False))

        logging.info('Cleaning Data...')
        clean_df = clean_data(summary_df)
        logging.info("Cleaned Data Preview:\n" + clean_df.head().to_string(index=False))

        logging.info('Ingesting Cleaned Data into DB...')
        ingest_db(clean_df, 'vendor_sales_summary', conn)

        logging.info('Process Completed Successfully.')

    except Exception as e:
        logging.exception("Error occurred: %s", str(e))
    finally:
        conn.close()
