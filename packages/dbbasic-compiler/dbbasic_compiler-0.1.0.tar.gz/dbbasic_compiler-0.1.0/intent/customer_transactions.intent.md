# customer_transactions

## Intent History

**User** (2025-10-13T14:49:51.221076):
I need to process customer transaction data from a CSV file.

**Ai** (2025-10-13T14:49:51.221078):
What information is in the CSV, and what processing do you need?

**User** (2025-10-13T14:49:51.221080):
The CSV has customer_id, transaction_date, amount, and product_category. I need to calculate totals per customer.

**Ai** (2025-10-13T14:49:51.221081):
Should I include any filtering or flagging logic?

**User** (2025-10-13T14:49:51.221082):
Yes! Filter out transactions older than 90 days. Flag customers who spent over $1000 as 'high_value'.

**User** (2025-10-13T14:49:51.221083):
Also flag customers as 'at_risk' if they haven't purchased in 30 days.

**Ai** (2025-10-13T14:49:51.221084):
Should I calculate average transaction amount and most frequent category?

**User** (2025-10-13T14:49:51.221086):
Yes, that would be helpful for the marketing team.

**Ai** (2025-10-13T14:49:51.221087):
What's the expected file size? This helps me choose optimal libraries.

**User** (2025-10-13T14:49:51.221088):
Files can be up to 100,000 rows. Performance matters.

**User** (2025-10-13T14:49:51.221089):
Oh, and export the results to JSON format.

## Context Tags

@context:financial @context:customer-analytics @context:data-processing
@pattern:etl @pattern:aggregation @pattern:filtering

## Extracted Requirements

1. [input] Read CSV file with customer transaction data (must)
2. [filter] Filter transactions older than 90 days (must)
3. [aggregate] Group transactions by customer_id (must)
4. [aggregate] Calculate total spending per customer (must)
5. [aggregate] Calculate average transaction amount per customer (should)
6. [aggregate] Identify most frequent product category per customer (should)
7. [aggregate] Count number of transactions per customer (should)
8. [flag] Flag customers with total spending > $1000 as high_value (must)
9. [flag] Flag customers with no purchases in 30 days as at_risk (must)
10. [output] Export results to JSON format (must)
11. [performance] Handle files up to 100k rows efficiently (must)
12. [output] Sort results by total spending (highest first) (should)

## Metadata

- **Created**: 2025-10-13T14:49:51.221069
- **Total Messages**: 11
- **Total Requirements**: 12

- **stakeholder**: marketing-team
- **performance_requirement**: 100k-rows
- **priority**: high
- **estimated_complexity**: medium