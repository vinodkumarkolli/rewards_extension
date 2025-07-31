<template>
  <div class="mt-6 p-6 bg-white rounded-lg shadow-lg w-full max-w-md">
    <h3 class="text-xl font-bold mb-4 text-gray-700">Rewards Quiz</h3>
    <p class="text-sm text-gray-500 mb-6">Answer these questions to unlock your reward</p>
    
    <div v-if="currentStep < quizData.length">
      <div class="mb-6">
        <h4 class="font-medium mb-2 text-gray-700">
          {{ quizData[currentStep].question }} (Step {{ currentStep + 1 }} of {{ quizData.length }})
        </h4>
        
        <!-- Warmup Question -->
        <div v-if="quizData[currentStep].warmup_question" class="mb-4">
          <p class="text-sm text-gray-500 mb-2">{{ quizData[currentStep].warmup_question }}</p>
          <Select
            v-if="quizData[currentStep].warmup_type === 'Select'"
            :options="quizData[currentStep].warmup_options.split(',')"
            v-model="answers[currentStep].warmup"
            placeholder="Select an option"
            class="w-full"
          />
          <Input
            v-else
            type="text"
            v-model="answers[currentStep].warmup"
            :placeholder="quizData[currentStep].warmup_placeholder || 'Enter your answer'"
            class="w-full"
          />
        </div>
        
        <!-- Main Question -->
        <div class="mb-4">
          <p class="text-sm text-gray-500 mb-2">{{ quizData[currentStep].main_question }}</p>
          <Input
            type="text"
            v-model="answers[currentStep].main"
            :placeholder="quizData[currentStep].main_placeholder || 'Enter your answer'"
            class="w-full"
          />
        </div>
        
        <!-- Followup Question -->
        <div v-if="quizData[currentStep].followup_question">
          <p class="text-sm text-gray-500 mb-2">{{ quizData[currentStep].followup_question }}</p>
          <Input
            type="text"
            v-model="answers[currentStep].followup"
            :placeholder="quizData[currentStep].followup_placeholder || 'Enter your answer'"
            class="w-full"
          />
        </div>
      </div>
      
      <!-- Navigation Controls -->
      <div class="flex justify-between mt-8">
        <button
          v-if="currentStep > 0"
          @click="currentStep--"
          class="px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300"
        >
          Previous
        </button>
        <button
          v-else
          disabled
          class="px-4 py-2 bg-gray-100 text-gray-400 rounded cursor-not-allowed"
        >
          Previous
        </button>
        
        <button
          v-if="currentStep < quizData.length - 1"
          @click="currentStep++"
          class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Next
        </button>
        <button
          v-else
          @click="submitQuiz"
          class="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
        >
          Submit
        </button>
      </div>
    </div>
    <div v-else>
      <p class="text-center text-lg font-semibold text-green-600">Quiz completed successfully!</p>
    </div>
    
    
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
import { Input, Select, Button, Alert, call } from "frappe-ui"

const props = defineProps({
  quizData: Array
})

const emit = defineEmits(['complete'])

const currentStep = ref(0)
const answers = ref(props.quizData.map(() => ({
  warmup: '',
  main: '',
  followup: ''
})))
const submitting = ref(false)
const submissionMessage = ref('')
const submissionSuccess = ref(false)


async function submitQuiz() {
  submitting.value = true
  submissionMessage.value = ''
  
  try {
    // Call API to submit quiz answers
    const result = await call('rewards_extension.rewards_extension.doctype.gift_voucher.gift_voucher.submit_quiz_answers', {
      answers: answers.value,
      voucher_trail_id: sessionStorage.getItem('voucher_trail_id')
    })
    
    if (result.success) {
      submissionSuccess.value = true
      submissionMessage.value = 'Answers submitted successfully!'
      // Emit completion event after short delay
      setTimeout(() => emit('complete'), 1500)
    } else {
      submissionMessage.value = result.message || 'Error submitting answers'
    }
  } catch (error) {
    submissionMessage.value = 'Error: ' + error.message
  } finally {
    submitting.value = false
  }
}
</script>