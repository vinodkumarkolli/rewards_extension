<template>
    <!--Tutorial https://www.youtube.com/watch?v=NilffTjcDVA-->
    <div v-show="modalActive" class="absolute w-full h-screen bg-black bg-opacity-30 top-0 left-0 flex justify-center px-8">
        <div v-if="modalActive" class="p-4 flex flex-col rounded-lg bg-white self-start mt-32 max-w-screen-md">
            <slot />
        </div>
    </div>
</template>
<script>
export default {
    props:{
        modalActive:{
            type:Boolean,
            default:false
        }
    },
    // emits:['close-base-modal']
}
</script>