// Copyright (c) 2025, Vinod Kumar K and contributors
// For license information, please see license.txt
frappe.ui.form.on("Voucher Campaign", {
    before_save(frm){
        if(frm.doc.end_date<frm.doc.start_date){
            frappe.throw(__("End Date cannot be less than Start Date"))
        }
    },
    refresh(frm){
        if(frm.doc.docstatus === 1){
            if(frm.doc.campaign_status == 'Active'){
                addHoldButton(frm)
                addVoucherBatchButtons(frm)
                frm.add_custom_button(__('Hard Activate Disabled Coupons'), function(){
                    hardActivateDisabledCoupons(frm);
                }, __('Campaign Status'));
            }
            if(frm.doc.campaign_status == 'Held'){
                addActivateButton(frm)
                addDeleteCampaignButton(frm)
                // addVoucherBatchButtons(frm)
            }
        }
        frm.page.btn_secondary.hide();
    },
    base_voucher_price(frm) {
        frm.set_value("campaign_budget",frm.doc.base_voucher_price * frm.doc.voucher_count)
	},
    voucher_count(frm){
        frm.set_value("campaign_budget",frm.doc.base_voucher_price * frm.doc.voucher_count)
    },
});

function addVoucherBatchButtons(frm){
    const now = moment();
    const endDate = moment(frm.doc.end_date);
    // const startDate = moment(frm.doc.start_date);
    if(now.isBefore(endDate)){
        frm.add_custom_button(__('Create a Batch'),function(){
            openBatchPopup(frm)
        },__('Voucher Batch'))
        //Check for Pending Inactivated Batches
        frappe.call({
            method:'rewards_extension.rewards_extension.doctype.voucher_campaign.voucher_campaign.get_pending_batches',
            args:{
                campaign:frm.doc.name
            },
            callback:function(r){
                if(!r.exc){
                    //refresh_field('status');
                    // console.log(r.message);
                    if(r.message.length>0){
                        frm.add_custom_button(__('Activate Voucher Batch'),function(){
                            addBatchActivationForm(frm,r.message)
                        },__('Voucher Batch'))
                    }
                }
            }
        })
    }
}
function addBatchActivationForm(frm,options){
    d = new frappe.ui.Dialog({
        'title': __('Activate Voucher Batch'),
        'fields':[{
            'fieldname':'batch',
            'fieldtype':'Select',
            'label':'Batch Name',
            'options':options,
            'reqd':1,
        }],
        'primary_action_label':__('Activate'),
        'primary_action': function() {
            var batch = d.get_value('batch');
            frappe.call({
                method:'rewards_extension.rewards_extension.doctype.voucher_campaign.voucher_campaign.activate_pending_batch',
                args:{
                    batch:batch,
                    campaign:frm.doc.name
                },
                callback:function(r){
                    if(!r.exc){
                        //refresh_field('status');
                        d.hide();
                    }
                }
            })
        }
    })
    d.show();
}
function openBatchPopup(frm){
    d = new frappe.ui.Dialog({
        'title': __('Create Voucher Batch'),
        'fields':[{
            'fieldname': "my_note",
            'fieldtype': "HTML", // Or "Text" if you just need plain text
            'options': "<p>Create batch with less than or equal to 500 Vouchers</p>", // Your note text
            'label': "Note" // Optional label for the note field
        },
        {
            'fieldname':'count',
            'fieldtype':'Int',
            'label':'No. of vouchers to create',
            'reqd':1,
        }],
        primary_action:function(){
            //hide fields in the Dialog d, show frappe progress bar
            var count = d.get_value('count');
            
            // Hide all fields in the dialog
            d.hide();
            
            // Show Frappe progress bar
            frappe.show_progress(__('Creating Vouchers'), 0, count, __('Please wait...'));
            
            frappe.call({
                method:'rewards_extension.rewards_extension.doctype.voucher_campaign.voucher_campaign.create_voucher_batch',
                args:{
                    campaign:frm.doc.name,
                    count:count
                },
                callback:function(r){
                    if(!r.exc){
                        // Close progress bar
                        frappe.hide_progress();
                        // Show message that vouchers are being created in background
                        if(r.message && r.message.status === "enqueued") {
                            frappe.show_alert({
                                message: __('Creating {0} vouchers in background. This may take a few minutes.', [r.message.count]),
                                indicator: 'green'
                            });
                        } else {
                            frappe.show_alert({
                                message: __('Voucher batch created successfully'),
                                indicator: 'green'
                            });
                        }
                        //refresh_field('status');
                        d.hide();
                    } else {
                        frappe.show_alert({
                            message: __('Error creating voucher batch'),
                            indicator: 'red'
                        });
                    }
                }
            });
            // alert('Creating '+count+' vouchers')
        }
    })
    d.show()
}
function addHoldButton(frm){
    frm.add_custom_button(__('Disable Campaign'),function(){
        // Get total number of vouchers for this campaign to set up progress bar
        frappe.call({
            method: 'frappe.client.get_count',
            args: {
                doctype: 'Gift Voucher',
                filters: {
                    campaign: frm.doc.name
                }
            },
            callback: function(r) {
                if (r.message) {
                    var total_vouchers = r.message;
                    // Show progress bar
                    frappe.show_progress(__('Disabling Vouchers'), 0, total_vouchers, __('Please wait...'));
                } else {
                    // Fallback to a generic progress bar if we can't get the count
                    frappe.show_progress(__('Disabling Vouchers'), 0, 100, __('Please wait...'));
                }
                
                frappe.call({
                    method:'rewards_extension.rewards_extension.doctype.voucher_campaign.voucher_campaign.change_campaign_status',
                    args:{
                        campaign:frm.doc.name,
                        status:'Held'
                    },
                    callback:function(r){
                        // Close progress bar
                        frappe.hide_progress();
                        if(!r.exc){
                            //refresh_field('status');
                            frappe.show_alert({
                                message: __('Campaign disabled successfully'),
                                indicator: 'green'
                            });
                            frm.reload_doc();
                        } else {
                            frappe.show_alert({
                                message: __('Error disabling campaign'),
                                indicator: 'red'
                            });
                        }
                    }
                })
            }
        });
        // frm.set_value('campaign_status','Held')
        // frm.save()
    },__('Campaign Status'))
}
function addActivateButton(frm){
    frm.add_custom_button(__('Activate Campaign'),function(){
        // Get total number of vouchers for this campaign to set up progress bar
        frappe.call({
            method: 'frappe.client.get_count',
            args: {
                doctype: 'Gift Voucher',
                filters: {
                    campaign: frm.doc.name
                }
            },
            callback: function(r) {
                if (r.message) {
                    var total_vouchers = r.message;
                    // Show progress bar
                    frappe.show_progress(__('Activating Vouchers'), 0, total_vouchers, __('Please wait...'));
                } else {
                    // Fallback to a generic progress bar if we can't get the count
                    frappe.show_progress(__('Activating Vouchers'), 0, 100, __('Please wait...'));
                }
                
                frappe.call({
                    method:'rewards_extension.rewards_extension.doctype.voucher_campaign.voucher_campaign.change_campaign_status',
                    args:{
                        campaign:frm.doc.name,
                        status:'Active'
                    },
                    callback:function(r){
                        // Close progress bar
                        frappe.hide_progress();
                        if(!r.exc){
                            //refresh_field('status');
                            frappe.show_alert({
                                message: __('Campaign activated successfully'),
                                indicator: 'green'
                            });
                            frm.reload_doc();
                        } else {
                            frappe.show_alert({
                                message: __('Error activating campaign'),
                                indicator: 'red'
                            });
                        }
                    }
                })
            }
        });
        // frm.set_value('campaign_status','Active')
        // frm.save()
    },__('Campaign Status'))
}

function addDeleteCampaignButton(frm){
    // Check if all associated Gift Vouchers are in 'Disabled' status
    frappe.call({
        method: 'rewards_extension.rewards_extension.doctype.voucher_campaign.voucher_campaign.can_delete_campaign',
        args: {
            campaign: frm.doc.name
        },
        callback: function(r) {
            if (r.message) {
                // All vouchers are disabled, show the delete button
                frm.add_custom_button(__('Delete Campaign'), function(){
                    // Show danger prompt
                    frappe.confirm(
                        __('This action is irreversible and all associated data with the Campaign will be lost. Do you want to proceed?'),
                        function(){
                            // User clicked "Yes"
                            frappe.call({
                                method: 'rewards_extension.rewards_extension.doctype.voucher_campaign.voucher_campaign.delete_campaign',
                                args: {
                                    campaign: frm.doc.name
                                },
                                freeze: true,
                                freeze_message: __('Deleting Campaign...'),
                                callback: function(r) {
                                    if (!r.exc) {
                                        // Success - redirect to list view
                                        frappe.show_alert({
                                            message: __('Campaign deleted successfully'),
                                            indicator: 'green'
                                        });
                                        frappe.set_route('List', 'Voucher Campaign');
                                    } else {
                                        // Error occurred
                                        frappe.show_alert({
                                            message: __('Error deleting campaign'),
                                            indicator: 'red'
                                        });
                                    }
                                }
                            });
                        },
                        function(){
                            // User clicked "No" - do nothing
                        }
                    );
                }, __('Campaign Status'));
            }
        }
    });
}
function hardActivateDisabledCoupons(frm) {
    // Show confirmation dialog
    frappe.confirm(
        __('This will enable the first 500 disabled coupons linked to this campaign. Do you want to proceed?'),
        function() {
            // User clicked "Proceed"
            frappe.call({
                method: 'rewards_extension.rewards_extension.doctype.voucher_campaign.voucher_campaign.hard_activate_disabled_coupons',
                args: {
                    campaign: frm.doc.name
                },
                freeze: true,
                freeze_message: __('Activating coupons...'),
                callback: function(r) {
                    if (!r.exc) {
                        frappe.show_alert({
                            message: __('{0} coupons activated successfully', [r.message]),
                            indicator: 'green'
                        });
                        frm.reload_doc();
                    } else {
                        frappe.show_alert({
                            message: __('Error activating coupons'),
                            indicator: 'red'
                        });
                    }
                }
            });
        },
        function() {
            // User clicked "Cancel" - do nothing
        }
    );
}