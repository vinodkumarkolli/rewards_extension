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
            }
            if(frm.doc.campaign_status == 'Held'){
                addActivateButton(frm)
                // addVoucherBatchButtons(frm)
            }
        }
        frm.page.btn_secondary.hide();
        // frm.add_custom_button(__('Temporary Button'),function(){
        //     frappe.call({
        //     // method:'rewards_extension.rewards_extension.doctype.gift_voucher.gift_voucher.expire_old_vouchers',
        //     method:'rewards_extension.rewards_extension.doctype.voucher_campaign.voucher_campaign.expire_old_campaigns',
        //     args:{},
        //     callback:function(r){
        //         if(!r.exc){
        //             //refresh_field('status');
        //             console.log(r.message);
        //         }
        //     }
        //     })    
        // })
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
    const startDate = moment(frm.doc.start_date);
    if(now.isBetween(startDate,endDate)){
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
                    console.log(r.message);
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
            'fieldname':'count',
            'fieldtype':'Int',
            'label':'Number of vouchers to create',
            'reqd':1,
        }],
        primary_action:function(){
            var count = d.get_value('count');
            frappe.call({
                method:'rewards_extension.rewards_extension.doctype.voucher_campaign.voucher_campaign.create_voucher_batch',
                args:{
                    campaign:frm.doc.name,
                    count:count
                },
                callback:function(r){
                    if(!r.exc){
                        //refresh_field('status');
                        d.hide();
                    }
                }
            })
            // alert('Creating '+count+' vouchers')
        }
    })
    d.show()
}
function addHoldButton(frm){
    frm.add_custom_button(__('Disable Campaign'),function(){
        frappe.call({
            method:'rewards_extension.rewards_extension.doctype.voucher_campaign.voucher_campaign.change_campaign_status',
            args:{
                campaign:frm.doc.name,
                status:'Held'
            },
            callback:function(r){
                if(!r.exc){
                    //refresh_field('status');
                    d.hide();
                }
            }
        })
        // frm.set_value('campaign_status','Held')
        // frm.save()
    },__('Campaign Status'))
}
function addActivateButton(frm){
    frm.add_custom_button(__('Activate Campaign'),function(){
        frappe.call({
            method:'rewards_extension.rewards_extension.doctype.voucher_campaign.voucher_campaign.change_campaign_status',
            args:{
                campaign:frm.doc.name,
                status:'Active'
            },
            callback:function(r){
                if(!r.exc){
                    //refresh_field('status');
                    d.hide();
                }
            }
        })
        // frm.set_value('campaign_status','Active')
        // frm.save()
    },__('Campaign Status'))
}