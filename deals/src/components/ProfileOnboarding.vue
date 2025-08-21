<template>
  <div class="w-full max-w-md py-4 flex flex-col items-center justify-center">
    <h3 class="text-xl font-bold mb-4 text-gray-700">{{ headerText }}</h3>
    <p class="text-sm text-gray-500 mb-6">{{ subHeaderText }}</p>
    <!-- Step 0: Link or Create Profile -->
    <div v-if="currentStep === 0" class="w-full max-w-md flex flex-col items-center justify-center">
      <div class="w-full space-y-4">
        <!-- <h3 class="text-xl font-bold text-gray-800 text-center">Profile Setup</h3>
        <p class="text-gray-600 text-center">Would you like to link an existing profile or create a new one?</p>
         -->
        <div class="flex flex-col gap-3 mt-4">
          <Button
            label="Link Existing Profile"
            variant="solid"
            @click="selectLinkProfile"
            class="w-full"
          />
          <Button
            label="Create New Profile"
            variant="outline"
            @click="goToStep(1)"
            class="w-full"
          />
        </div>
      </div>
    </div>
    
    <!-- Step 0.5: Select Existing Profile -->
    <div v-if="currentStep === 0.5" class="w-full max-w-md flex flex-col items-center justify-center">
      <div class="w-full space-y-4">
        <label class="block text-sm font-medium text-gray-700">Select Customer <span class="text-red-500">*</span></label>
        <Autocomplete
          v-model="selectedProfile"
          :options="customerProfiles"
          placeholder="Search and select a profile..."
          class="w-full"
        />
        
        <!-- Navigation Controls for Step 0.5 -->
        <div class="flex justify-between mt-8 gap-4 w-full">
          <Button
            variant="outline"
            @click="goToStep(0)"
          >
            Previous
          </Button>
          <Button
            label="Link"
            variant="solid"
            @click="linkProfile"
            :loading="linkingProfile"
            :disabled="!selectedProfile"
          />
        </div>
      </div>
    </div>

    <!-- Step 1: Customer/Store Name -->
    <div v-if="currentStep === 1" class="w-full max-w-md flex flex-col items-center justify-center">
        <div id="profileQuestion1" class="w-full space-y-2">
          <label for="store_name" v-if="voucherCampaign?.campaign_target == 'Retailers'" class="block text-sm font-medium text-gray-700">Store Name <span class="text-red-500">*</span></label>
          <label for="store_name" v-if="voucherCampaign?.campaign_target == 'Consumers'" class="block text-sm font-medium text-gray-700">Name <span class="text-red-500">*</span></label>
          <Input
            id="store_name"
            v-model="customerProfileData.customer_name"
            placeholder="Enter your store or business name"
            required
            class="w-full"
          />
        </div>
        
        <!-- Navigation Controls for Step 1 -->
        <div class="flex justify-between mt-8 gap-4 w-full">
          <Button
            variant="outline"
            @click="goToStep(0)"
          >
            Previous
          </Button>
          <Button
            label="Next"
            variant="solid"
            @click="goToStep(2)"
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
      
      <!-- Navigation Controls for Step 2 -->
      <div class="flex justify-between mt-8 gap-4 w-full">
        <Button
          variant="outline"
          @click="goToStep(1)"
        >
          Previous
        </Button>
        <Button
          label="Submit"
          variant="solid"
          @click="$emit('submit')"
          :loading="creatingProfile"
          :disabled="!isFormValid"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { Autocomplete, call } from 'frappe-ui';
import { session } from '../data/session';

export default {
  components: {
    Autocomplete
  },
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
    this.fetchCustomerProfiles();
  },
  data() {
    return {
      currentStep: 0,
      customerProfiles: [],
      selectedProfile: null,
      linkingProfile: false
    };
  },
  computed: {
    headerText() {
      if (this.currentStep === 0.5) {
        return "Link Existing Profile";
      }
      return "Create Your Profile";
    },
    subHeaderText() {
      if (this.currentStep === 0.5) {
        return "Select an existing profile to link to your account";
      }
      return "We couldn't find an existing profile. Please provide your details to continue.";
    },
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
    },
    selectLinkProfile() {
      if (this.voucherCampaign?.campaign_target == 'Retailers' || this.voucherCampaign?.campaign_target == 'Consumers') {
        this.currentStep = 0.5;
      }
    },
    async fetchCustomerProfiles() {
      try {
        const profiles = await call('rewards_extension.rewards_extension.doctype.gift_voucher.gift_voucher.get_all_customer_profiles');
        this.customerProfiles = profiles.sort((a, b) => new Date(b.modified) - new Date(a.modified)).map(profile => ({
          label: profile.customer_name,
          value: profile.name
        }));
      } catch (error) {
        console.error('Error fetching customer profiles:', error);
      }
    },
    async linkProfile() {
      if (!this.selectedProfile) return;
      
      this.linkingProfile = true;
      try {
        // Call API to link the selected profile to the current user
        const result = await call('rewards_extension.rewards_extension.doctype.gift_voucher.gift_voucher.link_customer_profile_to_user', {
          profile_name: this.selectedProfile.value,
          user: session.user
        });
        
        if (result.success) {
          // Emit an event to notify the parent component that profile linking is complete
          this.$emit('profile-linked', result.profile);
        } else {
          console.error('Failed to link profile:', result.message);
        }
      } catch (error) {
        console.error('Error linking profile:', error);
      } finally {
        this.linkingProfile = false;
      }
    }
  }
};
</script>