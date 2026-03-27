import pandas as pd
from pathlib import Path
from app.core.config.settings import config

def nlp(df):
    df["description"] = df.apply(
        lambda row: f'On {row["Order Date"]}, {row["Segment"]} {row["Customer Name"]} from {row["City"]}, {row["Country"]} ordered {row["Quantity"]} {row["Product Name"]} item{"s" if row["Quantity"]>1 else ""} for ${row["Sales"]:.2f} with a {row["Discount"]} discount yielding a profit of {row["Profit"]}. The order was shipped on {row["Ship Date"]} via {row["Ship Mode"]}. Category of the item is {row["Category"]} and sub-category {row["Sub-Category"]}',
        axis=1
    )
    return df

def agg(df, key, fr = None):
    if fr:
        d = df.groupby(pd.Grouper(key=key, freq=fr))
    else:
        d = df.groupby(pd.Grouper(key=key))
    
    data = d.agg(
        Sales_sum=("Sales", "sum"),
        Profit_sum=("Profit", "sum"),
        Quantity_sum=("Quantity", "sum"),
        Avg_Sale=("Sales", "mean"),
        Avg_Profit=("Profit", "mean"),
        Unique_customers=("Customer ID", "nunique")
    )
    if fr is not None:
        f = fr
        if len(fr) > 1:
            f = fr[0]   
        data.index = data.index.to_period(f)
    return data

def aggregate_by_month(df):
    return agg(df, "Order Date", "ME")

def aggregate_by_quater(df):
    return agg(df, "Order Date", "QE")

def aggregate_by_year(df):
    return agg(df, "Order Date", "YE")

def aggregate_by_category(df):
    return agg(df, "Category")

def aggregate_by_sub_category(df):
    return agg(df, "Sub-Category")

def aggregate_by_city(df):
    return agg(df, "City")

def aggregate_by_state(df):
    return agg(df, "State")

def report(tables, r_table):
    if r_table == 'agg_month': style = "month"
    if r_table == 'agg_quater': style = "quater"
    if r_table == 'agg_year': style = "year"
    if r_table == 'agg_item_category': style = "item category"
    if r_table == 'agg_item_sub_category': style = "item sub category"
    if r_table == 'agg_city': style = "city"
    if r_table == 'agg_state': style = "state"
    table = tables[r_table]

    mean = table["Sales_sum"].mean()
    top = table["Sales"].quantile(0.90)
    low = table["Sales"].quantile(0.10)

    margin = table['Profit_sum']/table['Sales_sum']

    def label_sales(x):
        if x > top: return f"Sales performance of this {style} was one of the strongest"
        if x > mean: return f"Sales performance of this {style} was above average"
        if x > low: return f"Sales performance of this {style} was below average"
        return f"Sales performance of this {style} was one of the weakest"

    def label_margin(x, y):
        if x/y > 0.2: return 'high profitability'
        if x/y > 0.1: return 'modest profitability'
        if x/y > 0: return 'barely positive profitability'
        return 'negative profitability'
    


def process(file_name):
    path = config.DATA_RAW_DIR / file_name
    df = pd.read_csv(path, encoding="cp1252")
    df["Order Date"] = pd.to_datetime(df["Order Date"], format='%m/%d/%Y')
    df["Ship Date"] = pd.to_datetime(df["Ship Date"], format='%m/%d/%Y')
    
    # Creating aggregate tables
    aggregate_tables = {
        'agg_month': aggregate_by_month(df),
        'agg_quater': aggregate_by_quater(df),
        'agg_year': aggregate_by_year(df),
        'agg_item_category': aggregate_by_category(df),
        'agg_item_sub_category': aggregate_by_sub_category(df),
        'agg_city': aggregate_by_city(df),
        'agg_state': aggregate_by_state(df)
    }

    # other useful: spent per customer, customers vs companies 
    # Creating summaries text documents
    for table_name, _ in aggregate_tables.items():
        report(aggregate_tables, table_name)

    # Format datetimes correclt and produce natural languaged representation
    df["Order Date"] = df["Order Date"].dt.strftime('%Y-%m-%d')
    df["Ship Date"] = df["Ship Date"].dt.strftime('%Y-%m-%d')
    df = nlp(df)


