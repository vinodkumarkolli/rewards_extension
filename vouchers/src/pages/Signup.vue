<template>
  <div class="signup-container">
    <h1>Create Account</h1>
    <form @submit.prevent="handleSignup">
      <div class="form-group">
        <label for="firstName">First Name</label>
        <input
          type="text"
          id="firstName"
          v-model="signupData.first_name"
          required
        />
      </div>
      
      <div class="form-group">
        <label for="lastName">Last Name</label>
        <input
          type="text"
          id="lastName"
          v-model="signupData.last_name"
          required
        />
      </div>
      
      <div class="form-group">
        <label for="company">Company Name</label>
        <input
          type="text"
          id="company"
          v-model="signupData.company_name"
          required
        />
      </div>
      
      <div class="form-group">
        <label for="mobile">Mobile Number</label>
        <input
          type="tel"
          id="mobile"
          v-model="signupData.mobile_no"
          :readonly="isMobilePrepopulated"
          :class="{ 'bg-gray-100': isMobilePrepopulated }"
          required
        />
      </div>
      
      <div class="form-group">
        <label for="email">Email</label>
        <input
          type="email"
          id="email"
          v-model="signupData.email"
          required
        />
      </div>
      
      <button type="submit" class="btn-submit">Sign Up</button>
    </form>
    
    <p class="login-link">
      Already have an account? <router-link to="/login">Login</router-link>
    </p>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import apiService from '@/data/apiService';

export default {
  setup() {
    const router = useRouter();
    const route = useRoute();
    const signupData = ref({
      first_name: '',
      last_name: '',
      company_name: '',
      mobile_no: route.query.mobile || '',
      email: ''
    });
    
    const isMobilePrepopulated = ref(!!route.query.mobile);

    const showOTPField = ref(false);
    const isVerifyingOTP = ref(false);
    const otp = ref("");
    const tmpId = ref("");

    const handleSignup = async () => {
      try {
        const response = await apiService.post('/api/method/rewards_extension.api.signup', signupData.value);
        
        if (response.data.status === 'success') {
          tmpId.value = response.data.tmp_id;
          showOTPField.value = true;
        } else {
          console.error('Signup failed:', response.data.message);
          alert("Signup failed: " + response.data.message);
        }
      } catch (error) {
        console.error('Signup error:', error);
        alert("Signup failed: " + error.message);
      }
    };

    const verifyOTP = async () => {
      if (!otp.value || !tmpId.value) return;
      
      isVerifyingOTP.value = true;
      try {
        await apiService.post('/api/method/rewards_extension.api.verify_login_otp', {
          tmp_id: tmpId.value,
          otp: otp.value
        });
        // Redirect to home after successful verification
        router.push({ name: "Home" });
      } catch (error) {
        console.error('OTP verification failed:', error);
        alert("Invalid OTP. Please try again.");
      } finally {
        isVerifyingOTP.value = false;
      }
    };

    return {
      signupData,
      handleSignup,
      verifyOTP,
      showOTPField,
      otp,
      isVerifyingOTP
    };
  }
};
</script>

<style scoped>
.signup-container {
  max-width: 400px;
  margin: 0 auto;
  padding: 2rem;
}

.form-group {
  margin-bottom: 1rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
}

input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.btn-submit {
  width: 100%;
  padding: 0.75rem;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.login-link {
  margin-top: 1rem;
  text-align: center;
}
</style>