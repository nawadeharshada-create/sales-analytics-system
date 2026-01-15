# main.py

from utils.file_handler import read_sales_data
from utils.data_processor import (
    parse_transactions,
    validate_and_filter,
    calculate_total_revenue,
    region_wise_sales,
    top_selling_products,
    customer_analysis,
    daily_sales_trend,
    low_performing_products,
)
from utils.api_handler import (
    fetch_all_products,
    create_product_mapping,
    enrich_sales_data,
    save_enriched_data,
)
from utils.report_generator import generate_sales_report


def main():
   
    try:
        print("=" * 40)
        print("SALES ANALYTICS SYSTEM")
        print("=" * 40)

        # -----------------------------
        # [1/10] Read sales data
        # -----------------------------
        print("\n[1/10] Reading sales data...")
        raw_lines = read_sales_data("data/sales_data.txt")
        if not raw_lines:
            print("No data read. Please check file path or file content.")
            return
        print(f"Successfully read {len(raw_lines)} raw lines")

        # -----------------------------
        # [2/10] Parse & clean
        # -----------------------------
        print("\n[2/10] Parsing and cleaning data...")
        transactions = parse_transactions(raw_lines)
        if not transactions:
            print("No valid transactions after parsing. Please check file format.")
            return
        print(f"Parsed {len(transactions)} records")

        # -----------------------------
        # [3/10] Filter options
        # -----------------------------
        regions = sorted({t.get("Region") for t in transactions if t.get("Region")})
        amounts = [
            (t.get("Quantity", 0) * t.get("UnitPrice", 0))
            for t in transactions
            if isinstance(t.get("Quantity"), int) and isinstance(t.get("UnitPrice"), (int, float))
        ]
        min_amt = min(amounts) if amounts else 0
        max_amt = max(amounts) if amounts else 0

        print("\n[3/10] Filter Options Available:")
        print("Regions:", ", ".join(regions) if regions else "N/A")
        print(f"Amount Range: ₹{min_amt:,.0f} - ₹{max_amt:,.0f}")

        apply_filter = input("\nDo you want to filter data? (y/n): ").strip().lower()

        region_filter = None
        min_amount = None
        max_amount = None

        if apply_filter == "y":
            if regions:
                region_filter = input(f"Enter region from {regions} (or press Enter to skip): ").strip()
                if region_filter == "":
                    region_filter = None

            min_in = input("Enter minimum amount (or press Enter to skip): ").strip()
            max_in = input("Enter maximum amount (or press Enter to skip): ").strip()

            if min_in:
                try:
                    min_amount = float(min_in)
                except ValueError:
                    print("Invalid min amount. Ignoring min filter.")
                    min_amount = None

            if max_in:
                try:
                    max_amount = float(max_in)
                except ValueError:
                    print("Invalid max amount. Ignoring max filter.")
                    max_amount = None

        # -----------------------------
        # [4/10] Validate + apply filter
        # -----------------------------
        print("\n[4/10] Validating transactions...")
        valid_transactions, invalid_count, filter_summary = validate_and_filter(
            transactions,
            region=region_filter,
            min_amount=min_amount,
            max_amount=max_amount,
        )

        print(f"Valid: {len(valid_transactions)} | Invalid: {invalid_count}")
        if filter_summary:
            print("Filter Summary:", filter_summary)

        if not valid_transactions:
            print("No valid transactions after validation/filtering.")
            return

        # -----------------------------
        # [5/10] Analysis (Part 2)
        # -----------------------------
        print("\n[5/10] Analyzing sales data...")

        total_revenue = calculate_total_revenue(valid_transactions)
        region_stats = region_wise_sales(valid_transactions)
        top_products = top_selling_products(valid_transactions, n=5)
        customers = customer_analysis(valid_transactions)
        trend = daily_sales_trend(valid_transactions)
        low_products = low_performing_products(valid_transactions, threshold=10)

        print("Analysis complete")

        # -----------------------------
        # [6/10] Fetch API products
        # -----------------------------
        print("\n[6/10] Fetching product data from API...")
        api_products = fetch_all_products()
        print(f"Fetched {len(api_products)} products")

        # -----------------------------
        # [7/10] Enrich transactions
        # -----------------------------
        print("\n[7/10] Enriching sales data...")
        product_mapping = create_product_mapping(api_products)
        enriched_transactions = enrich_sales_data(valid_transactions, product_mapping)

        enriched_count = sum(1 for t in enriched_transactions if t.get("API_Match") is True)
        success_rate = (enriched_count / len(enriched_transactions)) * 100

        print(f"Enriched {enriched_count}/{len(enriched_transactions)} transactions ({success_rate:.1f}%)")

        # -----------------------------
        # [8/10] Save enriched file
        # -----------------------------
        print("\n[8/10] Saving enriched data...")
        enriched_path = "data/enriched_sales_data.txt"
        save_enriched_data(enriched_transactions, filename=enriched_path)
        print(f"Saved to: {enriched_path}")

        # -----------------------------
        # [9/10] Generate report
        # -----------------------------
        print("\n[9/10] Generating report...")
        report_path = "output/sales_report.txt"
        generate_sales_report(
            transactions=valid_transactions,
            enriched_transactions=enriched_transactions,
            output_file=report_path,
        )
        print(f"Report saved to: {report_path}")

        # -----------------------------
        # [10/10] Done
        # -----------------------------
        print("\n[10/10] Process Complete!")
        print("=" * 40)

    except Exception as e:
        print("\n✗ An error occurred. Please check the details below:")
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
