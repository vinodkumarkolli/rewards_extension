// Copyright (c) 2025, Vinod Kumar K and contributors
// For license information, please see license.txt

frappe.query_reports["Active Campaign Links"] = {
	filters: [
		{
			"fieldname": "campaign",
			"label": __("Campaign"),
			"fieldtype": "Link",
			"options":"Voucher Campaign"
		},
		{
			"fieldname":"campaign_name",
			"label":__("Campaign Name"),
			"fieldtype":"Data"
		},
		{
			"fieldname":"campaign_status",
			"label":__("Campaign Status"),
			"fieldtype":"Select",
			"reqd":1,
			"default":"Active",
			"options": "Active\nHeld\nExpired"
		},
		{
			"fieldname":"campaign_target",
			"label":__("Campaign Target"),
			"fieldtype":"Select",
			"options": "Consumers\nRetailers\nWholesalers\nDistributors\nSales Persons"
		}
	],
};
