## ------------------------------ PART:1 ----------------------------- ##
#-------- Task 1.2: Parse and Clean Data -------#

def parse_transactions(raw_lines):
    transactions = []
    if not raw_lines:
        return transactions

    header = raw_lines[0].split("|")

    for line in raw_lines[1:]:
        parts = line.split("|")

        if len(parts) != len(header):
            continue

        try:
            transaction = {
                "TransactionID": parts[0].strip(),
                "Date": parts[1].strip(),
                "ProductID": parts[2].strip(),
                "ProductName": parts[3].strip(),
                "Quantity": int(parts[4].replace(",", "").strip()),
                "UnitPrice": float(parts[5].replace(",", "").strip()),
                "CustomerID": parts[6].strip(),
                "Region": parts[7].strip(),
            }
            transactions.append(transaction)

        except ValueError:
            continue

    return transactions


#--------- Task 1.3: Data Validation and Filtering --------#

def validate_and_filter(transactions, region=None, min_amount=None, max_amount=None):
    required_fields = [
        "TransactionID", "Date", "ProductID", "ProductName",
        "Quantity", "UnitPrice", "CustomerID", "Region"
    ]

    total_input = len(transactions)
    valid = []
    invalid_count = 0

    for t in transactions:
        if any(k not in t or str(t[k]).strip() == "" for k in required_fields):
            invalid_count += 1
            continue

        if not t["TransactionID"].startswith("T"):
            invalid_count += 1
            continue
        if not t["ProductID"].startswith("P"):
            invalid_count += 1
            continue
        if not t["CustomerID"].startswith("C"):
            invalid_count += 1
            continue

        if t["Quantity"] <= 0 or t["UnitPrice"] <= 0:
            invalid_count += 1
            continue

        valid.append(t)

    filtered = valid
    filtered_by_region = 0
    filtered_by_amount = 0

    if region:
        before = len(filtered)
        filtered = [t for t in filtered if t["Region"] == region]
        filtered_by_region = before - len(filtered)

    if min_amount is not None or max_amount is not None:
        before = len(filtered)

        def in_range(t):
            amt = t["Quantity"] * t["UnitPrice"]
            if min_amount is not None and amt < min_amount:
                return False
            if max_amount is not None and amt > max_amount:
                return False
            return True

        filtered = [t for t in filtered if in_range(t)]
        filtered_by_amount = before - len(filtered)

    summary = {
        "total_input": total_input,
        "invalid": invalid_count,
        "filtered_by_region": filtered_by_region,
        "filtered_by_amount": filtered_by_amount,
        "final_count": len(filtered),
    }

    return filtered, invalid_count, summary


## ------------------------------ PART:2 ----------------------------- ##
#-----------------Task 2.1: Sales Summary Calculation------------------#

#-- a) Calculate Total Revenue
def calculate_total_revenue(transactions):
    total_revenue = 0.0
    for txn in transactions:
        total_revenue += txn["Quantity"] * txn["UnitPrice"]
    return total_revenue


#-- b) Region-wise Sales Analysis
def region_wise_sales(transactions):
    region_data = {}
    overall_total = 0.0

    for txn in transactions:
        region = txn["Region"]
        amount = txn["Quantity"] * txn["UnitPrice"]
        overall_total += amount

        if region not in region_data:
            region_data[region] = {
                "total_sales": 0.0,
                "transaction_count": 0
            }

        region_data[region]["total_sales"] += amount
        region_data[region]["transaction_count"] += 1

    for region in region_data:
        pct = (region_data[region]["total_sales"] / overall_total * 100) if overall_total else 0
        region_data[region]["percentage"] = round(pct, 2)

    return dict(sorted(region_data.items(), key=lambda x: x[1]["total_sales"], reverse=True))


#-- c) Top Selling Products
def top_selling_products(transactions, n=5):
    product_data = {}

    for txn in transactions:
        product = txn["ProductName"]
        quantity = txn["Quantity"]
        revenue = txn["Quantity"] * txn["UnitPrice"]

        if product not in product_data:
            product_data[product] = {"qty": 0, "rev": 0.0}

        product_data[product]["qty"] += quantity
        product_data[product]["rev"] += revenue

    product_list = [
        (product, data["qty"], round(data["rev"], 2))
        for product, data in product_data.items()
    ]

    product_list.sort(key=lambda x: x[1], reverse=True)
    return product_list[:n]


#-- d) Customer Purchase Analysis
def customer_analysis(transactions):
    customer_data = {}

    for txn in transactions:
        customer = txn["CustomerID"]
        amount = txn["Quantity"] * txn["UnitPrice"]
        product = txn["ProductName"]

        if customer not in customer_data:
            customer_data[customer] = {
                "total_spent": 0.0,
                "purchase_count": 0,
                "products_bought": set()
            }

        customer_data[customer]["total_spent"] += amount
        customer_data[customer]["purchase_count"] += 1
        customer_data[customer]["products_bought"].add(product)

    for customer in customer_data:
        total = customer_data[customer]["total_spent"]
        count = customer_data[customer]["purchase_count"]
        customer_data[customer]["avg_order_value"] = round(total / count, 2)
        customer_data[customer]["products_bought"] = list(customer_data[customer]["products_bought"])

    return dict(sorted(customer_data.items(), key=lambda x: x[1]["total_spent"], reverse=True))


#--------------------- Task 2.2: Date-based Analysis ---------------------#

#-- a) Daily Sales Trend
def daily_sales_trend(transactions):
    daily = {}

    for txn in transactions:
        date = txn["Date"]
        amount = txn["Quantity"] * txn["UnitPrice"]
        customer = txn["CustomerID"]

        if date not in daily:
            daily[date] = {
                "revenue": 0.0,
                "transaction_count": 0,
                "customers": set()
            }

        daily[date]["revenue"] += amount
        daily[date]["transaction_count"] += 1
        daily[date]["customers"].add(customer)

    for date in daily:
        daily[date]["unique_customers"] = len(daily[date]["customers"])
        del daily[date]["customers"]
        daily[date]["revenue"] = round(daily[date]["revenue"], 2)

    return dict(sorted(daily.items(), key=lambda x: x[0]))


#-- b) Find Peak Sales Day
def peak_sales_day(daily_trends):
    if not daily_trends:
        return {}

    peak_date = max(daily_trends, key=lambda d: daily_trends[d]["revenue"])
    return {
        "date": peak_date,
        "revenue": daily_trends[peak_date]["revenue"],
        "transaction_count": daily_trends[peak_date]["transaction_count"]
    }


#--------------------- Task 2.3: Product Performance ---------------------#

#-- a) Low Performing Products
def low_performing_products(transactions, threshold=10):
    product_data = {}

    for txn in transactions:
        product = txn["ProductName"]
        quantity = txn["Quantity"]
        revenue = txn["Quantity"] * txn["UnitPrice"]

        if product not in product_data:
            product_data[product] = {"qty": 0, "rev": 0.0}

        product_data[product]["qty"] += quantity
        product_data[product]["rev"] += revenue

    low_products = [
        (product, data["qty"], round(data["rev"], 2))
        for product, data in product_data.items()
        if data["qty"] < threshold
    ]

    low_products.sort(key=lambda x: x[1])
    return low_products
