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
			"label": _("Distributor"),
			"fieldname": "distributor",
			"fieldtype": "Link",
			"options":"Distributor Profile"
		},
		{
			"label": _("Retailer"),
			"fieldname": "retailer",
			"fieldtype": "Data",
			# "options":"Master Retail Profile"
		},
		{
			"label":_("Sales Record ID"),
			"fieldname":"record_id",
			"fieldtype":"Data",
		},
		{
			"label":_("Sales Date"),
			"fieldname":"sales_date",
			"fieldtype":"Date",
		},
		{
			"label":_("Invoice #"),
			"fieldname":"invoice",
			"fieldtype":"Data",
			"reqd":1
		},
		{
			"label":_("Agent Code"),
			"fieldname":"agent_code",
			"fieldtype":"Data"
		},
		{
			"label":_("Item"),
			"fieldname":"item",
			"fieldtype":"Data",
			"reqd":1
		},
		{
			"label":_("Qty"),
			"fieldname":"item_qty",
			"fieldtype":"Float",
			"reqd":1
		},
		{
			"label":_("Free Qty"),
			"fieldname":"free_qty",
			"fieldtype":"Float"
		},
		{
			"label":_("Item Rate"),
			"fieldname":"item_rate",
			"fieldtype":"Float",
			"reqd":1
		},
		{
			"label":_("Line Item Value"),
			"fieldname":"basic_value",
			"fieldtype":"Float",
			"reqd":1
		},
	]
	return columns


def get_data(filters) -> list[list]:
	"""Return data for the report.

	The report data is a list of rows, with each row being a list of cell values.
	"""
	if not filters:
		filters = {}
	
	conditions = ""
	values = {}
	
	if filters.get("distributor"):
		conditions += " AND sr.distributor = %(distributor)s"
		values["distributor"] = filters["distributor"]
		
	if filters.get("retailer"):
		conditions += " AND sr.retailer = %(retailer)s"
		values["retailer"] = filters["retailer"]
		
	if filters.get("from_date"):
		conditions += " AND sr.sales_date >= %(from_date)s"
		values["from_date"] = filters["from_date"]
		
	if filters.get("to_date"):
		conditions += " AND sr.sales_date <= %(to_date)s"
		values["to_date"] = filters["to_date"]
	
	sql_query = f"""
		SELECT
			sr.distributor as distributor,
			mrp.retailer_name as retailer,
			sr.name as record_id,
			sr.sales_date as sales_date,
			sr.invoice as invoice,
			sr.agent_code as agent_code,
			srli.company_item as item,
			srli.converted_quantity as item_qty,
			(srli.free_quantity * srli.conversion_rate) as free_qty,
			(srli.item_rate / srli.conversion_rate) as item_rate,
			srli.line_item_amount as basic_value
		FROM
			`tabSales Record` sr
		INNER JOIN
			`tabSales Record Line Item` srli ON sr.name = srli.parent
		INNER JOIN
			`tabMaster Retail Profile` mrp ON sr.retailer = mrp.name
		WHERE
			1=1 {conditions}
		ORDER BY
			sr.sales_date
	"""
	
	data = frappe.db.sql(sql_query, values=values, as_dict=True)
	return data
