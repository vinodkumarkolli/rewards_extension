<template>
  <div>
    <!-- Step 1: Customer/Store Name -->
    <div v-if="currentStep === 1">
      <div class="space-y-4">
        <div id="profileQuestion1">
          <label for="store_name" v-if="voucherCampaign?.campaign_target != 'Consumers'" class="block text-sm font-medium text-gray-700">Store Name <span class="text-red-500">*</span></label>
          <label for="store_name" v-if="voucherCampaign?.campaign_target == 'Consumers'" class="block text-sm font-medium text-gray-700">Name <span class="text-red-500">*</span></label>
          <Input
            id="store_name"
            v-model="customerProfileData.customer_name"
            placeholder="Enter your store or business name"
            required
            class="mt-1 w-full"
          />
        </div>
      </div>
    </div>

    <!-- Step 2: Customer Type -->
    <div v-if="currentStep === 2">
      <div class="space-y-4">
        <div id="profileQuestion2">
          <label class="block text-sm font-medium text-gray-700">What describes you the best? <span class="text-red-500">*</span></label>
          <div class="mt-2 flex flex-wrap gap-x-6 gap-y-2">
            <div v-for="c_type in customerTypes" :key="c_type" class="flex items-center">
              <input
                :id="`customer_type_${c_type}`"
                name="customer_type"
                type="radio"
                :value="c_type"
                v-model="customerProfileData.customer_type"
                class="focus:ring-black h-4 w-4 text-black border-gray-300"
              />
              <label :for="`customer_type_${c_type}`" class="ml-2 block text-sm text-gray-900">
                {{ c_type }}
              </label>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Step 3: Address -->
    <div v-if="currentStep === 3">
      <div class="space-y-4">
        <div id="profileQuestion3" class="space-y-4">
                  <div>
                    <label for="address_line1" class="block text-sm font-medium text-gray-700">Address Line 1 <span class="text-red-500">*</span></label>
                    <Input
                      id="address_line1"
                      v-model="customerProfileData.address.address_line1"
                      placeholder="e.g., House No, Street Name"
                      required
                      class="mt-1 w-full"
                    />
                  </div>
                  
                  <div>
                    <label for="locality" class="block text-sm font-medium text-gray-700">Locality <span class="text-red-500">*</span></label>
                    <Input
                      id="locality"
                      v-model="customerProfileData.address.locality"
                      placeholder="e.g., Area or Landmark"
                      required
                      class="mt-1 w-full"
                    />
                  </div>
                  
                  <div>
                    <label for="city" class="block text-sm font-medium text-gray-700">City <span class="text-red-500">*</span></label>
                    <Input
                      id="city"
                      v-model="customerProfileData.address.city"
                      placeholder="Enter your city"
                      required
                      class="mt-1 w-full"
                    />
                  </div>
                  
                  <div>
                    <label for="pincode" class="block text-sm font-medium text-gray-700">Pincode <span class="text-red-500">*</span></label>
                    <Input
                      id="pincode"
                      v-model="customerProfileData.address.pincode"
                      placeholder="Enter your 6-digit pincode"
                      required
                      class="mt-1 w-full"
                    />
                  </div>
                </div>
      </div>
    </div>

    <!-- Navigation Controls -->
    <div class="mt-6 flex justify-between">
      <Button
        v-if="currentStep > 1"
        label="Previous"
        @click="goToStep(currentStep - 1)"
        variant="outline"
      />
      <Button
        v-if="currentStep < 3"
        label="Next"
        @click="goToStep(currentStep + 1)"
        variant="solid"
      />
      <Button
        v-if="currentStep === 3"
        label="Submit Profile"
        @click="$emit('submit')"
        :loading="creatingProfile"
        variant="solid"
      />
    </div>
  </div>
</template>

<script>
export default {
  props: {
    customerProfileData: Object,
    voucherCampaign: Object,
    customerTypes: Array,
    creatingProfile: Boolean
  },
  data() {
    return {
      currentStep: 1
    };
  },
  methods: {
    goToStep(step) {
      this.currentStep = step;
    }
  }
};
</script>