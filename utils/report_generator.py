import os
from datetime import datetime

 # 1)HEADER
from utils.data_processor import (
    calculate_total_revenue,
    region_wise_sales,
    top_selling_products,
    customer_analysis,
    daily_sales_trend,
    low_performing_products,
)

def format_inr(amount: float) -> str:
    return f"₹{amount:,.2f}"

def generate_sales_report(transactions, enriched_transactions, output_file="output/sales_report.txt"):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total_records = len(transactions)

 # 2) OVERALL SUMMARY
    total_revenue = calculate_total_revenue(transactions)
    total_txn = len(transactions)
    avg_order_value = (total_revenue / total_txn) if total_txn else 0.0

    dates = sorted([t.get("Date") for t in transactions if t.get("Date")])
    date_range = f"{dates[0]} to {dates[-1]}" if dates else "N/A"

 # 3) REGION-WISE PERFORMANCE
    region_stats = region_wise_sales(transactions)

 # 4) TOP 5 PRODUCTS
    top5_products = top_selling_products(transactions, n=5)

 # 5) TOP 5 CUSTOMERS
    customers = customer_analysis(transactions)
    top5_customers = list(customers.items())[:5]

  # 6) DAILY SALES TREND
    trend = daily_sales_trend(transactions)

 # 7) PRODUCT PERFORMANCE ANALYSIS
    best_day = None
    best_day_rev = -1
    for d, info in trend.items():
        rev = float(info.get("revenue", 0))
        if rev > best_day_rev:
            best_day_rev = rev
            best_day = d

    low_perf = low_performing_products(transactions, threshold=10)

    avg_by_region = {}
    for region, info in region_stats.items():
        sales = float(info.get("total_sales", 0))
        cnt = int(info.get("transaction_count", 0))
        avg_by_region[region] = (sales / cnt) if cnt else 0.0

 # 8) API ENRICHMENT SUMMARY
    enriched_count = 0
    failed_products = set()

    for t in enriched_transactions:
        if t.get("API_Match") is True:
            enriched_count += 1
        else:
            pid = t.get("ProductID", "")
            pname = t.get("ProductName", "")
            failed_products.add(f"{pid} ({pname})".strip())

    total_checked = len(enriched_transactions)
    success_rate = (enriched_count / total_checked * 100) if total_checked else 0.0

# WRITE REPORT
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("=" * 55 + "\n")
        f.write("SALES ANALYTICS REPORT".center(55) + "\n")
        f.write(f"Generated: {now}".center(55) + "\n")
        f.write(f"Records Processed: {total_records}".center(55) + "\n")
        f.write("=" * 55 + "\n\n")

        f.write("OVERALL SUMMARY\n")
        f.write("-" * 55 + "\n")
        f.write(f"Total Revenue:         {format_inr(total_revenue)}\n")
        f.write(f"Total Transactions:    {total_txn}\n")
        f.write(f"Average Order Value:   {format_inr(avg_order_value)}\n")
        f.write(f"Date Range:            {date_range}\n\n")

        f.write("REGION-WISE PERFORMANCE\n")
        f.write("-" * 55 + "\n")
        f.write(f"{'Region':<10}{'Sales':>15}{'% of Total':>12}{'Transactions':>14}\n")
        for region, info in region_stats.items():
            sales = float(info.get("total_sales", 0))
            pct = float(info.get("percentage", 0))
            cnt = int(info.get("transaction_count", 0))
            f.write(f"{region:<10}{format_inr(sales):>15}{pct:>12.2f}{cnt:>14}\n")
        f.write("\n")

        f.write("TOP 5 PRODUCTS\n")
        f.write("-" * 55 + "\n")
        f.write(f"{'Rank':<6}{'Product Name':<22}{'Qty Sold':>10}{'Revenue':>15}\n")
        for i, (pname, qty, rev) in enumerate(top5_products, start=1):
            f.write(f"{i:<6}{str(pname)[:22]:<22}{int(qty):>10}{format_inr(float(rev)):>15}\n")
        f.write("\n")

        f.write("TOP 5 CUSTOMERS\n")
        f.write("-" * 55 + "\n")
        f.write(f"{'Rank':<6}{'Customer ID':<15}{'Total Spent':>15}{'Order Count':>14}\n")
        for i, (cid, info) in enumerate(top5_customers, start=1):
            spent = float(info.get("total_spent", 0))
            cnt = int(info.get("purchase_count", 0))
            f.write(f"{i:<6}{cid:<15}{format_inr(spent):>15}{cnt:>14}\n")
        f.write("\n")

        f.write("DAILY SALES TREND\n")
        f.write("-" * 55 + "\n")
        f.write(f"{'Date':<12}{'Revenue':>15}{'Transactions':>14}{'Unique Customers':>18}\n")
        for d, info in trend.items():
            rev = float(info.get("revenue", 0))
            cnt = int(info.get("transaction_count", 0))
            uniq = int(info.get("unique_customers", 0))
            f.write(f"{d:<12}{format_inr(rev):>15}{cnt:>14}{uniq:>18}\n")
        f.write("\n")

        f.write("PRODUCT PERFORMANCE ANALYSIS\n")
        f.write("-" * 55 + "\n")
        f.write(f"Best Selling Day: {best_day} ({format_inr(best_day_rev)})\n\n")

        f.write("Low Performing Products (Qty < threshold)\n")
        if low_perf:
            f.write(f"{'Product Name':<22}{'Qty Sold':>10}{'Revenue':>15}\n")
            for pname, qty, rev in low_perf:
                f.write(f"{str(pname)[:22]:<22}{int(qty):>10}{format_inr(float(rev)):>15}\n")
        else:
            f.write("None\n")
        f.write("\n")

        f.write("Average Transaction Value by Region\n")
        f.write(f"{'Region':<10}{'Avg Value':>15}\n")
        for region, avgv in avg_by_region.items():
            f.write(f"{region:<10}{format_inr(avgv):>15}\n")
        f.write("\n")

        f.write("API ENRICHMENT SUMMARY\n")
        f.write("-" * 55 + "\n")
        f.write(f"Total Transactions Checked: {total_checked}\n")
        f.write(f"Total Products Enriched:    {enriched_count}\n")
        f.write(f"Success Rate:              {success_rate:.2f}%\n\n")

        f.write("Products that couldn't be enriched:\n")
        failed_list = sorted([x for x in failed_products if x])
        if failed_list:
            for item in failed_list:
                f.write(f"- {item}\n")
        else:
            f.write("None\n")

    return output_file