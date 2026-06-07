// Copyright (c) 2025, Vinod Kumar K and contributors
// For license information, please see license.txt

frappe.ui.form.on("Sales Records Import Job", {
	setup: function(frm) {
		// Set restrictions for the attach field
		frm.get_field("sales_records_file").df.options = {
			restrictions: {
				allowed_file_types: [".csv"],
			},
			folder: "Home/Sales Records Uploads",
		};
	},
	
	refresh: function(frm) {
		frm.trigger("update_indicators");
		frm.trigger("sales_records_file");
		frm.trigger("show_import_warnings");
		frm.trigger("show_import_log");
		
		// Listen for real-time updates
		if (!frm.is_new() && frappe.socket) {
			frappe.socket.on("sales_records_import_progress", function(data) {
				if (data.status === "Completed" || data.status === "Failed") {
					// Refresh the form to show updated status and import log
					frm.reload_doc();
				}
			});
		}
		
		// Add Export Errored Rows button if there are failed logs
		if (frm.doc.import_log) {
			try {
				let logs = JSON.parse(frm.doc.import_log);
				let failed_logs = logs.filter(log => !log.success);
				if (failed_logs.length > 0) {
					frm.add_custom_button(__("Export Errored Rows"), function() {
						frm.events.export_errored_rows(frm);
					});
				}
			} catch (e) {
				console.error("Error parsing import log:", e);
			}
		}
		// Set default values for from_date and to_date to last month's start and end dates
		if (!frm.doc.from_date) {
			frm.set_value("from_date", moment().subtract(1, 'months').startOf('month').format("YYYY-MM-DD"));
		}
		if (!frm.doc.to_date) {
			frm.set_value("to_date", moment().subtract(1, 'months').endOf('month').format("YYYY-MM-DD"));
		}
		// Clear standard primary actions
		frm.page.clear_primary_action();
		
		// Add Start Import button only if all mandatory fields are mapped
		if (!frm.is_new() && frm.doc.sales_records_file && frm.doc.docstatus === 0) {
			if (frm.events.are_all_mandatory_fields_mapped(frm)) {
				frm.add_custom_button(__("Start Import"), function() {
					frm.trigger("start_import");
				}).addClass("btn-primary");
			}
		}
		
		// Override standard cancel behavior and add custom cancel button for submitted documents
		if (!frm.is_new() && frm.doc.docstatus === 1) {
			// Remove standard cancel button
			frm.page.clear_secondary_action();
			
			// Add custom cancel button
			frm.page.set_secondary_action(__("Cancel"), function() {
				frm.trigger("custom_cancel");
			});
		}
		
		// Make scheduled_time and job_completion_time read-only
		frm.set_df_property("scheduled_time", "read_only", 1);
		frm.set_df_property("job_completion_time", "read_only", 1);
		
		// Listen for real-time updates for cancel process
		if (!frm.is_new() && frappe.socket) {
			frappe.socket.on("sales_records_cancel_progress", function(data) {
				if (data.status === "Completed" || data.status === "Failed") {
					// Refresh the form to show updated status
					frm.reload_doc();
				}
			});
		}
	},
	
	sales_records_file: function(frm) {
		frm.toggle_display("mapping_section_section", frm.doc.sales_records_file);
		if (!frm.doc.sales_records_file) {
			frm.get_field("import_preview").$wrapper.empty();
			return;
		}
		
		// Load import preview
		frm.get_field("import_preview").$wrapper.empty();
		$('<span class="text-muted">')
			.html(__("Loading import file..."))
			.appendTo(frm.get_field("import_preview").$wrapper);
		
		frappe.call({
			method: "rewards_extension.rewards_extension.doctype.sales_records_import_job.sales_records_import_job.get_preview_from_template",
			args: {
				doc: frm.doc
			},
			callback: function(r) {
				if (r.message) {
					frm.events.show_import_preview(frm, r.message);
					frm.events.show_import_warnings(frm, r.message);
				} else {
					frm.get_field("import_preview").$wrapper.empty();
					$('<span class="text-danger">')
						.html(__("Failed to load preview. Please ensure the CSV is valid and contains data."))
						.appendTo(frm.get_field("import_preview").$wrapper);
				}
			},
			error: function() {
				frm.get_field("import_preview").$wrapper.empty();
				$('<span class="text-danger">')
					.html(__("An error occurred while loading the preview."))
					.appendTo(frm.get_field("import_preview").$wrapper);
			}
		});
	},
	
	show_import_preview: function(frm, preview_data) {
		// Create a preview table using DataTable component
		let wrapper = frm.get_field("import_preview").$wrapper.empty();
		
		if (!preview_data || !preview_data.columns || !preview_data.columns.length || !preview_data.data) {
			$('<span class="text-warning">')
				.html(__("No valid columns or data rows found in the CSV file."))
				.appendTo(wrapper);
			return;
		}
		
		// Add actions section
		let actions_html = `
			<div class="table-actions margin-bottom">
				<button class="btn btn-sm btn-default show-column-mapper-btn">
					${__("Map Columns")}
				</button>
			</div>
		`;
		$(actions_html).appendTo(wrapper);
		
		// Create table preview container
		let table_container = $(`<div class="table-preview"></div>`).appendTo(wrapper);
		
		// Get column mapping from template_warnings (used to store column mappings)
		let column_to_field_map = {};
		if (frm.doc.template_warnings) {
			try {
				let template_warnings_data = JSON.parse(frm.doc.template_warnings);
				column_to_field_map = template_warnings_data.column_to_field_map || {};
			} catch (e) {
				console.error("Error parsing template_warnings for column mapping:", e);
			}
		}
		
		// Prepare columns for DataTable
		let columns = preview_data.columns.map((col, index) => {
			// Check if column is mapped
			let is_mapped = column_to_field_map.hasOwnProperty(index);
			let indicator_class = is_mapped ? "indicator green" : "indicator red";
			
			return {
				id: `column-${index}`,
				name: col,
				content: `<span class="${indicator_class}">${col}</span>`,
				editable: false,
				align: "left",
				width: 150
			};
		});
		
		// Prepare data for DataTable
		let data = preview_data.data.map(row => {
			return row.map(cell => {
				if (cell == null) {
					return "";
				}
				if (typeof cell === "string") {
					return frappe.utils.xss_sanitise(cell);
				}
				return cell;
			});
		});
		
		// Create DataTable
		if (frm.datatable) {
			frm.datatable.destroy();
		}
		
		frm.datatable = new DataTable(table_container.get(0), {
			data: data,
			columns: columns,
			layout: columns.length < 10 ? "fluid" : "fixed",
			cellHeight: 35,
			language: frappe.boot.lang,
			translations: frappe.utils.datatable.get_translations(),
			serialNoColumn: false,
			checkboxColumn: false,
			noDataMessage: __("No Data"),
			disableReorderColumn: true,
		});
		
		// Bind actions
		frappe.utils.bind_actions_with_object(wrapper, frm.events);
		
		// Explicitly bind the show_column_mapper action
		wrapper.find('.show-column-mapper-btn').on('click', function() {
			frm.events.show_column_mapper(frm);
		});
		
		// Add mapping section
		frm.events.add_mapping_section(frm, preview_data);
	},
	
	add_mapping_section: function(frm, preview_data) {
		// Add a section for column mapping info
		let wrapper = frm.get_field("import_preview").$wrapper;
		
		// Add a header for mapping
		$(`<h4 style="margin-top: 20px;">${__("Column Mapping")}</h4>`).appendTo(wrapper);
		
		// Add info text
		$(`<div class="text-muted">
			${__("Use the 'Map Columns' button above to map your CSV columns to fields.")}
		</div>`).appendTo(wrapper);
		
		// Show current mappings if they exist
		if (frm.doc.template_warnings) {
			try {
				let template_warnings_data = JSON.parse(frm.doc.template_warnings);
				let column_to_field_map = template_warnings_data.column_to_field_map || {};
				
				if (Object.keys(column_to_field_map).length > 0) {
					let mapping_html = `<table class="table table-bordered" style="margin-top: 10px;">
						<thead>
							<tr>
								<th>${__("Column")}</th>
								<th>${__("Mapped to Field")}</th>
							</tr>
						</thead>
						<tbody>`;
					
					// Add rows for each mapping
					preview_data.columns.forEach((column, index) => {
						let mapped_field = column_to_field_map[index] || __("Not mapped");
						if (mapped_field === "Don't Import") {
							mapped_field = __("Don't Import");
						}
						mapping_html += `<tr>
							<td>${column}</td>
							<td>${mapped_field}</td>
						</tr>`;
					});
					
					mapping_html += `</tbody></table>`;
					$(mapping_html).appendTo(wrapper);
				}
			} catch (e) {
				console.error("Error parsing template warnings for column mapping:", e);
			}
		}
	},
	
	show_column_mapper: function(frm) {
		if (!frm.doc.sales_records_file) {
			frappe.msgprint(__("Please attach a file before mapping columns."));
			return;
		}
		
		// Get preview data
		frappe.call({
			method: "rewards_extension.rewards_extension.doctype.sales_records_import_job.sales_records_import_job.get_preview_from_template",
			args: {
				doc: frm.doc
			},
			callback: function(r) {
				if (r.message) {
					frm.events.create_column_mapping_dialog(frm, r.message);
				}
			}
		});
	},
	
	create_column_mapping_dialog: function(frm, preview_data) {
		// Define the doctype for which we want to get fields
		let doctype = "Sales Record";
		
		// Ensure the doctype is loaded before proceeding
		frappe.model.with_doctype(doctype, () => {
			try {
				let fields = [];
				let changed = [];
				
				// Get column mapping from template_warnings (used to store column mappings)
				let column_to_field_map = {};
				if (frm.doc.template_warnings) {
					try {
						let template_warnings = JSON.parse(frm.doc.template_warnings);
						if (template_warnings.column_to_field_map) {
							column_to_field_map = template_warnings.column_to_field_map;
						}
					} catch (e) {
						console.error("Error parsing template_warnings for column mapping:", e);
					}
				}
				
				// Get fields for the doctype
				let column_picker_fields = get_columns_for_picker(doctype);
				
				// Get all available options
				let all_autocomplete_options = get_fields_as_options(doctype, column_picker_fields);
				
				// Create fields for each column
				preview_data.columns.forEach((column, i) => {
					// Get current mapping if exists
					let current_value = column_to_field_map[i] || "";
					
					// Get already selected values (excluding current one)
					let selected_values = [];
					for (let key in column_to_field_map) {
						if (key != i && column_to_field_map[key] && column_to_field_map[key] !== "Don't Import") {
							selected_values.push(column_to_field_map[key]);
						}
					}
					
					// Filter out already selected options
					let autocomplete_options = all_autocomplete_options.filter(option => {
						return !selected_values.includes(option.value) || option.value === current_value;
					});
					
					// Add column label field
					fields.push({
						label: "",
						fieldtype: "Data",
						default: column,
						fieldname: `Column ${i}`,
						read_only: 1,
					});
					
					// Add column break
					fields.push({
						fieldtype: "Column Break",
					});
					
					// Add autocomplete field
					fields.push({
						fieldtype: "Autocomplete",
						fieldname: i,
						label: "",
						max_items: Infinity,
						options: [
							{
								label: __("Don't Import"),
								value: "Don't Import",
							},
						].concat(autocomplete_options),
						default: current_value,
						onchange: function() {
							changed.push(i);
							// Update other dropdowns to remove selected value
							update_other_dropdowns(dialog, i, this.value, all_autocomplete_options);
						},
					});
					
					// Add section break
					fields.push({
						fieldtype: "Section Break",
					});
				});
				
				let dialog = new frappe.ui.Dialog({
					title: __("Map Columns"),
					fields: [
						{
							fieldtype: "HTML",
							fieldname: "heading",
							options: `
								<div class="margin-top text-muted">
								${__("Map columns from your file to fields")}
								</div>
							`,
						},
						{
							fieldtype: "Section Break",
						},
					].concat(fields),
					primary_action: (values) => {
						let changed_map = {};
						changed.map((i) => {
							changed_map[i] = values[i];
						});
						if (changed.length > 0) {
							frm.events.remap_column(frm, changed_map);
						}
						dialog.hide();
					},
				});
				dialog.$body.addClass("map-columns");
				dialog.show();
			} catch (error) {
				console.error("Error creating column mapping dialog:", error);
				frappe.msgprint(__("Error creating column mapping dialog. Please try again."));
			}
		});
	},
	
	remap_column: function(frm, changed_map) {
		// Store mapping in template_warnings field
		let column_mapping_data = {};
		if (frm.doc.template_warnings) {
			try {
				let template_warnings = JSON.parse(frm.doc.template_warnings);
				if (typeof template_warnings === 'object' && template_warnings !== null) {
					column_mapping_data = template_warnings;
				}
			} catch (e) {
				console.error("Error parsing template_warnings:", e);
			}
		}
		
		// Initialize column_to_field_map if it doesn't exist
		if (!column_mapping_data.column_to_field_map) {
			column_mapping_data.column_to_field_map = {};
		}
		
		// Update the column mapping
		Object.assign(column_mapping_data.column_to_field_map, changed_map);
		
		// Store the updated data in template_warnings
		frm.set_value("template_warnings", JSON.stringify(column_mapping_data));
		frm.save().then(() => {
			frm.trigger("sales_records_file");
			frm.refresh(); // Refresh to update Start Import button visibility
		});
	},
	
	show_import_warnings: function(frm, preview_data) {
		let warnings = [];
		
		// Get warnings from preview data
		if (preview_data && preview_data.warnings) {
			warnings = preview_data.warnings;
		}
		
		// Always show the section to ensure import_warnings field is visible
		frm.toggle_display("import_file_errors_and_warnings_section", true);
		
		if (warnings.length === 0) {
			frm.get_field("import_warnings").$wrapper.html("");
			return;
		}
		
		// Group warnings by row
		let warnings_by_row = {};
		let other_warnings = [];
		for (let warning of warnings) {
			if (warning.row) {
				warnings_by_row[warning.row] = warnings_by_row[warning.row] || [];
				warnings_by_row[warning.row].push(warning);
			} else {
				other_warnings.push(warning);
			}
		}
		
		let html = "";
		html += Object.keys(warnings_by_row)
			.map((row_number) => {
				let message = warnings_by_row[row_number]
					.map((w) => {
						return `<li>${w.message}</li>`;
					})
					.join("");
				return `
				<div class="warning" data-row="${row_number}">
					<h5 class="text-uppercase">${__("Row {0}", [row_number])}</h5>
					<div class="body"><ul>${message}</ul></div>
				</div>
			`;
			})
			.join("");
		
		html += other_warnings
			.map((warning) => {
				let header = "";
				if (preview_data && preview_data.columns && warning.col !== undefined) {
					let column_number = `<span class="text-uppercase">${__("Column {0}", [
						warning.col,
					])}</span>`;
					let column_header = preview_data.columns[warning.col];
					header = `${column_number} (${column_header})`;
				}
				return `
					<div class="warning" data-col="${warning.col}">
						<h5>${header}</h5>
						<div class="body">${warning.message}</div>
					</div>
				`;
			})
			.join("");
			
		frm.get_field("import_warnings").$wrapper.html(`
			<div class="row">
				<div class="col-sm-12 warnings">${html}</div>
			</div>
		`);
	},
	
	show_import_log: function(frm) {
		frm.toggle_display("import_log_section", false);
		
		if (frm.is_new()) {
			return;
		}
		
		frappe.call({
			method: "rewards_extension.rewards_extension.doctype.sales_records_import_job.sales_records_import_job.get_import_logs",
			args: {
				doc: frm.doc
			},
			callback: function(r) {
				if (r.message && r.message.length > 0) {
					frm.toggle_display("import_log_section", true);
					frm.events.render_import_log(frm, r.message);
				}
			}
		});
	},
	
	show_failed_logs: function(frm) {
		// Refresh the import log when show_failed_logs is changed
		frm.trigger("show_import_log");
	},
	
	custom_cancel: function(frm) {
		frappe.confirm(
			"Are you sure you want to cancel this import job? This will cancel and delete all imported Sales Records.",
			function() {
				// Call the standard cancel method which will trigger on_cancel
				frm.page.btn_secondary.prop('disabled', true);
				frappe.call({
					method: "frappe.client.cancel",
					args: {
						doctype: frm.doc.doctype,
						name: frm.doc.name
					},
					callback: function(r) {
						if (r.exc) {
							frm.page.btn_secondary.prop('disabled', false);
						} else {
							frm.refresh();
						}
					}
				});
			}
		);
	},
	
	render_import_log: function(frm, logs) {
		let wrapper = frm.get_field("import_log_preview").$wrapper.empty();
		
		let table = $(`<table class="table table-bordered">
			<thead>
				<tr>
					<th>${__("Row Number")}</th>
					<th>${__("Status")}</th>
					<th>${__("Message")}</th>
				</tr>
			</thead>
			<tbody>
				${logs.map(log => 
					`<tr>
						<td>${log.row_number || ""}</td>
						<td><span class="indicator ${log.success ? "green" : "red"}">${log.success ? __("Success") : __("Failure")}</span></td>
						<td>${log.message || ""}</td>
					</tr>`
				).join("")}
			</tbody>
		</table>`).appendTo(wrapper);
},
	
	start_import: function(frm) {
		frappe.call({
			method: "rewards_extension.rewards_extension.doctype.sales_records_import_job.sales_records_import_job.start_import",
			args: {
				doc: frm.doc
			},
			callback: function(r) {
				if (r.message) {
					// Refresh the form to show the updated status
					frm.reload_doc();
				}
			}
		});
	},
	
	
	update_indicators: function(frm) {
		// Update status indicators
	},
	
	are_all_mandatory_fields_mapped: function(frm) {
		// Get the table field name dynamically
		const table_fields = frappe.meta.get_table_fields("Sales Record");
		const table_field_name = table_fields.length > 0 ? table_fields[0].fieldname : "table_sfpd"; // fallback to default
		
		// Define mandatory fields for Sales Record Line Item
		// Note: item_rate is mandatory (reqd: 1 in Sales Record Line Item doctype)
		const mandatory_line_item_fields = [
			`${table_field_name}.item_name`,
			`${table_field_name}.item_quantity`,
			`${table_field_name}.item_rate`
		];
		
		// Define mandatory fields for Sales Record (excluding distributor which is supplied by import job)
		const mandatory_sales_record_fields = ["sales_date", "invoice", "outlet_name"];
		
		// Get column mapping from template_warnings (used to store column mappings)
		let column_to_field_map = {};
		if (frm.doc.template_warnings) {
			try {
				let template_warnings_data = JSON.parse(frm.doc.template_warnings);
				column_to_field_map = template_warnings_data.column_to_field_map || {};
			} catch (e) {
				console.error("Error parsing template_warnings for column mapping:", e);
			}
		}
		
		// Get mapped fields
		let mapped_fields = Object.values(column_to_field_map);
		
		// Check if all mandatory line item fields are mapped
		for (let field of mandatory_line_item_fields) {
			if (!mapped_fields.includes(field)) {
				return false;
			}
		}
		
		// Check if all mandatory Sales Record fields are mapped
		for (let field of mandatory_sales_record_fields) {
			if (!mapped_fields.includes(field)) {
				return false;
			}
		}
		
		return true;
	},

	export_errored_rows: function(frm) {
		const dialog = new frappe.ui.Dialog({
			title: __("Export Errored Rows"),
			fields: [
				{
					fieldname: "file_format",
					label: __("File Format"),
					fieldtype: "Select",
					options: ["Excel", "CSV"],
					default: "Excel",
					reqd: 1
				}
			],
			primary_action_label: __("Export"),
			primary_action: (values) => {
				frappe.call({
					method: "rewards_extension.rewards_extension.doctype.sales_records_import_job.sales_records_import_job.export_errored_rows",
					args: {
						doc: frm.doc,
						file_type: values.file_format
					},
					callback: function(r) {
						if (r.message) {
							const D = new frappe.ui.Dialog({
								title: "Export Successful",
								primary_action_label: "Download",
								primary_action: () => {
									window.open(r.message.file_url);
									D.hide();
								}
							});
							D.show();
						}
					}
				});
				dialog.hide();
			}
		});
		dialog.show();
	}
});
// Helper functions for column mapping
function get_columns_for_picker(doctype) {
	let out = {};
	
	const exportable_fields = (df) => {
		let keep = true;
		if (frappe.model.no_value_type.includes(df.fieldtype)) {
			keep = false;
		}
		if (["lft", "rgt"].includes(df.fieldname)) {
			keep = false;
		}
		if (df.is_virtual) {
			keep = false;
		}
		// Exclude ID fields and amended_from
		if (df.fieldname === "name" || df.fieldname === "amended_from") {
			keep = false;
		}
		// Exclude Distributor and Retailer fields
		if (df.fieldname === "distributor" || df.fieldname === "retailer") {
			keep = false;
		}
		// Exclude specified fields from Sales Record Line Item
		const excluded_fields = ["company_item", "conversion_rate", "converted_quantity", "converted_rate"];
		if (df.parent === "Sales Record Line Item" && excluded_fields.includes(df.fieldname)) {
			keep = false;
		}
		return keep;
	};
	
	// parent
	let doctype_fields = frappe.meta.get_docfields(doctype).filter(exportable_fields);
	
	out[doctype] = doctype_fields;
	
	// children
	const table_fields = frappe.meta.get_table_fields(doctype);
	table_fields.forEach((df) => {
		const cdt = df.options;
		const child_table_fields = frappe.meta.get_docfields(cdt).filter(exportable_fields);
		
		out[df.fieldname] = child_table_fields;
	});
	
	return out;
}

function get_fields_as_options(doctype, column_map) {
	let keys = [doctype];
	frappe.meta.get_table_fields(doctype).forEach((df) => {
		keys.push(df.fieldname);
	});
	// flatten array
	let result = [].concat(
		...keys.map((key) => {
			if (!column_map[key]) {
				return [];
			}
			return column_map[key].map((df) => {
				let label = __(df.label, null, df.parent);
				let value = df.fieldname;
				if (doctype !== key) {
					// For child table fields, get the table field label from the df object directly
					let table_field = frappe.meta.get_docfield(doctype, key);
					let table_field_label = (table_field && table_field.label) ? __(table_field.label) : __(key);
					label = `${__(df.label, null, df.parent)} (${table_field_label})`;
					value = `${key}.${df.fieldname}`;
				}
				// Add asterisk for mandatory fields
				if (df.reqd) {
					label = `${label} *`;
				}
				return {
					label,
					value,
					description: value,
				};
			});
		})
	);
	return result;
}

function update_other_dropdowns(dialog, current_field_index, selected_value, all_options) {
	// Get all field values
	let field_values = dialog.get_values();
	
	// Get already selected values
	let selected_values = [];
	for (let key in field_values) {
		if (key != current_field_index && field_values[key] && field_values[key] !== "Don't Import") {
			selected_values.push(field_values[key]);
		}
	}
	
	// Update options for all dropdowns
	for (let key in field_values) {
		if (key != current_field_index) {
			let field = dialog.get_field(key);
			if (field) {
				// Filter out already selected options
				let filtered_options = all_options.filter(option => {
					return !selected_values.includes(option.value) || option.value === field.value;
				});
				
				// Update the field options
				let options = [
					{
						label: __("Don't Import"),
						value: "Don't Import",
					},
					...filtered_options
				];
				
				// Set the options for the field
				field.df.options = options;
				field.refresh();
			}
		}
	}
}
