// Copyright (c) 2025, Vinod Kumar K and contributors
// For license information, please see license.txt

frappe.query_reports["Invoice Search"] = {
	"filters": [
		{
			"fieldname": "inv_no",
			"label": __("Invoice Number"),
			"fieldtype": "Data",
			"reqd": 1
		}
	]
};
