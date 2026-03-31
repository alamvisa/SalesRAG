import pandas as pd
from pathlib import Path
from app.core.config.settings import config
import numpy as np
import json
import calendar

def nlp(df):
    df["description"] = df.apply(
        lambda row: f'On {row["Order Date"]}, {row["Segment"]} {row["Customer Name"]} from {row["City"]}, {row["Country"]} ordered {row["Quantity"]} {row["Product Name"]} item{"s" if row["Quantity"]>1 else ""} for ${row["Sales"]:.2f} with a {row["Discount"]} discount yielding a profit of {row["Profit"]}. The order was shipped on {row["Ship Date"]} via {row["Ship Mode"]}. Category of the item is {row["Category"]} and sub-category {row["Sub-Category"]}',
        axis=1
    )
    return df

def agg(df, keys, fr=None):
    if isinstance(keys, str):
        keys = [keys]

    if fr:
        grouper = [pd.Grouper(key=keys[0], freq=fr)] + keys[1:]
    else:
        grouper = keys

    data = df.groupby(grouper).agg(
        Sales_sum=("Sales", "sum"),
        Profit_sum=("Profit", "sum"),
        Quantity_sum=("Quantity", "sum"),
        Avg_Sale=("Sales", "mean"),
        Avg_Profit=("Profit", "mean"),
        Unique_customers=("Customer ID", "nunique"),
        Top_item=("Product Name", lambda x: x.value_counts().idxmax()),
        Avg_Discount=("Discount", "mean"),
        Discounted_rate=("Discount", lambda x: (x > 0).mean())
    )

    if fr is not None:
        f = fr[0] if len(fr) > 1 else fr
        if len(keys) > 1:
            data.index = data.index.set_levels(
                data.index.levels[0].to_period(f), level=0
            )
        else:
            data.index = data.index.to_period(f)

    return data



def aggregate_by_month(df):
    return agg(df, "Order Date", "ME")

def aggregate_by_quarter(df):
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

def aggregate_by_region(df):
    return agg(df, "Region")

def aggregate_by_product(df):
    return agg(df, "Product Name")

def aggregate_by_month_x_category(df):
    return agg(df, ["Order Date", "Category"], "ME")

def aggregate_by_year_x_category(df):
    return agg(df, ["Order Date", "Category"], "YE")

def aggregate_by_state_x_category(df):
    return agg(df, ["State", "Category"])

def aggregate_by_month_of_year(df):
    df = df.copy()
    df["Month"] = df["Order Date"].dt.month
    return agg(df, "Month")

def aggregate_by_region_x_year(df):
    return agg(df, ["Order Date", "Region"], "YE")


def report(tables, r_table):
    map = {
        'agg_month': ['month', 'months'],
        'agg_quarter': ['quarter', 'quarters'],
        'agg_year': ['year', 'years'],
        'agg_item_category': ['category', 'categories'], 
        'agg_item_sub_category': ['sub-category', 'sub-categories'],
        'agg_city': ['city', 'cities'], 
        'agg_state': ['state', 'states'],
        'agg_region': ['region', 'regions'],
        'agg_product': ['product', 'products'],
        'agg_month_x_category': ['month within the category', 'month-category combinations'],
        'agg_year_x_category':  ['year within the category', 'year-category combinations'],
        'agg_state_x_category': ['state within the category', 'state-category combinations'],
        'agg_month_of_year': ['seasonal month', 'seasonal months'],
        'agg_region_x_year': ['region for a year', 'region-year combinations'],
    }
    style = map[r_table]
    table = tables[r_table]

    mean = table["Sales_sum"].mean()
    top = table["Sales_sum"].quantile(0.90)
    low = table["Sales_sum"].quantile(0.10)


    def label_sales(x):
        if x > top: return f"one of the strongest performing sales"
        if x > mean: return f"an above-average performing sales"
        if x > low: return f"a below-average performing sales"
        return f"one of the weakest performing sales"

    def label_margin(x, y):
        if y == 0: return f"unprofitable"
        if x/y > 0.2: return f'very profitable'
        if x/y > 0.1: return f'moderately profitable'
        if x/y > 0: return f'barely profitable'
        return f'unprofitable'
    
    def label_start(x):
        s = style[0]
        if s == "month": return f'Sales report for month {x[0].strftime("%B %Y")}: In {x[0].strftime("%B %Y")},'
        if s == "quarter": return f'Sales report for quarter Q{x[0].quarter} {x[0].year}: In Q{x[0].quarter} {x[0].year},'
        if s == "year": return f'Annual sales report for year {x[0].year}: In {x[0].year},'
        if s == "city": return f'City sales data for {x[0]}: In the city of {x[0]}'
        if s == "state": return f'State sales data for {x[0]}: The state of {x[0]}'
        if s == "region": return f'Regional sales data for {x[0]}: The {x[0]} region'
        if s == "category": return f'Product category report for {x[0]}: The {x[0]} category'
        if s == "sub-category": return f'Product sub-category report for {x[0]}: The {x[0]} sub-category'
        if s == "product": return f'Sales data for product {x[0]}: {x[0]}'
        if s == "month within the category": return f'Sales report for {x[1]} in {x[0].strftime("%B %Y")}: In {x[0].strftime("%B %Y")}, the {x[1]} category'
        if s == "year within the category": return f'Sales report for {x[1]} in {x[0].year}: In {x[0].year}, the {x[1]} category'
        if s == "state within the category": return f'Sales report for {x[1]} in {x[0]}: In {x[0]}, the {x[1]} category'
        if s == "seasonal month": return f'Seasonal sales data for {calendar.month_name[x[0]]}: Across all years, {calendar.month_name[x[0]]}'
        if s == "region for a year": return f'Sales report for the {x[1]} region in {x[0].year}: In {x[0].year}, the {x[1]} region'
        return ""
        
    def label_item(x):
        return f'the most sold product was {x["Top_item"]}'
        
    def compare_previous(x, previous):
        if style[0] in ['month', 'year', 'quarter'] and previous is not None:
            if x > (1 + 0.1 * np.sign(previous)) * previous:
                rep = 'strong growth'
            elif x > previous:
                rep = 'weak growth'
            else:
                rep = 'shrinkage'
            return f' and compared to the last period, there was {rep}'
        return ""
    
    def create_metadata(idx, row):
        base = {
            "type": style[0],
            "sales": float(row["Sales_sum"]),
            "profits": float(row["Profit_sum"]),
            "quantity": int(row["Quantity_sum"]),
            "margin": round(float(row["Profit_sum"]) / float(row["Sales_sum"]), 4) if row["Sales_sum"] else 0.0,
            "discount_rate": round(float(row["Discounted_rate"]), 4)
        }

        field_map = {
            "month":                  lambda i: {"month": int(i[0].month), "year": int(i[0].year)},
            "quarter":                lambda i: {"quarter": int(i[0].quarter), "year": int(i[0].year)},
            "year":                   lambda i: {"year": int(str(i[0]))},
            "category":               lambda i: {"category": str(i[0])},
            "sub-category":           lambda i: {"sub-category": str(i[0])},
            "city":                   lambda i: {"city": str(i[0])},
            "state":                  lambda i: {"state": str(i[0])},
            "region":                 lambda i: {"region": str(i[0])},
            "product":                lambda i: {"product": str(i[0])},
            "month within the category":  lambda i: {"month": int(i[0].month), "year": int(i[0].year), "category": str(i[1])},
            "year within the category":   lambda i: {"year": int(str(i[0])), "category": str(i[1])},
            "state within the category":  lambda i: {"state": str(i[0]), "category": str(i[1])},
            "seasonal month":         lambda i: {"month": int(i[0])},
            "region for a year":      lambda i: {"region": str(i[1]), "year": int(str(i[0]))},
        }

        base.update(field_map[style[0]](idx))
        return base

    previous = None
    formats = []
    for idx, row in table.iterrows():
        idx_tuple = idx if isinstance(idx, tuple) else (idx,)
        margin_str = f'{row["Profit_sum"]/row["Sales_sum"]:.1%}'
        if style[0] == "product":
            verb = "is"
        else:
            verb = f'{label_item(row)} and was'
        chunk = f"{label_start(idx_tuple)} {verb} overall {label_margin(row['Profit_sum'], row['Sales_sum'])} {style[0]} with a margin of {margin_str} while having {label_sales(row['Sales_sum'])} among all {style[1]}. The total sales were ${row['Sales_sum']:.2f}{compare_previous(row['Sales_sum'], previous)}. Additionally the average discount given was {row['Avg_Discount']:.1%} ({row['Discounted_rate']:.1%} of orders were discounted)."
        previous = row['Sales_sum']

        formatted = {
            "text": chunk,
            "metadata": create_metadata(idx_tuple, row)
        }
        formats.append(formatted)
    
    (config.DATA_PROCESSED_DIR / "documents").mkdir(parents=True, exist_ok=True)
    with open((config.DATA_PROCESSED_DIR / "documents") / (r_table + "_document.jsonl"), "w") as f:
        for formatted in formats:
            f.write(json.dumps(formatted) + "\n")

def process(file_name):
    path = config.DATA_RAW_DIR / file_name
    df = pd.read_csv(path, encoding="cp1252")
    df["Order Date"] = pd.to_datetime(df["Order Date"], format='%m/%d/%Y')
    df["Ship Date"] = pd.to_datetime(df["Ship Date"], format='%m/%d/%Y')
    
    # Creating aggregate tables
    aggregate_tables = {
        'agg_month': aggregate_by_month(df),
        'agg_quarter': aggregate_by_quarter(df),
        'agg_year': aggregate_by_year(df),
        'agg_item_category': aggregate_by_category(df),
        'agg_item_sub_category': aggregate_by_sub_category(df),
        'agg_city': aggregate_by_city(df),
        'agg_state': aggregate_by_state(df),
        'agg_region': aggregate_by_region(df),
        'agg_product': aggregate_by_product(df),
        'agg_month_x_category': aggregate_by_month_x_category(df),
        'agg_year_x_category': aggregate_by_year_x_category(df),
        'agg_state_x_category': aggregate_by_state_x_category(df),
        'agg_month_of_year': aggregate_by_month_of_year(df),
        'agg_region_x_year': aggregate_by_region_x_year(df)
    }

    # other useful: spent per customer, customers vs companies 
    # Creating summaries text documents
    for table_name, _ in aggregate_tables.items():
        report(aggregate_tables, table_name)
        
    # Format datetimes correclt and produce natural languaged representation
    df["Order Date"] = df["Order Date"].dt.strftime('%Y-%m-%d')
    df["Ship Date"] = df["Ship Date"].dt.strftime('%Y-%m-%d')
    df = nlp(df)

    df.to_csv(config.DATA_PROCESSED_DIR / "processed_superstore.csv", index=False)


