<template>
  <div class="mt-6 p-6 bg-white rounded-lg shadow-lg w-full max-w-md">
    <h3 class="text-xl font-bold mb-4 text-gray-700">Redeem Your Reward</h3>
    <p class="text-sm text-gray-500 mb-6">Provide your redemption details to receive your reward</p>
    
    <div class="space-y-4">
      <Input
        type="text"
        label="UPI ID"
        v-model="redemptionData.upiId"
        placeholder="yourname@upi"
        class="w-full"
      />
      
      <Input
        type="tel"
        label="GPay Number"
        v-model="redemptionData.gpayNumber"
        placeholder="+91 00000 00000"
        class="w-full"
      />
      
      <Input
        type="text"
        label="Bank Account Number"
        v-model="redemptionData.bankAccount"
        placeholder="Enter bank account number"
        class="w-full"
      />
      
      <Input
        type="text"
        label="IFSC Code"
        v-model="redemptionData.ifscCode"
        placeholder="Enter IFSC code"
        class="w-full"
      />
    </div>
    
    <Button
      label="Submit Redemption"
      @click="submitRedemption"
      :loading="submitting"
      variant="solid"
      class="w-full mt-6"
    />
    
    <Alert
      v-if="submissionMessage"
      :type="submissionSuccess ? 'success' : 'danger'"
      class="mt-4"
    >
      {{ submissionMessage }}
    </Alert>
  </div>
</template>

<script setup>
import { ref } from "vue"
import { Input, Button, Alert, call } from "frappe-ui"

const emit = defineEmits(['complete'])

const redemptionData = ref({
  upiId: '',
  gpayNumber: '',
  bankAccount: '',
  ifscCode: ''
})

const submitting = ref(false)
const submissionMessage = ref('')
const submissionSuccess = ref(false)

async function submitRedemption() {
  submitting.value = true
  submissionMessage.value = ''
  
  try {
    // Call API to submit redemption details
    const result = await call('rewards_extension.rewards_extension.doctype.gift_voucher.gift_voucher.submit_redemption_details', {
      redemptionData: redemptionData.value,
      voucher_trail_id: sessionStorage.getItem('voucher_trail_id')
    })
    
    if (result.success) {
      submissionSuccess.value = true
      submissionMessage.value = 'Redemption submitted successfully! Your reward will be processed shortly.'
      // Emit completion event after short delay
      setTimeout(() => emit('complete'), 1500)
    } else {
      submissionMessage.value = result.message || 'Error submitting redemption details'
    }
  } catch (error) {
    submissionMessage.value = 'Error: ' + error.message
  } finally {
    submitting.value = false
  }
}
</script>