<template>
  <div v-if="loading" class="fixed inset-0 flex items-center justify-center z-50 bg-black bg-opacity-30">
    <div class="w-16 h-16 border-t-4 border-blue-500 rounded-full animate-spin"></div>
  </div>
</template>

<script>
export default {
  props: {
    loading: Boolean
  }
}
</script>