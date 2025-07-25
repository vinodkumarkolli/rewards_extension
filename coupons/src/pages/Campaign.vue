<script>
import {sessionUser} from '@/data/session'
import BaseModal from '@/components/BaseModal.vue'
import Login from '@/components/Login.vue' 
import {ref} from 'vue'
import { createResource } from 'frappe-ui'
import Alert from 'frappe-ui/src/components/Alert/Alert.vue'
export default {
    props:{
        id:{type:String,required:true},
    },
    components:{
        BaseModal
    },
    data(){
        return{
            campaign : ref({}),
            campaignActive:ref(false),
            bgColor:"#FFD5B9",
            activeStep:ref(''),
            modalActive:ref(true),
        }
    },
    mounted(){
        if (this.id) {
            // console.log('fetching campaign',props.id)
            let resource = createResource({
                url:'frappe.client.get',
                params:{
                    doctype:"Voucher Campaign",
                    name:this.id,
                    fields:['*']
                },
                onSuccess:(res)=>{
                    this.campaign=res
                    const startDate = new Date(this.campaign.start_date);
                    const endDate = new Date(this.campaign.end_date);
                    const da = new Date();
                    if(endDate >da && startDate <= da && this.campaign.campaign_status =='Active'){
                        this.campaignActive=true;
                        this.activeStep = this.campaign.interface[0]['interface_type'];
                        // this.activeStep=this.campaign.interface[0];
                    }
                    else{
                        this.campaignActive=false;
                    }
                }
            })
            resource.fetch()
        }
    }
}
</script>
<script setup>
import { Card } from 'frappe-ui'</script>
<template>
    <div class="campaign flex justify-center items-center h-screen text-black font-bold">
        <div v-if="!campaignActive">
            <Alert type="warning" title="Campaign not Active">
                This campaign is currently inactive.
            </Alert>
        </div>
        <div v-if="campaignActive">
            <BaseModal :modalActive="modalActive" @close-base-modal="modalActive=false">
                <div>
                    <img v-if="campaign.webpage_popup_image" :src="campaign.webpage_popup_image">
                </div>
                <div class="flex justify-start w-full py-2">
                    <button class="text-white bg-red-700 hover:bg-red-800 focus:outline-none focus:ring-4 focus:ring-red-300 font-medium rounded-full text-sm p-2.5 text-center me-2 mb-2 dark:bg-red-600 dark:hover:bg-red-700 dark:focus:ring-red-800 flex items-center justify-center" @click="modalActive=false">
                        I am aware of the terms and conditions of the offer
                        <!-- <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                        </svg> -->
                    </button>
                </div>
            </BaseModal>
            <div class="campaign w-[360px] h-[480px] rounded-xl border-2 p-4">
                <img v-if="campaign.webpage_header_image" :src=campaign.webpage_header_image alt="" width="360px" height="auto">
                <Login v-if="activeStep=='Login'" :bgColor='campaign.webpage_background_color'/>
            </div>
        </div>
    </div>
</template>
<style scoped>
.campaign{
    background-color:v-bind('campaign.webpage_background_color');
}
</style>