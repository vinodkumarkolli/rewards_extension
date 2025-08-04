<template>
  <div class="w-full max-w-md py-4 flex flex-col items-center justify-center">
    <!-- Step 1: Customer/Store Name -->
    <div v-if="currentStep === 1" class="w-full max-w-md flex flex-col items-center justify-center">
        <div id="profileQuestion1" class="w-full space-y-2">
          <label for="store_name" v-if="voucherCampaign?.campaign_target != 'Consumers'" class="block text-sm font-medium text-gray-700">Store Name <span class="text-red-500">*</span></label>
          <label for="store_name" v-if="voucherCampaign?.campaign_target == 'Consumers'" class="block text-sm font-medium text-gray-700">Name <span class="text-red-500">*</span></label>
          <Input
            id="store_name"
            v-model="customerProfileData.customer_name"
            placeholder="Enter your store or business name"
            required
            class="w-full"
          />
        </div>
    </div>


    <!-- Step 2: Address -->
    <div v-if="currentStep === 2" class="w-full max-w-md flex flex-col items-center justify-center">
        <div id="profileQuestion3" class="w-full space-y-2">
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
          <label for="state" class="block text-sm font-medium text-gray-700">State <span class="text-red-500">*</span></label>
          <select
            id="state"
            v-model="customerProfileData.address.state"
            required
            class="mt-1 w-full rounded-md border border-gray-300 bg-white py-2 px-3 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-blue-500 sm:text-sm"
          >
            <option value="">Select State</option>
            <option v-for="state in indianStates" :key="state" :value="state">
              {{ state }}
            </option>
          </select>
        </div>
        
        <div>
          <label for="country" class="block text-sm font-medium text-gray-700">Country <span class="text-red-500">*</span></label>
          <Input
            id="country"
            v-model="customerProfileData.address.country"
            placeholder="Enter your country"
            required
            disabled
            class="mt-1 w-full bg-gray-100"
          />
        </div>
        
        <div>
          <label for="pincode" class="block text-sm font-medium text-gray-700">Pincode <span class="text-red-500">*</span></label>
          <Input
            id="pincode"
            v-model="customerProfileData.address.pincode"
            placeholder="Enter your 6-digit pincode"
            required
            maxlength="6"
            class="mt-1 w-full"
          />
        </div>
        
        
      </div>
    </div>

    <!-- Navigation Controls -->
    <div class="flex justify-between mt-8 gap-4 w-full">
      <Button
          v-if="currentStep > 1"
          :variant="'outline'"
          @click="currentStep--"
        >Previous
      </Button>
      <Button
        v-else
        :variant="'outline'"
        disabled
      >
        Previous
      </Button>
      
      <Button
        v-if="currentStep < 2"
        label="Next"
        @click="goToStep(currentStep + 1)"
        variant="solid"
      />
      <Button
        v-if="currentStep === 2"
        label="Submit Profile"
        @click="$emit('submit')"
        :loading="creatingProfile"
        :disabled="!isFormValid"
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
    indianStates: Array,
    creatingProfile: Boolean
  },
  created() {
    if (this.voucherCampaign?.campaign_target) {
      this.customerProfileData.customer_type =
        this.voucherCampaign.campaign_target.slice(0, -1);
    }
  },
  data() {
    return {
      currentStep: 1
    };
  },
  computed: {
    isFormValid() {
      const data = this.customerProfileData;
      if (this.currentStep === 1) {
        return data.customer_name && data.customer_type;
      } else if (this.currentStep === 2) {
        return data.customer_name &&
               data.customer_type &&
               data.address.address_line1 &&
               data.address.locality &&
               data.address.city &&
               data.address.pincode &&
               data.address.state &&
               data.address.country &&
               /^\d{6}$/.test(data.address.pincode);
      }
      return false;
    }
  },
  methods: {
    goToStep(step) {
      this.currentStep = step;
    }
  }
};
</script>