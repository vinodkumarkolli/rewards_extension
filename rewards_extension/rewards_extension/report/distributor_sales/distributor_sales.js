// Copyright (c) 2025, Vinod Kumar K and contributors
// For license information, please see license.txt

frappe.query_reports["Distributor Sales"] = {
	filters: [
		{
			"fieldname": "distributor",
			"label": __("Distributor"),
			"fieldtype": "Link",
			"options":"Distributor Profile"
		},
		{
			"fieldname":"from_date",
			"label":__("From Date"),
			"fieldtype":"Date",
			"reqd":1
		},
		{
			"fieldname":"to_date",
			"label":__("To Date"),
			"fieldtype":"Date",
			"reqd":1
		},
		{
			"fieldname":"aggregate_option",
			"label":__("Aggregate"),
			"fieldtype":"Select",
			"options":['Monthly','Quarterly','Yearly'],
			"default":"Monthly"
		}
	],
};
