<template>
  <div class="m-3 flex flex-row items-center justify-center h-screen">
    <Card :title="currentStepTitle" class="w-full max-w-md mt-4">
      <!-- Mobile Input Step -->
      <div v-if="currentStep === 'mobile'">
        <form class="flex flex-col space-y-2 w-full" @submit.prevent="sendOTP">
          <div class="relative">
            <div class="flex flex-row items-center justify-center space-x-2">
            <div class="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none text-gray-500">
              +91
            </div>
            <TextInput
                required
                name="mobile"
                type="text"
                maxlength="10"
                placeholder="Mobile number"
                label="Mobile Number"
                v-model="mobile"
                class="pl-10 w-full"
                @input="validateMobileNumber"
              />
            </div>
            <div v-if="mobileError" class="text-red-500 text-sm mt-1">{{ mobileError }}</div>
          </div>
          <Button type="submit" :loading="loading" variant="solid" :disabled="!!mobileError">Send OTP</Button>
        </form>
      </div>
      <!-- OTP Verification Step -->
      <div v-if="currentStep === 'otp'">
        <form class="flex flex-col space-y-2 w-full" @submit.prevent="verifyOTP">
          <div class="flex flex-col items-center justify-center">
            <div class="flex flex-row items-center justify-center space-x-2 py-2 relative">
              <input
                v-for="(digit, index) in otpDigits"
                :key="index"
                v-model="otpDigits[index]"
                type="text"
                inputmode="numeric"
                pattern="[0-9]*"
                maxlength="1"
                :class="[
                  'w-12 h-12 text-center border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                  verifying ? 'opacity-50 cursor-not-allowed' : ''
                ]"
                :disabled="verifying"
                @input="handleOtpInput(index, $event)"
                @keydown.delete="handleOtpDelete(index, $event)"
                ref="otpInputs"
              />
              <div v-if="verifying" class="absolute inset-0 flex items-center justify-center">
                <div class="w-8 h-8 border-t-2 border-blue-500 rounded-full animate-spin"></div>
              </div>
            </div>
            <div v-if="otpError" class="text-red-500 text-sm mt-1">{{ otpError }}</div>
          </div>
          <Button
            type="button"
            @click="resendOTP"
            variant="outline"
            class="mt-2"
            :disabled="resendDisabled"
          >
            {{ resendButtonText }}
          </Button>
        </form>
      </div>

      <!-- Signup Form Step -->
      <div v-if="currentStep === 'signup'">
        <form class="flex flex-col space-y-2 w-full" @submit.prevent="signupUser">
          <div class="relative">
            <div class="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none text-gray-500">
              +91
            </div>
            <TextInput
              required
              name="mobile"
              type="text"
              label="Mobile Number <span class='text-red-500'>*</span>"
              :value="mobile"
              disabled
              class="pl-10"
            />
          </div>
          <TextInput
            required
            name="first_name"
            type="text"
            placeholder="First Name (Required)"
            label="First Name <span class='text-red-500'>*</span>"
            v-model="signupData.first_name"
          />
          <TextInput
            required
            name="last_name"
            type="text"
            placeholder="Last Name (Required)"
            label="Last Name <span class='text-red-500'>*</span>"
            v-model="signupData.last_name"
          />
          <TextInput
            name="company_name"
            type="text"
            placeholder="Company Name (Optional)"
            label="Company Name"
            v-model="signupData.company_name"
          />
          <Button type="submit" :loading="loading" variant="solid">Sign Up</Button>
          <Button type="button" @click="currentStep = 'mobile'" variant="outline" class="mt-2">
            Change Number
          </Button>
        </form>
      </div>
    </Card>
  </div>
</template>

<script lang="ts" setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { call } from 'frappe-ui'
import { Card, Button } from 'frappe-ui'
import GuidedTour from '../components/GuidedTour.vue'
import { createDocumentResource } from 'frappe-ui'

import { useRoute } from 'vue-router'

const route = useRoute()
const currentStep = ref('mobile')
const mobile = ref('')
const mobileError = ref('')
const otpError = ref('')
const resendDisabled = ref(true)
const resendCountdown = ref(30)
const resendButtonText = computed(() => 
  resendDisabled.value 
    ? `Resend OTP (${resendCountdown.value}s)` 
    : 'Resend OTP'
)
const otpDigits = ref(Array(6).fill(''))
const otpInputs = ref<HTMLInputElement[]>([])
const otp = computed(() => otpDigits.value.join(''))
const tmpId = ref('')
const loading = ref(false)
const verifying = ref(false)
const signupData = ref({
  first_name: '',
  last_name: '',
  company_name: ''
})

// Tour state
const showTour = ref(false)
const voucherCampaign = ref(null)
const tourResource = createDocumentResource({
  doctype: 'Voucher Campaign',
  fields: ['campaign_name', 'instructions.*'],
  auto: false
})

/**
 * Computed property for step title displayed in card header
 */
const currentStepTitle = computed(() => {
  return {
    mobile: 'Login with Mobile',
    otp: 'Verify OTP',
    signup: 'Complete Signup'
  }[currentStep.value]
})

/**
 * Validates mobile number format and sets error message if invalid
 * @returns {boolean} True if valid, false otherwise
 */
function validateMobileNumber() {
  mobileError.value = ''
  
  if (!mobile.value) {
    mobileError.value = 'Mobile number is required'
    return false
  }
  
  if (mobile.value.length !== 10) {
    mobileError.value = 'Mobile number must be 10 digits'
    return false
  }
  
  if (!/^\d+$/.test(mobile.value)) {
    mobileError.value = 'Mobile number must contain only digits'
    return false
  }
  
  return true
}

/**
 * Sends OTP to user's mobile number
 * Handles transition to OTP or signup steps based on API response
 */
async function sendOTP() {
  if (!validateMobileNumber()) return
  
  loading.value = true
  try {
    const res = await call('rewards_extension.auth.send_login_otp', {
      mobile_no: '+91' + mobile.value
    })
    if (res.status === 'user_not_found') {
      currentStep.value = 'signup'
    } else if (res.status === 'success') {
      tmpId.value = res.tmp_id
      currentStep.value = 'otp'
    }
  } catch (error) {
    console.error('OTP send error:', error)
  } finally {
    loading.value = false
  }
}

/**
 * Handles user signup process
 * Generates temporary email and submits signup data to API
 */
async function signupUser() {
  loading.value = true
  try {
    const email = `u_${btoa(mobile.value).replace(/=/g, '')}@sravie.in`
    
    const res = await call('rewards_extension.auth.signup', {
      first_name: signupData.value.first_name,
      last_name: signupData.value.last_name,
      company_name: signupData.value.company_name,
      mobile_no: '+91' + mobile.value,
      email: email
    })
    
    if (res.status === 'success') {
      tmpId.value = res.tmp_id
      currentStep.value = 'otp'
    }
  } catch (error) {
    console.error('Signup error:', error)
  } finally {
    loading.value = false
  }
}

/**
 * Verifies entered OTP with server
 * Redirects to home page on successful verification
 */
async function verifyOTP() {
  otpError.value = ''
  verifying.value = true
  loading.value = true
  try {
    const res = await call('rewards_extension.auth.verify_login_otp', {
      tmp_id: tmpId.value,
      otp: otp.value
    })
    
    if (res.status === 'success') {
      // Get deal ID from route parameters
      const dealId = route.params.id
      
      // Always redirect after login
      redirectToDealPage()
    } else {
      otpError.value = 'OTP verification failed. Please try again.'
      verifying.value = false
    }
  } catch (error) {
    // console.error('OTP verification error:', error)
    
    // Handle all ValidationError exceptions from backend
    if (error?.exc_type === 'ValidationError') {
      // Extract the actual error message from the exception
      // const message = error.message.split(':').pop()?.trim() || 'Invalid OTP'
      const message = 'Invalid OTP'
      otpError.value = message
    } else {
      otpError.value = 'An error occurred during verification. Please try again.'
    }
    
    verifying.value = false
    loading.value = false
    
    // Reset OTP fields but keep digits for correction
    setTimeout(() => {
      otpInputs.value[0]?.focus()
    }, 100)
  }
}

/**
 * Handles OTP digit input:
 * - Validates numeric input only
 * - Auto-advances to next field
 * - Submits form when last digit entered
 * @param {number} index - Current OTP digit index
 * @param {Event} event - Input event
 */
function handleOtpInput(index: number, event: Event) {
  const input = event.target as HTMLInputElement
  const value = input.value
  
  // Only allow digits
  if (!/^\d*$/.test(value)) {
    input.value = ''
    otpDigits.value[index] = ''
    return
  }
  
  // Move to next input if digit entered
  if (value && index < 5) {
    otpInputs.value[index + 1]?.focus()
  } else if (index === 5 && value) {
    // Auto-submit when last digit is entered
    verifyOTP()
  }
}

/**
 * Handles backspace in OTP fields
 * Moves focus to previous field when deleting empty input
 * @param {number} index - Current OTP digit index
 * @param {KeyboardEvent} event - Keyboard event
 */
function handleOtpDelete(index: number, event: KeyboardEvent) {
  if (event.key === 'Backspace' && !otpDigits.value[index] && index > 0) {
    otpInputs.value[index - 1]?.focus()
  }
}

/**
 * Starts countdown timer for OTP resend button
 */
function startResendCountdown() {
  resendCountdown.value = 30
  const timer = setInterval(() => {
    resendCountdown.value--
    if (resendCountdown.value <= 0) {
      clearInterval(timer)
      resendDisabled.value = false
    }
  }, 1000)
}

onMounted(() => {
  if (currentStep.value === 'otp') {
    startResendCountdown()
  }
})

/**
 * Resends OTP to user's mobile number
 * Resets OTP fields and restarts countdown timer
 */
async function resendOTP() {
  resendDisabled.value = true
  loading.value = true
  try {
    const res = await call('rewards_extension.auth.send_login_otp', {
      mobile_no: '+91' + mobile.value
    })
    
    if (res.status === 'success') {
      tmpId.value = res.tmp_id
      otpDigits.value = Array(6).fill('')
      startResendCountdown()
      otpError.value = ''
      await nextTick()
      if (otpInputs.value[0]) {
        otpInputs.value[0].focus()
      }
    } else {
      otpError.value = 'Failed to resend OTP. Please try again.'
    }
  } catch (error) {
    console.error('OTP resend error:', error)
    otpError.value = 'Failed to resend OTP. Please try again.'
  } finally {
    loading.value = false
  }
}

// Redirect to deal page
function redirectToDealPage() {
  const dealId = route.params.id
  const redirectPath = dealId ? `/deals/${dealId}` : '/'
  
  setTimeout(() => {
    window.location.href = redirectPath
  }, 1000)
}
</script>

<!--
Test Cases for Passwordless Login:

1. Mobile Validation:
   - Empty input shows "Mobile number is required"
   - 9-digit input shows "Mobile number must be 10 digits"
   - Non-numeric input shows "Mobile number must contain only digits"
   - Valid 10-digit input clears error

2. Send OTP Flow:
   - Valid mobile triggers API call
   - API success transitions to OTP step
   - "User not found" transitions to signup step
   - API failure shows console error

3. OTP Handling:
   - Input fields only accept digits
   - Digits auto-advance to next field
   - Last digit triggers verification
   - Backspace moves to previous field

4. OTP Verification:
   - Valid OTP redirects to home page
   - Invalid OTP shows error message
   - API failure shows error message

5. Signup Flow:
   - Form submission triggers API call
   - Success transitions to OTP step
   - Failure shows console error

6. Resend OTP:
   - Button triggers new OTP request
   - Success resets OTP fields and starts countdown
   - Failure shows error message
   - Countdown timer disables button until expiration

7. Step Transitions:
   - Mobile step shows "Login with Mobile"
   - OTP step shows "Verify OTP"
   - Signup step shows "Complete Signup"
-->
