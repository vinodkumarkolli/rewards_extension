<template>
  <div>
    <router-view />
    <Spinner :loading="isLoading" />
  </div>
</template>

<script>
import { ref } from 'vue'
import Spinner from './components/Spinner.vue'

export default {
  components: {
    Spinner
  },
  setup() {
    const isLoading = ref(false)
    
    // Expose loading state to router
    return {
      isLoading
    }
  }
}
</script>
