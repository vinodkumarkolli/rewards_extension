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
	return [
		{
			"label": _("Campaign Name"),
			"fieldname": "campaign_name",
			"fieldtype": "Data",
			"width": 200
		},
		{
			"label": _("Start Date"),
			"fieldname": "start_date",
			"fieldtype": "Date",
			"width": 120
		},
		{
			"label": _("End Date"),
			"fieldname": "end_date",
			"fieldtype": "Date",
			"width": 120
		},
		{
			"label": _("Campaign Target"),
			"fieldname": "campaign_target",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("URL"),
			"fieldname": "url",
			"fieldtype": "Data",
			"width": 300
		}
	]


def get_data(filters: dict | None = None) -> list[dict]:
	"""Return data for the report.

	The report data is a list of rows, with each row being a list of cell values.
	"""
	if not filters:
		filters = {}
	
	# Build conditions for the SQL query
	conditions = ""
	values = {}
	
	# Add filter conditions
	if filters.get("campaign"):
		conditions += " AND vc.name = %(campaign)s"
		values["campaign"] = filters["campaign"]
		
	if filters.get("campaign_name"):
		conditions += " AND vc.campaign_name LIKE %(campaign_name)s"
		values["campaign_name"] = f"%{filters['campaign_name']}%"
		
	if filters.get("campaign_status"):
		conditions += " AND vc.campaign_status = %(campaign_status)s"
		values["campaign_status"] = filters["campaign_status"]
		
	if filters.get("campaign_target"):
		conditions += " AND vc.campaign_target = %(campaign_target)s"
		values["campaign_target"] = filters["campaign_target"]
	
	# Get site URL for generating the URL column
	site_url = frappe.utils.get_url()
	
	# SQL query to fetch voucher campaign data
	sql_query = f"""
		SELECT
			vc.campaign_name as campaign_name,
			vc.start_date as start_date,
			vc.end_date as end_date,
			vc.campaign_target as campaign_target,
			CASE
				WHEN vc.campaign_status = 'Active' THEN CONCAT('{site_url}', '/deals/', vc.name)
				ELSE ''
			END as url
		FROM
			`tabVoucher Campaign` vc
		WHERE
			1=1 {conditions}
		ORDER BY
			vc.modified DESC
	"""
	
	data = frappe.db.sql(sql_query, values=values, as_dict=True)
	return data
