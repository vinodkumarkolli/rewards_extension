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
      <div class="flex items-center space-x-3">
        <div v-if="userResource && userResource.loading" class="text-sm text-gray-500">Loading...</div>
        <div v-else-if="userResource && userResource.doc" class="flex items-center">
          <div class="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center mr-2">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-500" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="text-sm">
            <span class="font-bold">{{ userResource.doc.first_name }}</span>
            <span class="text-gray-500"> • {{ userResource.doc.mobile_no }}</span>
          </div>
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
</template>

<script setup>
import { Dialog, Alert, Button,createDocumentResource } from "frappe-ui"
import { ref, watch } from "vue"
import { session } from "../data/session"

const props = defineProps({
  id: { type: String, default: null }
})

const showDialog = ref(false)
const userResource = createDocumentResource({
  doctype: "User",
  name: session.user,
  auto: true,
  onSuccess(data) {
    console.log("User details fetched:", data)
  }
})

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
