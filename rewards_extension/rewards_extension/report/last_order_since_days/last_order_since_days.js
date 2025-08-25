// Copyright (c) 2025, Vinod Kumar K and contributors
// For license information, please see license.txt

frappe.query_reports["Last Order since Days"] = {
	filters: [
		{
			"fieldname": "distributor",
			"label": __("Distributor"),
			"fieldtype": "Link",
			"options": "Distributor Profile",
			"reqd": 1,
		},
	],
};
