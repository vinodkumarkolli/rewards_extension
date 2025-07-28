<template>
  <div class="m-3 flex flex-row items-center justify-center">
    <Card :title="currentStepTitle" class="w-full max-w-md mt-4">
      <!-- Mobile Input Step -->
      <div v-if="currentStep === 'mobile'">
        <form class="flex flex-col space-y-2 w-full" @submit.prevent="sendOTP">
          <Input
            required
            name="mobile"
            type="text"
            placeholder="Enter Indian mobile number"
            label="Mobile Number"
            v-model="mobile"
          />
          <Button type="submit" :loading="loading" variant="solid">Send OTP</Button>
        </form>
      </div>

      <!-- OTP Verification Step -->
      <div v-if="currentStep === 'otp'">
        <form class="flex flex-col space-y-2 w-full" @submit.prevent="verifyOTP">
          <Input
            required
            name="otp"
            type="text"
            placeholder="Enter OTP"
            label="OTP Verification"
            v-model="otp"
          />
          <Button type="submit" :loading="loading" variant="solid">Verify OTP</Button>
          <Button type="button" @click="currentStep = 'mobile'" variant="outline" class="mt-2">
            Change Number
          </Button>
        </form>
      </div>

      <!-- Signup Form Step -->
      <div v-if="currentStep === 'signup'">
        <form class="flex flex-col space-y-2 w-full" @submit.prevent="signupUser">
          <Input
            required
            name="mobile"
            type="text"
            label="Mobile Number"
            v-model="mobile"
            disabled
          />
          <Input
            required
            name="first_name"
            type="text"
            placeholder="First Name"
            label="First Name"
            v-model="signupData.first_name"
          />
          <Input
            required
            name="last_name"
            type="text"
            placeholder="Last Name"
            label="Last Name"
            v-model="signupData.last_name"
          />
          <Input
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
import { ref, computed } from 'vue'
import { call } from 'frappe-ui'
import { useRouter } from 'vue-router'
import { Card, Input, Button } from 'frappe-ui'
const router = useRouter()
const currentStep = ref('mobile')
const mobile = ref('')
const otp = ref('')
const tmpId = ref('')
const loading = ref(false)
const signupData = ref({
  first_name: '',
  last_name: '',
  company_name: ''
})

const currentStepTitle = computed(() => {
  return {
    mobile: 'Login with Mobile',
    otp: 'Verify OTP',
    signup: 'Complete Signup'
  }[currentStep.value]
})

async function sendOTP() {
  loading.value = true
  try {
    const res = await call('rewards_extension.auth.send_login_otp', {
      mobile_no: mobile.value
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

async function signupUser() {
  loading.value = true
  try {
    // Generate encrypted email using HMAC
    const email = `u_${btoa(mobile.value).replace(/=/g, '')}@sravie.in`
    
    const res = await call('rewards_extension.auth.signup', {
      first_name: signupData.value.first_name,
      last_name: signupData.value.last_name,
      company_name: signupData.value.company_name,
      mobile_no: mobile.value,
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

async function verifyOTP() {
  loading.value = true
  try {
    const res = await call('rewards_extension.auth.verify_login_otp', {
      tmp_id: tmpId.value,
      otp: otp.value
    })
    
    if (res.status === 'success') {
      console.log(res)
      window.location.href = '/'
    }
  } catch (error) {
    console.error('OTP verification error:', error)
  } finally {
    loading.value = false
  }
}
</script>
