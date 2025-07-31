// Copyright (c) 2025, Vinod Kumar K and contributors
// For license information, please see license.txt

frappe.ui.form.on("Customer Profile", {
	refresh(frm) {
		// Fetch all addresses linked to this Customer Profile
		frappe.db.get_list('Address', {
		  filters: [
		      ['Dynamic Link', 'link_doctype', '=', 'Customer Profile'],
		      ['Dynamic Link', 'link_name', '=', frm.doc.name]
		  ],
		  fields: ['name', 'address_line1', 'address_line2', 'city', 'state', 'pincode', 'country']
}).then(addresses => {
			let htmlContent = '';
			
			if (addresses && addresses.length > 0) {
				addresses.forEach(address => {
					htmlContent += `
						<div class="address-card" style="border-radius: 8px; border: 1px solid #e0e0e0; padding: 15px; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
							<h6>${address.name}</h6>
							<p>${address.address_line1 || ''}</p>
							<p>${address.address_line2 || ''}</p>
							<p>${address.city || ''}</p>
							<p>${address.state || ''} ${address.pincode || ''}</p>
							<p>${address.country || ''}</p>
						</div>
					`;
				});
			} else {
				htmlContent = '<p>No addresses found</p>';
			}
			
			frm.set_df_property('address_html', 'options', htmlContent);
			frm.refresh_field('address_html');
		}).catch(error => {
			console.error('Error fetching addresses:', error);
			frm.set_df_property('address_html', 'options', '<p>Error loading addresses</p>');
			frm.refresh_field('address_html');
		});
	},
});
