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
			"fieldname":"aggregation_fact",
			"label":__("Fact Column"),
			"fieldtype":"Select",
			"options": ["Sale Amount", "Customer Count", "Avg Order Value"],
			"default": "Sale Amount"
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
	
	after_refresh: function(report) {
		// Fetch company items and update the aggregation_fact filter options
		frappe.call({
			method: "rewards_extension.rewards_extension.report.distributor_sales.distributor_sales.get_company_items",
			callback: function(r) {
				if (r.message && r.message.length > 0) {
					// Add company items to the options after "Sale Amount", "Customer Count", and "Avg Order Value"
					var options = ["Sale Amount", "Customer Count", "Avg Order Value"];
					r.message.forEach(function(item) {
						// Add each company item to the options array
						options.push(item);
					});
					// Update the options for the aggregation_fact filter
					var aggregation_fact_filter = report.filters.find(function(filter) {
						return filter.df.fieldname === "aggregation_fact";
					});
					if (aggregation_fact_filter) {
						aggregation_fact_filter.df.options = options;
						aggregation_fact_filter.refresh();
					}
				}
			}
		});
	}
};
