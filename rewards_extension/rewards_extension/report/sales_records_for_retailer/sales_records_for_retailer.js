// Copyright (c) 2025, Vinod Kumar K and contributors
// For license information, please see license.txt

frappe.query_reports["Sales Records for Retailer"] = {
	filters: [
		{
			"fieldname": "distributor",
			"label": __("Distributor"),
			"fieldtype": "Link",
			"options":"Distributor Profile",
			// "reqd": 1,
		},
		{
			"fieldname":"retailer",
			"label":__("Retailer"),
			"fieldtype":"Link",
			"options":"Master Retail Profile",
			"reqd":1,
			"get_query": function() {
				var distributor = frappe.query_report.get_filter_value('distributor');
				return {
					"filters": {
						"distributor": distributor
					}
				}
			}
		},
		{
			"fieldname":"from_date",
			"label":__("From Date"),
			"fieldtype":"Date"
		},
		{
			"fieldname":"to_date",
			"label":__("To Date"),
			"fieldtype":"Date"
		}
	],
};
