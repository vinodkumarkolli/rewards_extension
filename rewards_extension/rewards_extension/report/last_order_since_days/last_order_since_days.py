# Copyright (c) 2025, Vinod Kumar K and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters: dict | None = None):
	"""Return columns and data for the report.

	This is the main entry point for the report. It accepts the filters as a
	dictionary and should return columns and data. It is called by the framework
	every time the report is refreshed or a filter is updated.
	"""
	columns = get_columns()
	data = get_data(filters)

	return columns, data


def get_columns() -> list[dict]:
	"""Return columns for the report.

	One field definition per column, just like a DocType field definition.
	"""
	columns = [
			{
				"label": _("Retailer"),
				"fieldname": "retailer",
				"fieldtype": "Link",
				"options":"Master Retail Profile"
			},
			{
				"label": _("Retailer Name"),
				"fieldname":"retailer_name",
				"fieldtype":"Data"
			},
			{
				"label": _("Outlet Code"),
				"fieldname":"outlet_code",
				"fieldtype":"Data"
			},
			{
				"label": _("Last Ordered Date"),
				"fieldname":"last_ordered_date",
				"fieldtype":"Date"
			},
			{
				"label": _("Last Order since days"),
				"fieldname":"last_order_since_days",
				"fieldtype":"Int"
			},
			{
				"label": _("Orders till now"),
				"fieldname":"orders_till_now",
				"fieldtype":"Int"
			},
			{
				"label": _("Average Order Value"),
				"fieldname":"avg_order_value",
				"fieldtype":"Float",
				"precision":2
			},
			{
				"label": _("Average Order Days"),
				"fieldname":"avg_order_days",
				"fieldtype":"Int"
			}
		]
	return columns


def get_data(filters) -> list[list]:
	"""Return data for the report.

	The report data is a list of rows, with each row being a list of cell values.
	"""
	if not filters:
		filters = {}
	
	# Build conditions based on filters
	conditions = ""
	values = {}
	
	# Add distributor filter if provided
	if filters.get("distributor"):
		conditions += " AND sr.distributor = %(distributor)s"
		values["distributor"] = filters["distributor"]
	
	# We need to find retailers with negative quantity items in their sales records
	# and then get the most recent sales date for each retailer
	sql_query = f"""
		SELECT
			sr.retailer as retailer,
			mrp.retailer_name as retailer_name,
			mrp.outlet_code as outlet_code,
			MAX(sr.sales_date) as last_ordered_date,
			DATEDIFF(CURDATE(), MAX(sr.sales_date)) as last_order_since_days,
			COUNT(DISTINCT sr.name) as orders_till_now,
			AVG(order_totals.total_value) as avg_order_value,
			COALESCE(AVG(order_intervals.days_between_orders), 0) as avg_order_days
		FROM
			`tabSales Record` sr
		INNER JOIN
			`tabMaster Retail Profile` mrp ON sr.retailer = mrp.name
		INNER JOIN
			`tabSales Record Line Item` srli ON sr.name = srli.parent
		INNER JOIN
			(
				SELECT
					parent,
					SUM(item_quantity * item_rate) as total_value
				FROM
					`tabSales Record Line Item`
				WHERE
					item_quantity > 0
				GROUP BY
					parent
			) as order_totals ON sr.name = order_totals.parent
		LEFT JOIN
			(
				SELECT
					retailer,
					AVG(DATEDIFF(sales_date, prev_sales_date)) as days_between_orders
				FROM
					(
						SELECT
							retailer,
							sales_date,
							LAG(sales_date) OVER (PARTITION BY retailer ORDER BY sales_date) as prev_sales_date
						FROM
							`tabSales Record`
						WHERE
							sales_date IS NOT NULL
					) as ordered_sales
				WHERE
					prev_sales_date IS NOT NULL
				GROUP BY
					retailer
			) as order_intervals ON sr.retailer = order_intervals.retailer
		WHERE
			srli.item_quantity > 0
			{conditions}
		GROUP BY
			sr.retailer, mrp.retailer_name, mrp.outlet_code
		ORDER BY
			last_order_since_days DESC
	"""
	
	# Execute the query
	data = frappe.db.sql(sql_query, values=values, as_dict=True)
	
	# Format the result as list of lists
	result = []
	for row in data:
		result.append([
			row.retailer,
			row.retailer_name,
			row.outlet_code,
			row.last_ordered_date,
			row.last_order_since_days,
			row.orders_till_now,
			row.avg_order_value,
			row.avg_order_days
		])
	
	return result
