<template>
  <!-- Rewards Animation Background -->
  <div class="fixed inset-0 overflow-hidden z-0 bg-[#FFF8E1]">
    <div v-for="i in 20" :key="i" class="absolute reward-item" :style="rewardStyle(i)">
      <span v-if="Math.random() > 0.7" class="rupee-symbol">₹</span>
    </div>
  </div>

  <!-- Top Navigation Bar -->
  <nav class="fixed top-0 left-0 w-full bg-[#FFF8E1] shadow-md p-4 z-10">
    <div class="max-w-3xl mx-auto flex justify-between items-center">
      <div class="flex items-center bg-gradient-to-r from-blue-500 to-purple-500 text-white px-4 py-2 rounded-lg shadow-md">
        <span class="text-2xl mr-2">🎟️</span>
        <div class="font-bold text-lg">Coupon Rewards</div>
      </div>
      <div class="flex items-center">
        <div class="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center mr-3 text-blue-600">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-6-3a2 2 0 11-4 0 2 2 0 014 0zm-2 4a5 5 0 00-4.546 2.916A5.986 5.986 0 005 10a6 6 0 0012 0c0-.35-.03-.693-.088-1.027A5 5 0 0010 11z" clip-rule="evenodd" />
          </svg>
        </div>
        <div class="text-right">
          <div class="font-bold text-sm">{{ userResource.doc?.full_name }}</div>
          <div class="text-gray-500 text-xs">{{ userResource.doc?.mobile_no }}</div>
        </div>
      </div>
    </div>
  </nav>

  <!-- Floating Logout Ribbon -->
  <div class="fixed bottom-0 left-0 w-full bg-gray-900 p-3 z-20 border-t border-gray-700">
    <div class="max-w-3xl mx-auto flex justify-center">
      <button
        @click="session.logout.submit()"
        class="flex items-center text-gray-300 hover:text-white transition-colors px-4 py-2 rounded-md hover:bg-gray-800"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M3 3a1 1 0 00-1 1v12a1 1 0 102 0V4a1 1 0 00-1-1zm10.293 9.293a1 1 0 001.414 1.414l3-3a1 1 0 000-1.414l-3-3a1 1 0 10-1.414 1.414L14.586 9H7a1 1 0 100 2h7.586l-1.293 1.293z" clip-rule="evenodd" />
        </svg>
        Logout
      </button>
    </div>
  </div>

  <div class="max-w-3xl py-12 mx-auto h-screen flex flex-col items-center justify-center relative z-10" v-if="!id">
    <Alert>
        You need to navigate here with a valid url by scanning from QR or from a link shared by your sales person
    </Alert>
  </div>
  <div class="max-w-3xl py-12 mx-auto h-screen flex flex-col items-center justify-center relative z-10" v-if="id">
    <!-- Show coupon input after tour completion -->
    <div v-if="voucherCampaign && tourCompleted && profileData && currentStep === 'coupon'" class="bg-white rounded-lg shadow-lg flex flex-col items-center justify-center p-6 w-full max-w-md mx-auto space-y-2">
          <div class="text-center mb-4">
            <h3 class="text-xl font-bold mb-2 text-gray-700">
              Welcome {{ profileData.customer_name }}
            </h3>
            <p class="text-sm text-gray-500">We are happy to see you here. There are exciting rewards waiting for you.</p>
          </div>
          
          <div class="w-full max-w-md">
            <Input
              type="text"
              maxlength="6"
              label="Coupon Code"
              variant="outline"
              v-model="couponCode"
              placeholder="6 Character Code"
              class="w-full"
              :class="{'border-red-500': validationMessage && !validationSuccess}"
            />
            <div v-if="validationMessage && !validationSuccess" class="text-red-500 text-sm mt-1 w-full text-left">
              {{ validationMessage }}
            </div>
          </div>
          
          <Button
            label="Submit"
            @click="validateCoupon"
            :loading="validating"
            variant="solid"
            class="w-full"
          />
          
          <!-- <Alert
            v-if="validationMessage"
            :type="validationSuccess ? 'success' : 'danger'"
            class="w-full"
          >
            {{ validationMessage }}
          </Alert> -->
        </div>
    
    <!-- Quiz Component -->
    <Quiz
      v-if="currentStep === 'quiz' && showQuiz && profileData && quizData.length > 0"
      :quizData="quizData"
      :profileData="profileData"
      :source="currentVoucher"
      @complete="completeQuiz"
    />
    
    <!-- Redemption Component -->
    <Redemption
      v-if="currentStep === 'redemption' && showRedemption" :voucher="currentVoucher"
      @complete="completeRedemption"
    />
    
    <!-- Success Message -->
    <div v-if="currentStep === 'success'" class="bg-white rounded-lg p-8 shadow-lg max-w-md text-center">
      <div class="text-green-500 text-5xl mb-4">✓</div>
      <h3 class="text-2xl font-bold mb-2 text-gray-800">Redemption Successful!</h3>
      <p class="text-gray-600 mb-6">Your reward will be processed shortly. Thank you for participating!</p>
      <Button
        label="Logout"
        @click="session.logout.submit()"
        variant="solid"
        class="w-full"
      />
    </div>
    
    <!-- Customer Profile Form -->
    <div v-if="tourCompleted && !profileData" class="bg-white rounded-lg shadow-lg p-6 w-full max-w-md mx-auto flex flex-col items-center justify-center relative z-10">
      <h3 class="text-xl font-bold mb-4 text-gray-700">Create Your Profile</h3>
      <p class="text-sm text-gray-500 mb-6">We couldn't find an existing profile. Please provide your details to continue.</p>
      <ProfileOnboarding
        :customer-profile-data="customerProfileData"
        :voucher-campaign="voucherCampaign"
        :customer-types="customerTypes"
        :creating-profile="creatingProfile"
        @submit="createProfile"
      />
    </div>
  </div>
  
  <!-- Guided Tour -->
  <GuidedTour 
    v-if="showTour && voucherCampaign"
    :campaign="voucherCampaign"
    @complete="completeTour"
  />
</template>

<script setup>
import { Dialog, Alert, Button, Input, Select, call, createDocumentResource } from "frappe-ui"
import { ref, watch, onMounted } from "vue"
import { session } from "../data/session"
import GuidedTour from '@/components/GuidedTour.vue'
import ProfileOnboarding from '@/components/ProfileOnboarding.vue';
import Quiz from '@/components/Quiz.vue';
import Redemption from '@/components/Redemption.vue';

const props = defineProps({
  id: { type: String, default: null }
})

const showDialog = ref(false)
// State management
const showTour = ref(false)
const voucherCampaign = ref(null)
const currentStep = ref('tour') // 'tour', 'profile','coupon', 'quiz', 'redemption', 'success'
const tourCompleted = ref(false) // Simple reactive tour completion state
const couponCode = ref('')
const validating = ref(false)
const validationMessage = ref('')
const validationSuccess = ref(false)
const creatingProfile = ref(false)
const currentVoucher = ref({name:'',doctype:'',amount:0.00})
const customerTypes = ['Consumer', 'Retailer', 'Wholesaler', 'Distributor']
const customerProfileData = ref({
  customer_name: '',
  customer_type: '',
  address: {
    address_line1: '',
    locality: '',
    city: '',
    pincode: ''
  }
})
// Reactive variable to store profile data (single declaration)
const profileData = ref(null)
const quizData = ref([]) // Stores quiz questions
const showQuiz = ref(false) // Controls Quiz visibility
const showRedemption = ref(false) // Controls Redemption visibility
const redemptionComplete = ref(false) // Tracks redemption completion

// Create document resource for current user
const userResource = createDocumentResource({
  doctype: "User",
  name: session.user,
  fields: ["full_name", "mobile_no"],
  auto: true,
  onSuccess(data) {
    // console.log("User details fetched:", data)
  }
})

// Create document resource for voucher campaign
const voucherResource = createDocumentResource({
  doctype: "Voucher Campaign",
  name: props.id,
  fields: ["name", "campaign_name", "campaign_target","instructions.*", "quiz.*"],
  auto: true,
  onSuccess(data) {
    if (data) {
      // console.log("Campaign data:", data)
      voucherCampaign.value = data
      showTour.value = true
      // Store quiz data if available
      if (data.quiz) {
        quizData.value = data.quiz
      }
    }
  }
})

async function completeTour() {
  tourCompleted.value = true
  showTour.value = false
  
  // Show spinner during transition
  const spinner = showSpinner();
  
  setTimeout(() => {
    try {
      // Properly await the API call to get the resolved profile object
      if(voucherCampaign.value.campaign_target != 'Sales Persons'){
        call('rewards_extension.rewards_extension.doctype.gift_voucher.gift_voucher.search_customer_profile_for_contact', {
          user: session.user,
        }).then(profile => {
          if (profile) {
            profileData.value = profile
            currentStep.value = 'coupon' // Show coupon form
          } else {
            currentStep.value = 'profile' // Show profile form
          }
          hideSpinner(spinner);
        }).catch(error => {
          console.error('Profile check failed:', error)
          currentStep.value = 'profile' // Default to profile form on error
          hideSpinner(spinner);
        });
      } else {
        hideSpinner(spinner);
      }
    } catch (error) {
      console.error('Error in completeTour:', error)
      hideSpinner(spinner);
    }
  }, 500);
}

async function validateCoupon() {
  validating.value = true
  validationMessage.value = ''
  
  // Client-side validation
  const couponRegex = /^[A-Z0-9]{6}$/
  if (!couponRegex.test(couponCode.value)) {
    validationSuccess.value = false
    validationMessage.value = 'Coupon code must be exactly 6 uppercase alphanumeric characters'
    validating.value = false
    return
  }
  
  try {
    // Call custom API method with system manager permissions
    const result = await call('rewards_extension.rewards_extension.doctype.gift_voucher.gift_voucher.validate_coupon_code_and_create_trail', {
      coupon_code: couponCode.value,
      user: session.user,
      campaign_id: voucherCampaign.value.name,
      profile: profileData.value
    })
    if (result.valid == true) {
      sessionStorage.setItem('voucher_trail_id', result.trail.trail_id)
      currentVoucher.value = {'name':result.coupon_details.voucher_name,'doctype':result.coupon_details.doctype,'amount': result.coupon_details.voucher_base_amount}
      
      // Check if there's quiz data
      if (quizData.value && quizData.value.length > 0) {
        currentStep.value = 'quiz'
        showQuiz.value = true
      } else {
        // If no quiz, go directly to redemption
        currentStep.value = 'redemption'
        showRedemption.value = true
      }
      
      validationSuccess.value = true
    } else {
      validationSuccess.value = false
      validationMessage.value = result.message || 'Invalid coupon code'
    }
  } catch (error) {
    validationSuccess.value = false
    validationMessage.value = 'Error validating coupon: ' + error.message
  } finally {
    validating.value = false
  }
}

async function createProfile() {
  // Basic validation
  if (!customerProfileData.value.customer_name || !customerProfileData.value.customer_type || !customerProfileData.value.address.address_line1 || !customerProfileData.value.address.locality || !customerProfileData.value.address.city || !customerProfileData.value.address.pincode) {
    validationMessage.value = 'Please fill all required fields.'
    validationSuccess.value = false
    return
  }

  creatingProfile.value = true
  validationMessage.value = ''

  try {
    const newProfile = await call('rewards_extension.rewards_extension.doctype.gift_voucher.gift_voucher.create_customer_profile', {
      customer_data: customerProfileData.value,
      user: session.user
    })
    profileData.value = newProfile // Store profile data
    // Transition to coupon input after profile creation
    currentStep.value = 'coupon'

    if (newProfile) {
      validationSuccess.value = true
      // validationMessage.value = 'Profile created successfully! You can now proceed.'
    }
  } catch (error) {
    validationSuccess.value = false
    validationMessage.value = 'Error creating profile: ' + error.message
  } finally {
    creatingProfile.value = false
  }
}

function completeQuiz() {
  showQuiz.value = false
  currentStep.value = 'redemption'
  showRedemption.value = true
}

function completeRedemption() {
  showRedemption.value = false
  redemptionComplete.value = true
  currentStep.value = 'success'
}

watch(() => props.id, (newId) => {
  if (newId) {
    console.log("Deal ID received:", newId)
    // Add deal processing logic here
  }
})

// Generate random positions and animations for reward items
const rewardStyle = (index) => {
  const left = Math.random() * 100;
  const animationDuration = 5 + Math.random() * 10;
  const animationDelay = Math.random() * 5;
  const size = 10 + Math.random() * 20;
  
  return {
    left: `${left}%`,
    animationDuration: `${animationDuration}s`,
    animationDelay: `${animationDelay}s`,
    width: `${size}px`,
    height: `${size}px`,
    background: `hsl(${Math.random() * 360}, 50%, 40%)`,
    opacity: Math.random() * 0.3 + 0.1
  };
}
// Helper functions for spinner animation
function showSpinner() {
  const spinner = document.createElement('div');
  spinner.className = 'fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50';
  spinner.innerHTML = '<div class="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-blue-500"></div>';
  document.body.appendChild(spinner);
  return spinner;
}

function hideSpinner(spinner) {
  if (spinner && spinner.parentNode) {
    document.body.removeChild(spinner);
  }
}

// Updated step transition function with spinner animation
function nextStep() {
  const spinner = showSpinner();
  
  setTimeout(() => {
    if (currentStep.value === 'onboarding') {
      currentStep.value = 'coupon';
    } else if (currentStep.value === 'coupon') {
      currentStep.value = 'quiz';
    } else if (currentStep.value === 'quiz') {
      currentStep.value = 'redemption';
    }
    
    hideSpinner(spinner);
  }, 500);
}

</script>
<style scoped>
/* Rewards raining animation */
.reward-item {
  position: absolute;
  top: -50px;
  border-radius: 50%;
  animation: fall linear infinite;
  box-shadow: 0 0 10px rgba(255, 215, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
}

.rupee-symbol {
  font-size: 1.2rem;
  font-weight: bold;
  color: #5D4037;
  text-shadow: 0 0 3px rgba(0, 0, 0, 0.5);
}

@keyframes fall {
  to {
    transform: translateY(100vh) rotate(360deg);
  }
}
</style>
