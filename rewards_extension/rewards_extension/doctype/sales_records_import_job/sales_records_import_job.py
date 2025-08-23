# Copyright (c) 2025, Vinod Kumar K and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils.csvutils import read_csv_content
from frappe.utils import cint
import json
from datetime import datetime


class SalesRecordsImportJob(Document):
	def validate(self):
		pass


@frappe.whitelist()
def get_preview_from_template(doc):
	"""Get preview data from the uploaded template"""
	doc = frappe.parse_json(doc)
	sales_records_import_job = frappe.get_doc("Sales Records Import Job", doc.name)
	sales_records_import_job.check_permission("read")
	
	# Implement the logic directly here instead of calling the class method
	if not sales_records_import_job.sales_records_file:
		return
	
	# Read the uploaded file
	file_doc = frappe.get_doc("File", {"file_url": sales_records_import_job.sales_records_file})
	content = file_doc.get_content()
	
	if isinstance(content, bytes):
		content = content.decode('utf-8')
	
	rows = read_csv_content(content)
	
	if not rows:
		return
	
	# Prepare preview data
	headers = rows[0]
	data = rows[1:6]  # First 5 rows of data
	
	# Get the table field name dynamically
	try:
		table_fields = frappe.get_meta("Sales Record").get_table_fields()
		table_field_name = table_fields[0].fieldname if table_fields else "table_field_name"  # fallback to default
	except:
		table_field_name = "table_field_name"  # fallback to default
	
	# Prepare column mapping
	column_to_field_map = {}
	
	# Check if we have column mappings stored in template_warnings
	# Handle case where template_warnings field might contain column mapping data
	if hasattr(sales_records_import_job, 'template_warnings') and sales_records_import_job.template_warnings:
		try:
			template_warnings_data = json.loads(sales_records_import_job.template_warnings)
			if isinstance(template_warnings_data, dict) and "column_to_field_map" in template_warnings_data:
				column_to_field_map = template_warnings_data.get("column_to_field_map", {})
		except json.JSONDecodeError:
			pass
	
	# If no mappings exist, try to auto-map based on header names
	if not column_to_field_map:
		for i, header in enumerate(headers):
			# Map to standard fields if they match
			if header.lower() in ["item_name", "item_quantity", "item_rate", "free_quantity", "sales_date", "invoice", "outlet_name"]:
				if header.lower() in ["item_name", "item_quantity", "item_rate", "free_quantity"]:
					# For line item fields, use the prefixed name
					column_to_field_map[str(i)] = f"{table_field_name}.{header.lower()}"
				else:
					# For sales record fields, use the field name directly
					column_to_field_map[str(i)] = header.lower()
	
	# Generate warnings based on column mapping
	warnings = []
	
	# Define mandatory fields for Sales Record Line Item
	# Note: item_rate is mandatory (reqd: 1 in Sales Record Line Item doctype)
	mandatory_line_item_fields = [
		f"{table_field_name}.item_name",
		f"{table_field_name}.item_quantity",
		f"{table_field_name}.item_rate"
	]
	
	# Define mandatory fields for Sales Record (excluding distributor which is supplied by import job)
	mandatory_sales_record_fields = ["sales_date", "invoice", "outlet_name"]
	
	# Check for missing mandatory line item fields based on column mapping
	mapped_fields = list(column_to_field_map.values())
	missing_line_item_fields = [field for field in mandatory_line_item_fields if field not in mapped_fields]
	
	if missing_line_item_fields:
		warnings.append({
			"message": f"Missing mandatory line item fields: {', '.join(missing_line_item_fields)}",
			"row": 0
		})
	
	# Check for missing mandatory Sales Record fields based on column mapping
	# (excluding distributor which is supplied by the import job)
	missing_sales_record_fields = [field for field in mandatory_sales_record_fields if field not in mapped_fields]
	
	if missing_sales_record_fields:
		warnings.append({
			"message": f"Missing mandatory sales record fields: {', '.join(missing_sales_record_fields)}",
			"row": 0
		})
	
	# Validate sales_date column if it exists
	sales_date_column_index = None
	for index, field_name in column_to_field_map.items():
		if field_name == "sales_date":
			sales_date_column_index = int(index)
			break
	
	if sales_date_column_index is not None and sales_date_column_index < len(headers):
		# Check if sales_date values are within from_date and to_date range
		from_date = sales_records_import_job.from_date
		to_date = sales_records_import_job.to_date
		
		if from_date and to_date:
			# Check data rows for sales_date values
			for row_index, row in enumerate(rows[1:], 1):  # Skip header row
				if sales_date_column_index < len(row):
					sales_date_value = row[sales_date_column_index]
					if sales_date_value:
						try:
							from datetime import datetime
							# Try multiple date formats
							date_formats = ["%Y-%m-%d", "%d-%m-%Y", "%m-%d-%Y", "%d/%m/%Y", "%m/%d/%Y"]
							sales_date = None
							
							for date_format in date_formats:
								try:
									sales_date = datetime.strptime(sales_date_value, date_format).date()
									break
								except ValueError:
									continue
							
							if sales_date is None:
								# Invalid date format
								warnings.append({
									"message": f"Invalid date format {sales_date_value} in row {row_index+1} for sales_date column",
									"row": row_index+1
								})
							else:
								from_date_obj = datetime.strptime(str(from_date), "%Y-%m-%d").date()
								to_date_obj = datetime.strptime(str(to_date), "%Y-%m-%d").date()
								
								if sales_date < from_date_obj or sales_date > to_date_obj:
									warnings.append({
										"message": f"Sales date {sales_date_value} in row {row_index+1} is not within the selected date range ({from_date} to {to_date})",
										"row": row_index+1
									})
						except Exception as e:
							# Any other error
							warnings.append({
								"message": f"Invalid date format {sales_date_value} in row {row_index+1} for sales_date column",
								"row": row_index+1
							})
	
	preview_data = {
		"columns": headers,
		"data": data,
		"column_to_field_map": column_to_field_map,
		"warnings": warnings
	}
	
	return preview_data


@frappe.whitelist()
def get_import_logs(doc):
	"""Get import logs for this job"""
	doc = frappe.parse_json(doc)
	sales_records_import_job = frappe.get_doc("Sales Records Import Job", doc.name)
	sales_records_import_job.check_permission("read")
	
	# Get import logs
	logs = []
	if hasattr(sales_records_import_job, 'import_log') and sales_records_import_job.import_log:
		try:
			logs = json.loads(sales_records_import_job.import_log)
		except json.JSONDecodeError:
			pass
	
	# Filter logs if show_failed_logs is checked
	if sales_records_import_job.show_failed_logs:
		logs = [log for log in logs if not log.get("success", False)]
	
	return logs


@frappe.whitelist()
def start_import(doc):
	"""Start the import process"""
	doc = frappe.parse_json(doc)
	sales_records_import_job = frappe.get_doc("Sales Records Import Job", doc.name)
	sales_records_import_job.check_permission("write")
	
	# Implement the logic directly here instead of calling the class method
	# Set scheduled time to now
	sales_records_import_job.scheduled_time = frappe.utils.now_datetime()
	
	# Save and submit the document
	sales_records_import_job.save()
	sales_records_import_job.submit()
	
	# Start the actual import process
	try:
		import_sales_records(sales_records_import_job)
		sales_records_import_job.db_set("status", "Completed")
		sales_records_import_job.db_set("job_completion_time", frappe.utils.now_datetime())
		frappe.msgprint("Import process completed successfully")
	except Exception as e:
		sales_records_import_job.db_set("status", "Failed")
		sales_records_import_job.db_set("job_completion_time", frappe.utils.now_datetime())
		frappe.log_error(f"Sales Records Import Job {sales_records_import_job.name} failed: {str(e)}")
		frappe.msgprint(f"Import process failed: {str(e)}")
	
	return True


def import_sales_records(sales_records_import_job):
	"""Import sales records from the uploaded CSV file"""
	if not sales_records_import_job.sales_records_file:
		frappe.throw("No sales records file attached")
	
	# Read the uploaded file
	file_doc = frappe.get_doc("File", {"file_url": sales_records_import_job.sales_records_file})
	content = file_doc.get_content()
	
	if isinstance(content, bytes):
		content = content.decode('utf-8')
	
	rows = read_csv_content(content)
	
	if not rows:
		frappe.throw("No data found in the uploaded file")
	
	# Get column mapping from template_warnings
	column_to_field_map = {}
	if hasattr(sales_records_import_job, 'template_warnings') and sales_records_import_job.template_warnings:
		try:
			template_warnings_data = json.loads(sales_records_import_job.template_warnings)
			if isinstance(template_warnings_data, dict) and "column_to_field_map" in template_warnings_data:
				column_to_field_map = template_warnings_data.get("column_to_field_map", {})
		except json.JSONDecodeError:
			pass
	
	# Get the table field name dynamically
	try:
		table_fields = frappe.get_meta("Sales Record").get_table_fields()
		table_field_name = table_fields[0].fieldname if table_fields else "table_field_name"  # fallback to default
	except:
		table_field_name = "table_field_name"  # fallback to default
	
	# Prepare headers and data
	headers = rows[0]
	data_rows = rows[1:]
	
	# Create a mapping from field names to column indices
	field_to_column_index = {field_name: int(col_index) for col_index, field_name in column_to_field_map.items()}
	
	# Get item conversion map for the distributor
	item_conversion_map = get_item_conversion_map(sales_records_import_job.distributor)
	
	# Group rows by common fields: sales_date, distributor, outlet_name, outlet_code, retailer, invoice
	grouped_rows = {}
	for row_index, row in enumerate(data_rows):
		# Extract common fields for grouping
		outlet_name = get_field_value(row, field_to_column_index, "outlet_name")
		outlet_code = get_field_value(row, field_to_column_index, "outlet_code", "")
		sales_date_str = get_field_value(row, field_to_column_index, "sales_date")
		sales_date = parse_date_string(sales_date_str) if sales_date_str else None
		invoice = get_field_value(row, field_to_column_index, "invoice")
		
		# Create a key for grouping
		group_key = (sales_date, sales_records_import_job.distributor, outlet_name, outlet_code, invoice)
		
		# Add row to the appropriate group
		if group_key not in grouped_rows:
			grouped_rows[group_key] = {
				"row_data": row,
				"row_index": row_index,
				"line_items": []
			}
		# Add the row to the line_items list for this group
		grouped_rows[group_key]["line_items"].append((row, row_index))
	
	# Initialize import log
	import_logs = []
	
	# Process each group
	for group_key, group_data in grouped_rows.items():
		row = group_data["row_data"]
		row_index = group_data["row_index"]
		line_items_data = group_data["line_items"]
		
		try:
			# Create or get Master Retail Profile
			outlet_name = get_field_value(row, field_to_column_index, "outlet_name")
			outlet_code = get_field_value(row, field_to_column_index, "outlet_code", "")
			sales_date_str = get_field_value(row, field_to_column_index, "sales_date")
			sales_date = parse_date_string(sales_date_str) if sales_date_str else None
			
			# Validate that we have a proper date
			if sales_date_str and not sales_date:
				error_msg = f"Row {row_index + 2}: Invalid date format {sales_date_str}"
				import_logs.append({
					"row_number": row_index + 2,
					"success": False,
					"message": error_msg
				})
				frappe.log_error(error_msg)
				continue
			
			if not outlet_name:
				error_msg = f"Row {row_index + 2}: Missing outlet name"
				import_logs.append({
					"row_number": row_index + 2,
					"success": False,
					"message": error_msg
				})
				frappe.log_error(error_msg)
				continue
			
			retailer_profile = create_or_get_retailer_profile(outlet_name, outlet_code, sales_date, sales_records_import_job.distributor)
			
			# Create Sales Record
			sales_record = frappe.new_doc("Sales Record")
			sales_record.distributor = sales_records_import_job.distributor
			if sales_date:
				sales_record.sales_date = sales_date
			sales_record.invoice = get_field_value(row, field_to_column_index, "invoice")
			sales_record.outlet_name = outlet_name
			sales_record.outlet_code = outlet_code
			sales_record.retailer = retailer_profile.name
			
			# Set other optional fields if they exist in the mapping
			agent_code = get_field_value(row, field_to_column_index, "agent_code")
			if agent_code:
				sales_record.agent_code = agent_code
			
			# Create Sales Record Line Items for all rows in this group
			all_line_items = []
			for line_item_row, line_item_row_index in line_items_data:
				line_items = create_sales_record_line_items(line_item_row, field_to_column_index, table_field_name, item_conversion_map)
				all_line_items.extend(line_items)
			
			# If no valid line items, skip this group
			if not all_line_items:
				error_msg = f"Group with invoice {sales_record.invoice}: No valid line items found or item names don't match distributor conversion records"
				import_logs.append({
					"row_number": row_index + 2,
					"success": False,
					"message": error_msg
				})
				frappe.log_error(error_msg)
				continue
			
			sales_record.set(table_field_name, all_line_items)
			
			# Save and submit the sales record
			sales_record.insert()
			sales_record.submit()
			
			# Update retailer's first and last purchase dates
			if sales_date and retailer_profile:
				# Update first purchase date if sales_date is earlier
				if not retailer_profile.first_purchase_date or sales_date < retailer_profile.first_purchase_date:
					retailer_profile.first_purchase_date = sales_date
				
				# Update last purchase date if sales_date is later
				if not retailer_profile.last_purchase_date or sales_date > retailer_profile.last_purchase_date:
					retailer_profile.last_purchase_date = sales_date
				
				# Save the retailer profile if any changes were made
				if retailer_profile.first_purchase_date or retailer_profile.last_purchase_date:
					retailer_profile.save()
			
			# Log success
			import_logs.append({
				"row_number": row_index + 2,
				"success": True,
				"message": f"Sales Record {sales_record.name} created successfully with {len(all_line_items)} line items"
			})
			
		except Exception as e:
			error_msg = f"Error processing group with invoice {get_field_value(row, field_to_column_index, 'invoice')}: {str(e)}"
			import_logs.append({
				"row_number": row_index + 2,
				"success": False,
				"message": error_msg
			})
			frappe.log_error(error_msg)
			continue
	
	# Save import logs to the document
	sales_records_import_job.db_set("import_log", json.dumps(import_logs))


def get_field_value(row, field_to_column_index, field_name, default=None):
	"""Get field value from row based on column mapping"""
	column_index = field_to_column_index.get(field_name)
	if column_index is not None and column_index < len(row):
		return row[column_index]
	return default


def create_or_get_retailer_profile(outlet_name, outlet_code, sales_date, distributor):
	"""Create or get Master Retail Profile based on outlet name"""
	# Check if a Master Retail Profile already exists with this outlet name in alias_names
	retailer_profiles = frappe.get_all("Master Retail Profile", filters={"alias_names": ["like", f"%{outlet_name}%"]})
	
	if retailer_profiles:
		# Retailer profile exists, return the first one
		return frappe.get_doc("Master Retail Profile", retailer_profiles[0].name)
	
	# Check if a Master Retail Profile already exists with this outlet name as retailer_name
	retailer_profiles = frappe.get_all("Master Retail Profile", filters={"retailer_name": outlet_name})
	
	if retailer_profiles:
		# Retailer profile exists, update alias_names and return
		retailer_profile = frappe.get_doc("Master Retail Profile", retailer_profiles[0].name)
		
		# Add outlet_name to alias_names if not already present
		alias_names = retailer_profile.alias_names.split("\n") if retailer_profile.alias_names else []
		if outlet_name not in alias_names:
			alias_names.append(outlet_name)
			retailer_profile.alias_names = "\n".join(alias_names)
			retailer_profile.save()
		
		return retailer_profile
	
	# No existing profile found, create a new one
	retailer_profile = frappe.new_doc("Master Retail Profile")
	retailer_profile.retailer_name = outlet_name
	retailer_profile.outlet_code = outlet_code
	if sales_date:
		retailer_profile.first_purchase_date = sales_date
		retailer_profile.last_purchase_date = sales_date
	retailer_profile.category = "Bronze"
	retailer_profile.distributor = distributor
	retailer_profile.alias_names = outlet_name  # Initialize with the outlet name
	
	retailer_profile.insert()
	
	return retailer_profile


def parse_date_string(date_string):
	"""Parse date string into proper date format"""
	if not date_string:
		return None
	
	# Try multiple date formats
	date_formats = ["%Y-%m-%d", "%d-%m-%Y", "%m-%d-%Y", "%d/%m/%Y", "%m/%d/%Y"]
	
	for date_format in date_formats:
		try:
			return datetime.strptime(date_string, date_format).date()
		except ValueError:
			continue
	
	# If none of the formats work, return None
	return None


def get_item_conversion_map(distributor):
	"""Get item conversion map for the distributor"""
	item_conversion_map = {}
	
	try:
		distributor_doc = frappe.get_doc("Distributor Profile", distributor)
		for conversion in distributor_doc.item_conversion_table:
			item_conversion_map[conversion.item_name] = {
				"company_item": conversion.company_item,
				"conversion_rate": conversion.conversion_rate
			}
	except Exception as e:
		frappe.log_error(f"Error getting item conversion map for distributor {distributor}: {str(e)}")
	
	return item_conversion_map


def create_sales_record_line_items(row, field_to_column_index, table_field_name, item_conversion_map):
	"""Create Sales Record Line Items from row data"""
	line_items = []
	
	# Extract line item fields
	item_names = get_field_value(row, field_to_column_index, f"{table_field_name}.item_name")
	item_quantities = get_field_value(row, field_to_column_index, f"{table_field_name}.item_quantity")
	item_rates = get_field_value(row, field_to_column_index, f"{table_field_name}.item_rate")
	free_quantities = get_field_value(row, field_to_column_index, f"{table_field_name}.free_quantity", 0)
	
	# For simplicity, assuming these are single values for now
	# In a real implementation, you might need to handle multiple line items per row
	if item_names and item_quantities and item_rates:
		# Handle case where these might be arrays or single values
		if not isinstance(item_names, list):
			item_names = [item_names]
		if not isinstance(item_quantities, list):
			item_quantities = [item_quantities]
		if not isinstance(item_rates, list):
			item_rates = [item_rates]
		if not isinstance(free_quantities, list):
			free_quantities = [free_quantities]
		
		# Process each item
		for i in range(len(item_names)):
			if i < len(item_quantities) and i < len(item_rates):
				item_name = item_names[i]
				item_quantity = float(item_quantities[i]) if item_quantities[i] else 0
				item_rate = float(item_rates[i]) if item_rates[i] else 0
				free_quantity = float(free_quantities[i]) if i < len(free_quantities) and free_quantities[i] else 0
				
				# Check if item_name exists in conversion map
				if item_name not in item_conversion_map:
					# Item name doesn't match any conversion record, skip this item
					frappe.log_error(f"Item name '{item_name}' not found in distributor conversion records")
					continue
				
				line_item = frappe.new_doc("Sales Record Line Item")
				line_item.item_name = item_name
				line_item.item_quantity = item_quantity
				line_item.item_rate = item_rate
				line_item.free_quantity = free_quantity
				line_item.line_item_amount = item_quantity * item_rate
				
				# Apply item conversion if available
				if item_name in item_conversion_map:
					conversion = item_conversion_map[item_name]
					line_item.company_item = conversion["company_item"]
					line_item.conversion_rate = conversion["conversion_rate"]
					line_item.converted_quantity = item_quantity * conversion["conversion_rate"]
				
				line_items.append(line_item)
	
	return line_items


@frappe.whitelist()
def export_errored_rows(doc, file_type="Excel"):
	"""Export errored rows to an Excel or CSV file"""
	from frappe.utils.xlsxutils import make_xlsx
	from io import StringIO, BytesIO
	import csv

	doc = frappe.parse_json(doc)
	srij = frappe.get_doc("Sales Records Import Job", doc.name)
	srij.check_permission("read")

	if not srij.import_log:
		frappe.msgprint("No import log found.")
		return

	logs = json.loads(srij.import_log)
	failed_logs = [log for log in logs if not log.get("success")]

	if not failed_logs:
		frappe.msgprint("No errored rows to export.")
		return

	# Read the original imported file
	file_doc = frappe.get_doc("File", {"file_url": srij.sales_records_file})
	content = file_doc.get_content()
	if isinstance(content, bytes):
		content = content.decode('utf-8')

	rows = read_csv_content(content)
	headers = rows[0]
	data_rows = rows[1:]

	errored_data = []
	errored_data.append(headers + ["Error"])
	for log in failed_logs:
		row_number = log.get("row_number")
		if row_number and (row_number - 2) >= 0 and (row_number - 2) < len(data_rows):
			row_data = list(data_rows[row_number - 2]) # Get a copy
			row_data.append(log.get("message", "Unknown error"))
			errored_data.append(row_data)

	if len(errored_data) <= 1:
		frappe.msgprint("Could not retrieve data for errored rows.")
		return

	# Generate the file
	if file_type == "Excel":
		xlsx_file = make_xlsx(errored_data[1:], errored_data[0])
		file_content = xlsx_file.getvalue()
		file_extension = "xlsx"
	else:  # CSV
		output = StringIO()
		writer = csv.writer(output)
		for row in errored_data:
			writer.writerow(row)
		file_content = output.getvalue().encode('utf-8')
		file_extension = "csv"

	# Create a new File document
	file_name = f"errored_rows_{srij.name}.{file_extension}"
	new_file = frappe.new_doc("File")
	new_file.file_name = file_name
	new_file.attached_to_doctype = "Sales Records Import Job"
	new_file.attached_to_name = srij.name
	new_file.content = file_content
	new_file.is_private = 1
	new_file.save()

	frappe.response["message"] = {
		"file_name": new_file.file_name,
		"file_url": new_file.file_url
	}
