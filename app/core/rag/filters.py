import re
from app.core.config.logging import logger

REGIONS   = {"east", "west", "central", "south"}
CATEGORIES = {"furniture", "technology", "office supplies"}
MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12
}
METRIC_KEYWORDS = {
    "sales":         ["sales", "revenue", "income", "earning", "turnover"],
    # "profits":       ["profit", "profitable", "profitability", "gain", "earning"],
    # "margin":        ["margin", "efficiency", "markup"],
    # "quantity":      ["quantity", "units", "volume", "ordered", "popular", "demand"],
    # "discount_rate": ["discount", "discounted", "markdown", "reduced"],
}
DESC_KEYWORDS = ["best", "top", "highest", "most", "greatest", "leading", "largest", "performance", "frequently", "often"]
ASC_KEYWORDS  = ["worst", "lowest", "least", "bottom", "weakest", "smallest", "poorest", "rarely"]


def get_filters(query):
    q = query.lower()
    conditions = []

    # Year
    years = re.findall(r'\b(201[4-7])\b', q)
    if years:
        if len(years) == 1:
            conditions.append({"year": {"$eq": int(years[0])}})
        else:
            conditions.append({"year": {"$in": [int(y) for y in years]}})

    # Month
    for name, num in MONTHS.items():
        if name in q:
            conditions.append({"month": {"$eq": num}})
            break

    # Region
    matched_regions = [
        region.title() for region in REGIONS
        if re.search(rf'\b{re.escape(region)}\b', q)
    ]
    if matched_regions:
        if len(matched_regions) == 1:
            conditions.append({"region": {"$eq": matched_regions[0]}})
        else:
            conditions.append({
                "$or": [{"region": {"$eq": region}} for region in matched_regions]
            })

    # Category
    for cat in CATEGORIES:
        if cat in q:
            conditions.append({"category": {"$eq": cat.title()}})
            break

    # Metric
    found_metric = False
    for metric, keywords in METRIC_KEYWORDS.items():
        if any(kw in q for kw in keywords):
            if any(kw in q for kw in DESC_KEYWORDS):
                conditions.append({"sales_rank_desc": {"$le": 10}})
                found_metric = True
            elif any(kw in q for kw in ASC_KEYWORDS):
                conditions.append({"sales_rank_asc": {"$le": 10}})
                found_metric = True
        if found_metric:
            break

    if not conditions:
        where = None
    elif len(conditions) == 1:
        where = conditions[0]
    else:
        where = {"$and": conditions}

    logger.info({
            "filter_generation": {
                "query": query,
                "generated_filters": where
            }
        })

    return where