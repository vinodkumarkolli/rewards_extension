# Copyright (c) 2025, Vinod Kumar K and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from datetime import datetime
# For queries
from frappe.desk.reportview import get_match_cond


def execute(filters: dict | None = None):
	"""Return columns and data for the report.

	This is the main entry point for the report. It accepts the filters as a
	dictionary and should return columns and data. It is called by the framework
	every time the report is refreshed or a filter is updated.
	"""
	columns = get_columns(filters)
	data = get_data(filters)

	return columns, data


def get_columns(filters: dict | None = None) -> list[dict]:
	"""Return columns for the report.

	One field definition per column, just like a DocType field definition.
	"""
	columns = [
		{
			"label": _("Distributor"),
			"fieldname": "distributor",
			"fieldtype": "Link",
			"options": "Distributor Profile",
			"width": 200
		}
	]
	
	# Add company item column if a company item is selected as aggregation_fact
	if filters and filters.get("aggregation_fact") and filters.get("aggregation_fact") != "Sale Amount" and filters.get("aggregation_fact") != "Customer Count" and filters.get("aggregation_fact") != "Avg Order Value":
		columns.append({
			"label": _("Company Item"),
			"fieldname": "company_item",
			"fieldtype": "Link",
			"options": "Company Item",
			"width": 200
		})

	
	if not filters:
		filters = {}
	
	aggregate_option = filters.get("aggregate_option", "Monthly")
	
	# Determine the fieldtype based on aggregation_fact
	aggregation_fact = filters.get("aggregation_fact", "Sale Amount")
	if aggregation_fact == "Sale Amount" or aggregation_fact == "Avg Order Value":
		fieldtype = "Currency"
	elif aggregation_fact == "Customer Count":
		fieldtype = "Int"
	else:
		fieldtype = "Float"
	
	if aggregate_option == "Monthly":
		# Add columns for each month in the date range
		from_date = filters.get("from_date")
		to_date = filters.get("to_date")
		if from_date and to_date:
			from_date = datetime.strptime(from_date, "%Y-%m-%d")
			to_date = datetime.strptime(to_date, "%Y-%m-%d")
			
			# Generate month columns
			current = from_date.replace(day=1)
			end = to_date.replace(day=1)
			
			while current <= end:
				month_label = current.strftime("%b %Y")
				columns.append({
					"label": _(month_label),
					"fieldname": current.strftime("%Y-%m"),
					"fieldtype": fieldtype,
					"width": 120,
					"precision": 2 if fieldtype == "Float" else None
				})
				if current.month == 12:
					current = current.replace(year=current.year + 1, month=1)
				else:
					current = current.replace(month=current.month + 1)
	
	elif aggregate_option == "Quarterly":
		# Add columns for each quarter in the date range
		from_date = filters.get("from_date")
		to_date = filters.get("to_date")
		if from_date and to_date:
			from_date = datetime.strptime(from_date, "%Y-%m-%d")
			to_date = datetime.strptime(to_date, "%Y-%m-%d")
			
			# Generate quarter columns
			quarters = get_quarter_labels(from_date, to_date)
			for quarter_label, fieldname in quarters:
				columns.append({
					"label": _(quarter_label),
					"fieldname": fieldname,
					"fieldtype": fieldtype,
					"width": 150,
					"precision": 2 if fieldtype == "Float" else None
				})
	
	elif aggregate_option == "Yearly":
		# Add columns for each fiscal year in the date range
		from_date = filters.get("from_date")
		to_date = filters.get("to_date")
		if from_date and to_date:
			from_date = datetime.strptime(from_date, "%Y-%m-%d")
			to_date = datetime.strptime(to_date, "%Y-%m-%d")
			
			# Generate fiscal year columns
			years = get_fiscal_year_labels(from_date, to_date)
			for year_label, fieldname in years:
				columns.append({
					"label": _(year_label),
					"fieldname": fieldname,
					"fieldtype": fieldtype,
					"width": 150,
					"precision": 2 if fieldtype == "Float" else None
				})
	
	# Add total column if aggregation_fact is not "Avg Order Value" and not "Customer Count"
	if aggregation_fact != "Avg Order Value" and aggregation_fact != "Customer Count":
		columns.append({
			"label": _("Total"),
			"fieldname": "total",
			"fieldtype": fieldtype,
			"width": 150,
			"precision": 2 if fieldtype == "Float" else None
		})
	
	return columns


def get_quarter_labels(from_date, to_date):
	"""Generate quarter labels for the given date range."""
	quarters = []
	
	# Start from the beginning of the fiscal year
	current = get_fiscal_year_start(from_date)
	end = get_fiscal_year_end(to_date)
	
	while current <= end:
		# Q1: Apr, May, Jun
		q1_start = current.replace(month=4)
		if from_date <= get_fiscal_year_end(q1_start) and to_date >= q1_start:
			quarters.append((f"Q1 {current.year % 100:02d}-{(current.year+1) % 100:02d}", f"Q1_{current.year}_{current.year+1}"))
		
		# Q2: Jul, Aug, Sep
		q2_start = current.replace(month=7)
		if from_date <= get_fiscal_year_end(q2_start) and to_date >= q2_start:
			quarters.append((f"Q2 {current.year % 100:02d}-{(current.year+1) % 100:02d}", f"Q2_{current.year}_{current.year+1}"))
		
		# Q3: Oct, Nov, Dec
		q3_start = current.replace(month=10)
		if from_date <= get_fiscal_year_end(q3_start) and to_date >= q3_start:
			quarters.append((f"Q3 {current.year % 100:02d}-{(current.year+1) % 100:02d}", f"Q3_{current.year}_{current.year+1}"))
		
		# Q4: Jan, Feb, Mar
		q4_start = current.replace(year=current.year+1, month=1)
		q4_end = current.replace(year=current.year+1, month=3, day=31)
		if from_date <= q4_end and to_date >= q4_start:
			quarters.append((f"Q4 {(current.year+1) % 100:02d}-{(current.year+2) % 100:02d}", f"Q4_{current.year+1}_{current.year+2}"))
		
		current = current.replace(year=current.year + 1)
	
	return quarters


def get_fiscal_year_labels(from_date, to_date):
	"""Generate fiscal year labels for the given date range."""
	years = []
	
	# Start from the beginning of the fiscal year
	current = get_fiscal_year_start(from_date)
	end = get_fiscal_year_end(to_date)
	
	while current <= end:
		fiscal_year_label = f"FY {current.year % 100:02d}-{(current.year+1) % 100:02d}"
		fieldname = f"FY_{current.year}_{current.year+1}"
		years.append((fiscal_year_label, fieldname))
		current = current.replace(year=current.year + 1)
	
	return years


def get_fiscal_year_start(date):
	"""Get the start of the fiscal year (April 1) for the given date."""
	if date.month < 4:
		return date.replace(year=date.year - 1, month=4, day=1)
	else:
		return date.replace(month=4, day=1)


def get_fiscal_year_end(date):
	"""Get the end of the fiscal year (March 31) for the given date."""
	if date.month < 4:
		return date.replace(year=date.year, month=3, day=31)
	else:
		return date.replace(year=date.year + 1, month=3, day=31)


def get_data(filters: dict | None = None) -> list[dict]:
	"""Return data for the report.

	The report data is a list of rows, with each row being a list of cell values.
	"""
	if not filters:
		filters = {}
	
	# Build conditions for the SQL query
	conditions = ""
	values = {}
	
	if filters.get("distributor"):
		conditions += " AND sr.distributor = %(distributor)s"
		values["distributor"] = filters["distributor"]
		
	if filters.get("from_date"):
		conditions += " AND sr.sales_date >= %(from_date)s"
		values["from_date"] = filters["from_date"]
		
	if filters.get("to_date"):
		conditions += " AND sr.sales_date <= %(to_date)s"
		values["to_date"] = filters["to_date"]
	
	aggregate_option = filters.get("aggregate_option", "Monthly")
	
	if aggregate_option == "Monthly":
		return get_monthly_data(conditions, values, filters)
	elif aggregate_option == "Quarterly":
		return get_quarterly_data(conditions, values, filters)
	elif aggregate_option == "Yearly":
		return get_yearly_data(conditions, values, filters)
	else:
		return []


def get_monthly_data(conditions, values, filters):
	"""Get data aggregated by month."""
	from_date = datetime.strptime(filters["from_date"], "%Y-%m-%d")
	to_date = datetime.strptime(filters["to_date"], "%Y-%m-%d")
	
	# Generate month columns for grouping
	months = []
	current = from_date.replace(day=1)
	end = to_date.replace(day=1)
	
	while current <= end:
		months.append(current.strftime("%Y-%m"))
		if current.month == 12:
			current = current.replace(year=current.year + 1, month=1)
		else:
			current = current.replace(month=current.month + 1)
	
	# Determine the aggregation field and conditions based on aggregation_fact
	aggregation_fact = filters.get("aggregation_fact", "Sale Amount")
	
	if aggregation_fact == "Sale Amount":
		# Use line_item_amount for aggregation
		aggregation_field = "srli.line_item_amount"
		additional_conditions = ""
		select_fields = "sr.distributor as distributor"
	elif aggregation_fact == "Customer Count":
		# Use COUNT(DISTINCT retailer) for aggregation
		aggregation_field = "COUNT(DISTINCT sr.retailer)"
		additional_conditions = ""
		select_fields = "sr.distributor as distributor"
	elif aggregation_fact == "Avg Order Value":
		# Use SUM(line_item_amount)/COUNT(DISTINCT retailer) for aggregation
		# For monthly, we'll calculate the average across all months
		aggregation_field = "(SUM(srli.line_item_amount)/COUNT(DISTINCT sr.retailer))/1"
		additional_conditions = ""
		select_fields = "sr.distributor as distributor"
	elif aggregation_fact:
		# Use converted_quantity for aggregation with company_item filter
		aggregation_field = "srli.converted_quantity"
		additional_conditions = " AND srli.company_item = %(company_item)s"
		values["company_item"] = aggregation_fact
		select_fields = "sr.distributor as distributor, srli.company_item as company_item"
	else:
		# Default to item_quantity * item_rate
		aggregation_field = "srli.item_quantity * srli.item_rate"
		additional_conditions = ""
		select_fields = "sr.distributor as distributor"
	
	# Build the SQL query with CASE statements for each month
	month_sums = []
	for month in months:
		year, month_num = month.split("-")
		if aggregation_fact == "Customer Count":
			month_sums.append(f"COUNT(DISTINCT CASE WHEN YEAR(sr.sales_date) = {year} AND MONTH(sr.sales_date) = {int(month_num)} THEN sr.retailer ELSE NULL END) as `{month}`")
		elif aggregation_fact == "Avg Order Value":
			month_sums.append(f"SUM(CASE WHEN YEAR(sr.sales_date) = {year} AND MONTH(sr.sales_date) = {int(month_num)} THEN srli.line_item_amount ELSE 0 END)/COUNT(DISTINCT CASE WHEN YEAR(sr.sales_date) = {year} AND MONTH(sr.sales_date) = {int(month_num)} THEN sr.retailer ELSE NULL END) as `{month}`")
		else:
			month_sums.append(f"SUM(CASE WHEN YEAR(sr.sales_date) = {year} AND MONTH(sr.sales_date) = {int(month_num)} THEN {aggregation_field} ELSE 0 END) as `{month}`")
	
	sql_query = f"""
		SELECT
			{select_fields},
			{', '.join(month_sums)}
			{f", SUM({aggregation_field}) as total" if aggregation_fact != 'Avg Order Value' and aggregation_fact != 'Customer Count' else ""}
		FROM
			`tabSales Record` sr
		INNER JOIN
			`tabSales Record Line Item` srli ON sr.name = srli.parent
		WHERE
			1=1 {conditions} {additional_conditions}
		GROUP BY
			sr.distributor{', srli.company_item' if aggregation_fact != 'Sale Amount' and aggregation_fact and aggregation_fact != 'Customer Count' and aggregation_fact != 'Avg Order Value' else ''}
		ORDER BY
			sr.distributor{', srli.company_item' if aggregation_fact != 'Sale Amount' and aggregation_fact and aggregation_fact != 'Customer Count' and aggregation_fact != 'Avg Order Value' else ''}
	"""
	
	data = frappe.db.sql(sql_query, values=values, as_dict=True)
	return data


def get_quarterly_data(conditions, values, filters):
	"""Get data aggregated by quarter."""
	from_date = datetime.strptime(filters["from_date"], "%Y-%m-%d")
	to_date = datetime.strptime(filters["to_date"], "%Y-%m-%d")
	
	# Generate quarter columns for grouping
	quarters = get_quarter_labels(from_date, to_date)
	
	# Determine the aggregation field and conditions based on aggregation_fact
	aggregation_fact = filters.get("aggregation_fact", "Sale Amount")
	
	if aggregation_fact == "Sale Amount":
		# Use line_item_amount for aggregation
		aggregation_field = "srli.line_item_amount"
		additional_conditions = ""
		select_fields = "sr.distributor as distributor"
	elif aggregation_fact == "Customer Count":
		# Use COUNT(DISTINCT retailer) for aggregation
		aggregation_field = "COUNT(DISTINCT sr.retailer)"
		additional_conditions = ""
		select_fields = "sr.distributor as distributor"
	elif aggregation_fact == "Avg Order Value":
		# Use (SUM(line_item_amount)/COUNT(DISTINCT retailer))/number_of_months for aggregation
		# For quarterly, we'll calculate the average across all quarters
		aggregation_field = "(SUM(srli.line_item_amount)/COUNT(DISTINCT sr.retailer))/3"
		additional_conditions = ""
		select_fields = "sr.distributor as distributor"
	elif aggregation_fact:
		# Use converted_quantity for aggregation with company_item filter
		aggregation_field = "srli.converted_quantity"
		additional_conditions = " AND srli.company_item = %(company_item)s"
		values["company_item"] = aggregation_fact
		select_fields = "sr.distributor as distributor, srli.company_item as company_item"
	else:
		# Default to item_quantity * item_rate
		aggregation_field = "srli.item_quantity * srli.item_rate"
		additional_conditions = ""
		select_fields = "sr.distributor as distributor"
	
	# Build quarter sum expressions
	quarter_sums = []
	for quarter_label, fieldname in quarters:
		parts = quarter_label.split()
		if parts[0] == "Q1":
			# Q1: Apr, May, Jun
			year = int(parts[1].split("-")[0])
			if aggregation_fact == "Customer Count":
				quarter_sums.append(f"COUNT(DISTINCT CASE WHEN (sr.sales_date >= '{year}-04-01' AND sr.sales_date <= '{year}-06-30') THEN sr.retailer ELSE NULL END) as `{fieldname}`")
			elif aggregation_fact == "Avg Order Value":
				quarter_sums.append(f"(SUM(CASE WHEN (sr.sales_date >= '{year}-04-01' AND sr.sales_date <= '{year}-06-30') THEN srli.line_item_amount ELSE 0 END)/COUNT(DISTINCT CASE WHEN (sr.sales_date >= '{year}-04-01' AND sr.sales_date <= '{year}-06-30') THEN sr.retailer ELSE NULL END))/3 as `{fieldname}`")
			else:
				quarter_sums.append(f"SUM(CASE WHEN (sr.sales_date >= '{year}-04-01' AND sr.sales_date <= '{year}-06-30') THEN {aggregation_field} ELSE 0 END) as `{fieldname}`")
		elif parts[0] == "Q2":
			# Q2: Jul, Aug, Sep
			year = int(parts[1].split("-")[0])
			if aggregation_fact == "Customer Count":
				quarter_sums.append(f"COUNT(DISTINCT CASE WHEN (sr.sales_date >= '{year}-07-01' AND sr.sales_date <= '{year}-09-30') THEN sr.retailer ELSE NULL END) as `{fieldname}`")
			elif aggregation_fact == "Avg Order Value":
				quarter_sums.append(f"(SUM(CASE WHEN (sr.sales_date >= '{year}-07-01' AND sr.sales_date <= '{year}-09-30') THEN srli.line_item_amount ELSE 0 END)/COUNT(DISTINCT CASE WHEN (sr.sales_date >= '{year}-07-01' AND sr.sales_date <= '{year}-09-30') THEN sr.retailer ELSE NULL END))/3 as `{fieldname}`")
			else:
				quarter_sums.append(f"SUM(CASE WHEN (sr.sales_date >= '{year}-07-01' AND sr.sales_date <= '{year}-09-30') THEN {aggregation_field} ELSE 0 END) as `{fieldname}`")
		elif parts[0] == "Q3":
			# Q3: Oct, Nov, Dec
			year = int(parts[1].split("-")[0])
			if aggregation_fact == "Customer Count":
				quarter_sums.append(f"COUNT(DISTINCT CASE WHEN (sr.sales_date >= '{year}-10-01' AND sr.sales_date <= '{year}-12-31') THEN sr.retailer ELSE NULL END) as `{fieldname}`")
			elif aggregation_fact == "Avg Order Value":
				quarter_sums.append(f"(SUM(CASE WHEN (sr.sales_date >= '{year}-10-01' AND sr.sales_date <= '{year}-12-31') THEN srli.line_item_amount ELSE 0 END)/COUNT(DISTINCT CASE WHEN (sr.sales_date >= '{year}-10-01' AND sr.sales_date <= '{year}-12-31') THEN sr.retailer ELSE NULL END))/3 as `{fieldname}`")
			else:
				quarter_sums.append(f"SUM(CASE WHEN (sr.sales_date >= '{year}-10-01' AND sr.sales_date <= '{year}-12-31') THEN {aggregation_field} ELSE 0 END) as `{fieldname}`")
		elif parts[0] == "Q4":
			# Q4: Jan, Feb, Mar
			year = int(parts[1].split("-")[0])
			if aggregation_fact == "Customer Count":
				quarter_sums.append(f"COUNT(DISTINCT CASE WHEN (sr.sales_date >= '{year}-01-01' AND sr.sales_date <= '{year}-03-31') THEN sr.retailer ELSE NULL END) as `{fieldname}`")
			elif aggregation_fact == "Avg Order Value":
				quarter_sums.append(f"(SUM(CASE WHEN (sr.sales_date >= '{year}-01-01' AND sr.sales_date <= '{year}-03-31') THEN srli.line_item_amount ELSE 0 END)/COUNT(DISTINCT CASE WHEN (sr.sales_date >= '{year}-01-01' AND sr.sales_date <= '{year}-03-31') THEN sr.retailer ELSE NULL END))/3 as `{fieldname}`")
			else:
				quarter_sums.append(f"SUM(CASE WHEN (sr.sales_date >= '{year}-01-01' AND sr.sales_date <= '{year}-03-31') THEN {aggregation_field} ELSE 0 END) as `{fieldname}`")
	
	sql_query = f"""
		SELECT
			{select_fields},
			{', '.join(quarter_sums)}
			{f", SUM({aggregation_field}) as total" if aggregation_fact != 'Avg Order Value' and aggregation_fact != 'Customer Count' else ""}
		FROM
			`tabSales Record` sr
		INNER JOIN
			`tabSales Record Line Item` srli ON sr.name = srli.parent
		WHERE
			1=1 {conditions} {additional_conditions}
		GROUP BY
			sr.distributor{', srli.company_item' if aggregation_fact != 'Sale Amount' and aggregation_fact and aggregation_fact != 'Customer Count' and aggregation_fact != 'Avg Order Value' else ''}
		ORDER BY
			sr.distributor{', srli.company_item' if aggregation_fact != 'Sale Amount' and aggregation_fact and aggregation_fact != 'Customer Count' and aggregation_fact != 'Avg Order Value' else ''}
	"""
	
	data = frappe.db.sql(sql_query, values=values, as_dict=True)
	return data


def get_yearly_data(conditions, values, filters):
	"""Get data aggregated by fiscal year."""
	from_date = datetime.strptime(filters["from_date"], "%Y-%m-%d")
	to_date = datetime.strptime(filters["to_date"], "%Y-%m-%d")
	
	# Generate fiscal year columns for grouping
	years = get_fiscal_year_labels(from_date, to_date)
	
	# Determine the aggregation field and conditions based on aggregation_fact
	aggregation_fact = filters.get("aggregation_fact", "Sale Amount")
	
	if aggregation_fact == "Sale Amount":
		# Use line_item_amount for aggregation
		aggregation_field = "srli.line_item_amount"
		additional_conditions = ""
		select_fields = "sr.distributor as distributor"
	elif aggregation_fact == "Customer Count":
		# Use COUNT(DISTINCT retailer) for aggregation
		aggregation_field = "COUNT(DISTINCT sr.retailer)"
		additional_conditions = ""
		select_fields = "sr.distributor as distributor"
	elif aggregation_fact == "Avg Order Value":
		# Use (SUM(line_item_amount)/COUNT(DISTINCT retailer))/number_of_months for aggregation
		# For yearly, we'll calculate the average across all years
		aggregation_field = "(SUM(srli.line_item_amount)/COUNT(DISTINCT sr.retailer))/12"
		additional_conditions = ""
		select_fields = "sr.distributor as distributor"
	elif aggregation_fact:
		# Use converted_quantity for aggregation with company_item filter
		aggregation_field = "srli.converted_quantity"
		additional_conditions = " AND srli.company_item = %(company_item)s"
		values["company_item"] = aggregation_fact
		select_fields = "sr.distributor as distributor, srli.company_item as company_item"
	else:
		# Default to item_quantity * item_rate
		aggregation_field = "srli.item_quantity * srli.item_rate"
		additional_conditions = ""
		select_fields = "sr.distributor as distributor"
	
	# Build year sum expressions
	year_sums = []
	for year_label, fieldname in years:
		parts = year_label.split()
		fy_years = parts[1].split("-")
		start_year = int(fy_years[0])
		end_year = int(fy_years[1])
		
		if aggregation_fact == "Customer Count":
			year_sums.append(f"COUNT(DISTINCT CASE WHEN (sr.sales_date >= '{start_year}-04-01' AND sr.sales_date <= '{end_year}-03-31') THEN sr.retailer ELSE NULL END) as `{fieldname}`")
		elif aggregation_fact == "Avg Order Value":
			year_sums.append(f"(SUM(CASE WHEN (sr.sales_date >= '{start_year}-04-01' AND sr.sales_date <= '{end_year}-03-31') THEN srli.line_item_amount ELSE 0 END)/COUNT(DISTINCT CASE WHEN (sr.sales_date >= '{start_year}-04-01' AND sr.sales_date <= '{end_year}-03-31') THEN sr.retailer ELSE NULL END))/12 as `{fieldname}`")
		else:
			year_sums.append(f"SUM(CASE WHEN (sr.sales_date >= '{start_year}-04-01' AND sr.sales_date <= '{end_year}-03-31') THEN {aggregation_field} ELSE 0 END) as `{fieldname}`")
	
	sql_query = f"""
		SELECT
			{select_fields},
			{', '.join(year_sums)}
			{f", SUM({aggregation_field}) as total" if aggregation_fact != 'Avg Order Value' and aggregation_fact != 'Customer Count' else ""}
		FROM
			`tabSales Record` sr
		INNER JOIN
			`tabSales Record Line Item` srli ON sr.name = srli.parent
		WHERE
			1=1 {conditions} {additional_conditions}
		GROUP BY
			sr.distributor{', srli.company_item' if aggregation_fact != 'Sale Amount' and aggregation_fact and aggregation_fact != 'Customer Count' and aggregation_fact != 'Avg Order Value' else ''}
		ORDER BY
			sr.distributor{', srli.company_item' if aggregation_fact != 'Sale Amount' and aggregation_fact and aggregation_fact != 'Customer Count' and aggregation_fact != 'Avg Order Value' else ''}
	"""
	
	data = frappe.db.sql(sql_query, values=values, as_dict=True)
	return data

@frappe.whitelist()
def get_company_items():
	"""Get list of company items for the select filter."""
	company_items = frappe.get_all("Company Item", fields=["name"], order_by="name")
	
	# Return list of item names
	items = [item.name for item in company_items]
	return items
