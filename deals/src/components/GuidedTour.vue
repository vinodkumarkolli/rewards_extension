<template>
  <div class="fixed inset-0 bg-black bg-opacity-70 z-50 flex items-center justify-center">
    <Card :title="tourName" class="w-full max-w-2xl">
      <div class="mb-4">
        <div class="flex flex-col items-center p-4">
          <h3 class="text-xl font-semibold mb-2 text-gray-800">{{ currentInstruction.instruction_header }}</h3>
          <img
            v-if="currentInstruction.instruction_thumbnail"
            :src="currentInstruction.instruction_thumbnail"
            alt="Instruction thumbnail"
            class="w-32 h-32 object-cover rounded-lg mb-4"
          />
          <div class="prose" v-html="currentInstruction.instruction_html"></div>
        </div>
      </div>
      
      <div class="flex justify-between">
        <Button
          variant="outline"
          @click="prevStep"
          :disabled="currentStep === 0"
        >
          Previous
        </Button>
        
        <div class="text-gray-500 text-sm">
          Step {{ currentStep + 1 }} of {{ instructions.length }}
        </div>
        
        <Button
          variant="solid"
          @click="nextStep"
          v-if="currentStep < instructions.length - 1"
        >
          Next
        </Button>
        
        <Button
          variant="solid"
          @click="completeTour"
          v-else
        >
          Finish Tour
        </Button>
      </div>
    </Card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Card, Button } from 'frappe-ui'
import { createDocumentResource } from 'frappe-ui'

const props = defineProps({
  campaign: Object
})

const emit = defineEmits(['complete'])

const currentStep = ref(0)

const instructions = computed(() => props.campaign?.instructions || [])
const currentInstruction = computed(() => instructions.value[currentStep.value] || {})
const tourName = computed(() => `${props.campaign?.campaign_name || ''} - Guided Tour`)

function nextStep() {
  if (currentStep.value < instructions.value.length - 1) {
    currentStep.value++
  }
}

function prevStep() {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

function completeTour() {
  emit('complete')
}
</script>