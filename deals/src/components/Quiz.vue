<template>
  <div class="bg-white rounded-lg shadow-lg flex flex-col items-center justify-center p-6 w-full max-w-md mx-auto">
    <h3 class="text-xl font-bold mb-2 text-gray-700">Rewards Quiz</h3>
    <p class="text-sm text-gray-500">Answer these questions to unlock your reward</p>
    
    <div v-if="currentStep < quizData.length"  class="w-full max-w-md py-4">
      <div class="mb-6">
        <h4 class="font-medium mb-2 text-gray-900 flex flex-col items-center justify-center">
          Step {{ currentStep + 1 }} of {{ quizData.length }} -  ({{ quizData[currentStep].question_heading }})
        </h4>
        
        <!-- Main Question -->
        <div class="mb-4 py-2">
          <p class="text-sm text-gray-700 mb-2">
            {{ quizData[currentStep].main_question }}
            <span v-if="quizData[currentStep].mandatory_answer === 1" class="text-red-500">*</span>
          </p>
          <p class="text-sm text-gray-500 mb-2" v-if="quizData[currentStep].main_question_description">( {{ quizData[currentStep].main_question_description }} )</p>
          <component
            :is="getComponentType(quizData[currentStep].main_question_type)"
            v-model="answers[currentStep].main"
            :options="quizData[currentStep].main_question_options ? quizData[currentStep].main_question_options.split('\n') : []"
            :placeholder="quizData[currentStep].main_placeholder || (quizData[currentStep].mandatory_answer ? 'Required: ' : 'Optional: ') + getDefaultPlaceholder(quizData[currentStep].main_question_type)"
            :multiple="quizData[currentStep].main_question_type === 'Multi Select'"
            class="w-full"
          />
        </div>
      </div>
      
      <!-- Navigation Controls -->
      <div class="flex justify-between mt-8">
        <Button
          v-if="currentStep > 0"
          :variant="'outline'"
          @click="currentStep--"
          class="mr-2"
        >
          Previous
        </Button>
        <Button
          v-else
          :variant="'outline'"
          disabled
          class="mr-2"
        >
          Previous
        </Button>
        
        <Button
          v-if="currentStep < quizData.length - 1"
          :variant="'solid'"
          @click="currentStep++"
          :disabled="isCurrentStepMandatory && !isMainAnswerProvided"
        >
          Next
        </Button>
        <Button
          v-else
          :variant="'solid'"
          @click="submitQuiz"
          :loading="submitting"
          :disabled="isCurrentStepMandatory && !isMainAnswerProvided"
        >
          Submit
        </Button>
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
import { ref, computed, h } from "vue"
import { Input, Select, Button, Alert, call, Rating, Checkbox } from "frappe-ui"
import { session } from "../data/session"

const props = defineProps({
  quizData: Array,
  profileData: { type: Object, default: null },
  source: { type: Object, default: null }
})

const emit = defineEmits(['complete'])

const currentStep = ref(0)
const answers = ref(props.quizData.map(question => {
  let mainInitial = '';
  if (question.main_question_type === 'Rating') {
    mainInitial = null; // Use null for numeric Rating component
  }
  return {
    main: mainInitial
  };
}))
const submitting = ref(false)
const submissionMessage = ref('')
const submissionSuccess = ref(false)

// Computed properties for mandatory answer validation
const isCurrentStepMandatory = computed(() => {
  return props.quizData[currentStep.value]?.mandatory_answer === 1
})

const isMainAnswerProvided = computed(() => {
  const answer = answers.value[currentStep.value].main
  const questionType = props.quizData[currentStep.value]?.main_question_type
  
  if (questionType === 'Multi Select') {
    return Array.isArray(answer) && answer.length > 0
  }
  
  return answer !== null && answer !== undefined && answer !== ''
})


async function submitQuiz() {
  submitting.value = true
  submissionMessage.value = ''
  // Create array of main_question values
  const mainQuestions = props.quizData.map(q => q.main_question)
  try {
    // Call API to submit quiz answers
    const result = await call('rewards_extension.rewards_extension.doctype.quiz_transcript.quiz_transcript.submit_quiz_answers', {
      questions:mainQuestions,
      answers: answers.value,
      profile: props.profileData,
      user: session.user,
      source: props.source
    })
    if (result.status == 'success') {
      submissionSuccess.value = true
      submissionMessage.value = 'Answers submitted successfully!'
      // Emit completion event after short delay
      setTimeout(() => emit('complete'), 300)
    } else {
      submissionMessage.value = result.message || 'Error submitting answers'
    }
  } catch (error) {
    submissionMessage.value = 'Error: ' + error.message
  } finally {
    submitting.value = false
  }
}

function getComponentType(questionType) {
  switch(questionType) {
    case 'Select':
      return {
        props: ['options', 'modelValue'],
        emits: ['update:modelValue'],
        components: { Checkbox },
        render() {
          return h('div', { class: 'space-y-2' },
            this.options.map((option, index) =>
              h('div', { class: 'flex items-center', key: index }, [
                h(Checkbox, {
                  modelValue: this.modelValue === option,
                  onChange: (value) => {
                    if (value) this.$emit('update:modelValue', option)
                  },
                  class: 'mr-2 text-blue-600',
                  radio: true
                }),
                h('label', {
                  class: 'text-sm text-gray-700 cursor-pointer',
                  onClick: () => this.$emit('update:modelValue', option)
                }, option)
              ])
            )
          );
        }
      };
    case 'Multi Select':
      return {
        props: ['options', 'modelValue'],
        emits: ['update:modelValue'],
        components: { Checkbox },
        render() {
          return h('div', { class: 'space-y-2' },
            this.options.map((option, index) =>
              h('div', { class: 'flex items-center', key: index }, [
                h(Checkbox, {
                  modelValue: (this.modelValue || []).includes(option),
                  onChange: (checked) => {
                    const currentValue = [...this.modelValue || []];
                    const indexInValue = currentValue.indexOf(option);
                    
                    if (checked && indexInValue === -1) {
                      currentValue.push(option);
                    } else if (!checked && indexInValue > -1) {
                      currentValue.splice(indexInValue, 1);
                    }
                    
                    this.$emit('update:modelValue', currentValue);
                  },
                  class: 'mr-2 text-blue-600'
                }),
                h('label', {
                  class: 'text-sm text-gray-700 cursor-pointer',
                  onClick: () => {
                    const currentChecked = (this.modelValue || []).includes(option);
                    const newValue = !currentChecked;
                    
                    const currentValue = [...this.modelValue || []];
                    if (newValue && !currentValue.includes(option)) {
                      currentValue.push(option);
                    } else if (!newValue) {
                      const index = currentValue.indexOf(option);
                      if (index > -1) currentValue.splice(index, 1);
                    }
                    
                    this.$emit('update:modelValue', currentValue);
                  }
                }, option)
              ])
            )
          );
        }
      };
    case 'Rating':
      return {
        components: { Rating },
        props: ['modelValue'],
        emits: ['update:modelValue'],
        render() {
          return h(Rating, {
            modelValue: this.modelValue,
            'onUpdate:modelValue': (value) => this.$emit('update:modelValue', value),
            maxRating: 10,
            class: 'text-blue-600'
          });
        }
      };
    case 'Data':
      return Input;
    default:
      return Input;
  }
}

function getDefaultPlaceholder(questionType) {
  switch(questionType) {
    case 'Select':
    case 'Multi Select':
      return 'Select an option';
    case 'Rating':
      return 'Enter rating (1-5)';
    case 'Data':
      return 'Enter your answer';
    default:
      return 'Enter your answer';
  }
}
</script>