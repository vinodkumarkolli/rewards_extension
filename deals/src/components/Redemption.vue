<template>
  <div class="bg-white rounded-lg shadow-lg flex flex-col items-center justify-center p-6 w-full max-w-md mx-auto">
    <h3 class="text-xl font-bold mb-2 text-gray-700">Redeem Your Reward</h3>
    <p class="text-sm text-gray-500 mb-4">Provide your Redeem details to receive your reward</p>
    
    <div class="w-full mb-4">
      <div class="flex mb-4 text-sm">
        <Checkbox
          label="UPI ID"
          v-model="selectedOptions.upi"
          class="mr-4"
          @change="handleCheckboxChange('upi')"
        />
        <Checkbox
          label="GPAY"
          v-model="selectedOptions.gpay"
          @change="handleCheckboxChange('gpay')"
        />
      </div>

      <Input
        v-if="payoutMode === 'upi'"
        type="text"
        label="UPI ID"
        v-model="redemptionData.upiId"
        placeholder="yourname@upi"
        class="w-full"
        :validation="validateUPI"
      />

      <Input
        v-if="payoutMode === 'gpay'"
        type="text"
        label="GPay Number"
        v-model="redemptionData.gpayNumber"
        placeholder="10-digit mobile number"
        class="w-full"
        :validation="validateMobile"
      />
    </div>
    
    <Button
      label="Submit"
      @click="submitRedemption"
      :loading="submitting"
      :disabled="!isFormValid"
      variant="solid"
      class="w-full"
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
import { ref,computed } from "vue"
import { Input, Button, Alert, Checkbox, call } from "frappe-ui"
import { session } from "../data/session"

const props = defineProps({
  voucher: { type: Object, default: null }
})

const emit = defineEmits(['complete'])

const redemptionData = ref({
  upiId: '',
  gpayNumber: ''
})
const selectedOptions = ref({
  upi: false,
  gpay: false
})
const payoutMode = ref('')
const submitting = ref(false)
const submissionMessage = ref('')
const submissionSuccess = ref(false)

async function submitRedemption() {
  submitting.value = true
  submissionMessage.value = ''
  const payoutModeMapping = {
    upi: 'UPI ID',
    gpay: 'GPAY'
  };
  
  const redeem = {
    payout_mode: payoutModeMapping[payoutMode.value] || '',
    upi_id: redemptionData.value.upiId,
    gpay_number: redemptionData.value.gpayNumber,
    settlement_amount: props.voucher.amount
  }
  try {
    // Call API to submit redemption details
    const result = await call('rewards_extension.rewards_extension.doctype.gift_voucher.gift_voucher.update_redemption_details', {
      voucher_name: props.voucher.name,
      redeem_details: redeem,
      user: session.user
    })
    
    if (result.success) {
      submissionSuccess.value = true
      submissionMessage.value = 'Redemption submitted successfully! Your reward will be processed within 24 hrs. Please contact +91-6399962999 for any concerns'
      // Emit completion event after short delay
      setTimeout(() => emit('complete'), 300)
    } else {
      submissionMessage.value = result.message || 'Error submitting redemption details'
    }
  } catch (error) {
    submissionMessage.value = 'Error: ' + error.message
  } finally {
    submitting.value = false
  }
}

function validateUPI(value) {
  const upiRegex = /^[\w.-]+@[\w.-]+$/
  if (!value) return 'UPI ID is required'
  if (!upiRegex.test(value)) return 'Invalid UPI ID format'
  return true
}

function validateMobile(value) {
  const mobileRegex = /^\d{10}$/
  if (!value) return 'Mobile number is required'
  if (!mobileRegex.test(value)) return 'Mobile number must be 10 digits'
  return true
}

const isFormValid = computed(() => {
  if (payoutMode.value === 'upi') {
    return validateUPI(redemptionData.value.upiId) === true
  } else if (payoutMode.value === 'gpay') {
    return validateMobile(redemptionData.value.gpayNumber) === true
  }
  return false
})

function handleCheckboxChange(option) {
  // Reset other options when one is selected
  if (selectedOptions.value[option]) {
    payoutMode.value = option
    for (const key in selectedOptions.value) {
      if (key !== option) {
        selectedOptions.value[key] = false
      }
    }
  } else {
    payoutMode.value = ''
  }
}
</script>