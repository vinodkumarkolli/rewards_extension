// Copyright (c) 2025, Vinod Kumar K and contributors
// For license information, please see license.txt

frappe.query_reports["Distributor Sales Overview by Retailer"] = {
	filters: [
		{
			"fieldname": "distributor",
			"label": __("Distributor"),
			"fieldtype": "Link",
			"options":"Distributor Profile"
		},
		{
			"fieldname": "agent_code",
			"label": __("Agent"),
			"fieldtype": "Select",
			"options": [""],
			"depends_on": "distributor",
		},
		{
			"fieldname":"aggregation_fact",
			"label":__("Fact Column"),
			"fieldtype":"Select",
			"options": ["Sale Amount", "Order Count", "Avg Order Value"],
			"default": "Sale Amount",
			"reqd":1
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
				method: "rewards_extension.rewards_extension.report.distributor_sales_overview_by_retailer.distributor_sales_overview_by_retailer.get_company_items",
				callback: function(r) {
					if (r.message && r.message.length > 0) {
						// Add company items to the options after "Sale Amount", "Customer Count", and "Avg Order Value"
						var options = ["Sale Amount", "Order Count", "Avg Order Value"];
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
			
			// Update agent_code filter based on selected distributor
			var distributor_filter = report.filters.find(function(filter) {
				return filter.df.fieldname === "distributor";
			});
			
			if (distributor_filter) {
				// Add event listener to distributor filter
				distributor_filter.$input.on("change", function() {
					var distributor = distributor_filter.get_value();
					if (distributor) {
						// Fetch agent codes for the selected distributor
						frappe.call({
							method: "rewards_extension.rewards_extension.report.distributor_sales_overview_by_retailer.distributor_sales_overview_by_retailer.get_agent_codes",
							args: {
								distributor: distributor
							},
							callback: function(r) {
								if (r.message) {
									// Update the options for the agent_code filter
									var agent_code_filter = report.filters.find(function(filter) {
										return filter.df.fieldname === "agent_code";
									});
									if (agent_code_filter) {
										// Add empty option at the beginning
										var options = [""];
										r.message.forEach(function(code) {
											options.push(code);
										});
										agent_code_filter.df.options = options;
										agent_code_filter.refresh();
									}
								}
							}
						});
					} else {
						// Clear agent_code options if no distributor is selected
						var agent_code_filter = report.filters.find(function(filter) {
							return filter.df.fieldname === "agent_code";
						});
						if (agent_code_filter) {
							agent_code_filter.df.options = [""];
							agent_code_filter.refresh();
						}
					}
				});
				
				// Trigger the change event if distributor already has a value
				if (distributor_filter.get_value()) {
					distributor_filter.$input.trigger("change");
				}
			}
		}
};
