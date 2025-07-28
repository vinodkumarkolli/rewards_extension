<template>
  <div class="flex items-center justify-center min-h-screen bg-gray-100">
    <div class="w-full max-w-md p-8 space-y-6 bg-white rounded-lg shadow-md">
      <h2 class="text-2xl font-bold text-center text-gray-700">Passwordless Login</h2>

      <!-- Mobile Number Input Form -->
      <form v-if="!otpSent" @submit.prevent="handleSendOtp">
        <div>
          <label for="mobile" class="block text-sm font-medium text-gray-700">Mobile Number</label>
          <div class="mt-1">
            <input
              id="mobile"
              v-model="mobileNo"
              name="mobile"
              type="tel"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="+911234567890"
            />
          </div>
        </div>
        <div class="mt-6">
          <Button
            type="submit"
            theme="primary"
            variant="solid"
            class="w-full"
            :loading="sendOtpResource.loading"
          >
            Send OTP
          </Button>
        </div>
      </form>

      <!-- OTP Verification Form -->
      <form v-else @submit.prevent="handleVerifyOtp">
        <div>
          <label class="block text-sm font-medium text-gray-700">Enter OTP</label>
          <p class="mt-2 text-sm text-gray-500">An OTP has been sent to {{ mobileNo }}.</p>
          
          <div class="mt-4 flex justify-center space-x-2">
            <input
              v-for="i in 6"
              :key="i"
              v-model="otpDigits[i-1]"
              type="text"
              maxlength="1"
              inputmode="numeric"
              pattern="\d"
              required
              class="w-12 h-12 text-center text-xl border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              @input="handleOtpInput(i-1, $event)"
              @keydown.delete="handleOtpDelete(i-1, $event)"
              ref="otpInputs"
            />
          </div>
        </div>
        
        <div class="mt-6">
          <Button
            type="submit"
            theme="primary"
            variant="solid"
            class="w-full"
            :loading="verifyOtpResource.loading"
          >
            Verify & Login
          </Button>
        </div>
        
        <div class="mt-4 text-center">
          <Button variant="ghost" @click="resetForm">Try another number</Button>
        </div>
        
        <div class="mt-4 text-center">
          <p class="text-sm text-gray-500">
            Didn't receive OTP?
            <Button variant="link" @click="resendOTP">Resend</Button>
          </p>
        </div>
      </form>

      <!-- Error Message -->
      <div v-if="errorMessage" class="p-3 mt-4 text-sm text-red-700 bg-red-100 rounded-md" role="alert">
        {{ errorMessage }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { createResource, Button } from 'frappe-ui';
import { session } from '../data/session';
import { useRouter } from 'vue-router';

const router = useRouter();
const mobileNo = ref('');
const otpDigits = ref(Array(6).fill(''));
const tmpId = ref('');
const otpSent = ref(false);
const errorMessage = ref('');
const otpInputs = ref([]);

const sendOtpResource = createResource({
  url: 'rewards_extension.api.send_login_otp',
  method: 'POST',
  validate(data) {
    // Handle both success and user_not_found responses
    return data.status === 'success' || data.status === 'user_not_found';
  },
  onSuccess(data) {
    console.log('API Response:', data);
    if (data.status === 'user_not_found') {
      console.log('Redirecting to Signup with mobile:', mobileNo.value);
      // Redirect to signup with mobile number
      router.push({
        name: 'Signup',
        query: { mobile: mobileNo.value }
      });
    } else {
      tmpId.value = data.tmp_id;
      otpSent.value = true;
      errorMessage.value = '';
      // Focus first OTP input
      setTimeout(() => {
        if (otpInputs.value[0]) otpInputs.value[0].focus();
      }, 100);
    }
  },
  onError: (error) => {
    console.error('API Error:', error);
    errorMessage.value = error.message || 'An error occurred.';
  },
});

const verifyOtpResource = createResource({
  url: 'rewards_extension.api.verify_login_otp',
  method: 'POST',
  onSuccess: () => window.location.reload(), // Reload to establish the new session
  onError: (error) => (errorMessage.value = error.message || 'An error occurred.'),
});

const handleSendOtp = () => sendOtpResource.submit({ mobile_no: mobileNo.value });

const handleVerifyOtp = () => {
  const otp = otpDigits.value.join('');
  verifyOtpResource.submit({ tmp_id: tmpId.value, otp: otp });
};

const resetForm = () => {
  otpSent.value = false;
  mobileNo.value = '';
  otpDigits.value = Array(6).fill('');
  tmpId.value = '';
  errorMessage.value = '';
};

const resendOTP = () => {
  sendOtpResource.submit({ mobile_no: mobileNo.value });
};

const handleOtpInput = (index, event) => {
  // Move to next input
  if (event.target.value && index < 5) {
    otpInputs.value[index+1].focus();
  }
};

const handleOtpDelete = (index, event) => {
  // Move to previous input on delete
  if (event.key === 'Backspace' && !event.target.value && index > 0) {
    otpInputs.value[index-1].focus();
  }
};
</script>