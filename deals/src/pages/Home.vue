<template>
  <!-- Rewards Animation Background -->
  <div class="fixed inset-0 overflow-hidden z-0">
    <div v-for="i in 20" :key="i" class="absolute reward-item" :style="rewardStyle(i)">
      <span v-if="Math.random() > 0.7" class="rupee-symbol">₹</span>
    </div>
  </div>

  <!-- Top Navigation Bar -->
  <nav class="fixed top-0 left-0 w-full bg-white shadow-md p-4 z-10">
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
    <div v-if="tourCompleted" class="bg-gray-100 rounded-lg p-4">
      <h2 class="font-bold text-lg text-gray-600 mb-4">
        Claim your Reward
      </h2>
      
      <div class="w-full max-w-xs">
        <Input
          type="text"
          label=""
          variant="outline"
          v-model="couponCode"
          placeholder="6 Character Secret Code"
          class="mb-3"
        />
        <Button
          label="Submit"
          @click="validateCoupon"
          :loading="validating"
          variant="solid"
          class="w-full"
        />
      </div>
      
      <Alert
        v-if="validationMessage"
        :type="validationSuccess ? 'success' : 'danger'"
        class="mt-4"
      >
        {{ validationMessage }}
      </Alert>
    </div>
    
    <!-- Show original content if tour not completed -->
    <div v-else>
      <h2 class="font-bold text-lg text-gray-600 mb-4">
        Welcome {{ session.user }}!
      </h2>
      <div v-if="id">
        <p>
          ID Passed: {{ id }}
        </p>
      </div>
      <div class="flex flex-row space-x-2 mt-4">
        <Button @click="showDialog = true">Open Dialog</Button>
      </div>
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
import { Dialog, Alert, Button, Input, call, createDocumentResource } from "frappe-ui"
import { ref, watch, onMounted } from "vue"
import { session } from "../data/session"
import GuidedTour from '@/components/GuidedTour.vue'

const props = defineProps({
  id: { type: String, default: null }
})

const showDialog = ref(false)
const showTour = ref(false)
const voucherCampaign = ref(null)
const couponCode = ref('')
const validating = ref(false)
const validationMessage = ref('')
const validationSuccess = ref(false)
const tourCompleted = ref(localStorage.getItem('tourCompleted') === 'true')

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
  fields: ["name", "campaign_name", "campaign_target","instructions.*"],
  auto: true,
  onSuccess(data) {
    if (data) {
      // console.log("Campaign data:", data)
      voucherCampaign.value = data
      showTour.value = true
    }
  }
})

function completeTour() {
  localStorage.setItem('tourCompleted', 'true')
  showTour.value = false
  tourCompleted.value = true
}

async function validateCoupon() {
  validating.value = true
  validationMessage.value = ''
  
  try {
    // Call custom API method with system manager permissions
    const result = await call('rewards_extension.rewards_extension.doctype.gift_voucher.gift_voucher.validate_coupon_code_and_create_trail', {
      coupon_code: couponCode.value,
      user: session.user,
      campaign_id: voucherCampaign.value.name
    })
    
    if (result.valid) {
      // Store trail ID in session
      sessionStorage.setItem('voucher_trail_id', result.trail_id)
      
      validationSuccess.value = true
      validationMessage.value = 'Coupon validated! Trail initiated successfully'
    } else {
      validationSuccess.value = false
      validationMessage.value = result.message || 'Invalid coupon code or voucher is not active'
    }
  } catch (error) {
    validationSuccess.value = false
    validationMessage.value = 'Error validating coupon: ' + error.message
  } finally {
    validating.value = false
  }
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
    background: `hsl(${Math.random() * 360}, 70%, 60%)`,
    opacity: Math.random() * 0.3 + 0.1
  };
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
  color: white;
  text-shadow: 0 0 3px rgba(0, 0, 0, 0.5);
}

@keyframes fall {
  to {
    transform: translateY(100vh) rotate(360deg);
  }
}
</style>
