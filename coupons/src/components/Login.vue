<template>
    <!-- <div class="login flex justify-center items-center py-4">
        <h1>Login Page</h1>
    </div> -->
    <div class="m-3 flex flex-row items-center justify-center py-4 vertical_flexbox ">
        <Card v-if="!otpGenerated" title="Get Started" subtitle="Enter your Whatsapp Number" class="w-full login max-w-md">
            <form class="flex flex-col space-y-2 w-full" @submit.prevent="submit">
            <div class="flex flex-col space-y-2">
                <div class="flex flex-row items-center justify-center space-x-2" debounce="500">
                    <Badge
                    :variant="'outline'"
                    :ref_for="true"
                    theme="gray"
                    size="lg"
                    label="Country Code"
                    >
                    +91
                    </Badge>
                    <TextInput
                        :type="'tel'"
                        :ref_for="true"
                        size="sm"
                        variant="outline"
                        placeholder="xxxxxxxxx"
                        :disabled="false"
                        v-model="mobile"
                        @input="validateMobile"
                        maxlength="10"
                    />
                </div>
                <div v-if="mobileError" class="text-red-500 text-sm text-center">
                    {{ mobileError }}
                </div>
            </div>
            <div
                class="cf-turnstile"
                data-sitekey="0x4AAAAAABmlg0DebbYFY_xI"
                data-callback="javascriptCallback"
                data-theme="light"
                ></div>
            <Button
                :variant="'solid'"
                :ref_for="true"
                theme="blue"
                size="sm"
                label="Login"
                :loading="false"
                :loadingText="null"
                :disabled="false"
                :link="null"
                v-if="!mobileError && mobile.length===10"
                @click="sendOTP"
            >
                Get OTP
            </Button>
            <!-- <Button :loading="session.login.loading" variant="solid"
            >Login</Button
            > -->
        </form>
        </Card>
        <Card v-if="otpGenerated" title="Login" subtitle="Enter OTP received on Whatsapp" class="w-full login max-w-md">
            <form class="flex flex-col space-y-2 w-full" @submit.prevent="login">
                <TextInput
                    :type="'number'"
                    :ref_for="true"
                    size="sm"
                    variant="outline"
                    placeholder="One Time Password"
                    :disabled="false"
                    v-model="otpEntered"
                    maxlength="6"
                    @input="validateOTP"
                />
                <Button
                    :variant="'solid'"
                    :ref_for="true"
                    theme="blue"
                    size="sm"
                    label="Login"
                    :loading="false"
                    :loadingText="null"
                    :disabled="otpEntered.length !== 6"
                    :link="null"
                    @click="login"
                >
                    Login
                </Button>
            </form>
        </Card>
    </div>
</template>
<script>
import { ref } from "vue";
import { createResource,debounce } from 'frappe-ui';
// const bgColor=ref("red")
export default {
   name: 'Login',
   props: {bgColor:{type:String,required:true}},
   data(){
    return {
        mobile:ref(''),
        guest: ref({}),
        otpGuest:ref({}),
        mobileError: '',
        blacklist:[],
        otpGenerated:ref(false),
        otpEntered:ref('')
        }
    },
   methods:{
    javascriptCallback(e){
        alert(e)
    },
    validateOTP() {
        const otpValue = this.otpEntered;
        // Remove any non-digit characters
        const cleanOtp = otpValue.replace(/[^0-9]/g, '');
        // Update the otp value to only contain digits
        this.otpEntered = cleanOtp;
    },
    validateMobile() {
        const mobileValue = this.mobile;
        // Clear previous error
        this.mobileError = '';
        // Check if empty
        if (!mobileValue) {
            return;
        }
        // Remove any non-digit characters
        const cleanMobile = mobileValue.replace(/[^0-9]/g, '');
        // Update the mobile value to only contain digits
        this.mobile = cleanMobile;
        // Validate length and digits only
        if (cleanMobile.length >= 0 && cleanMobile.length < 10) {
            this.mobileError = 'Mobile number must be 10 digits';
        } 
        else if (cleanMobile.length === 10) {
            // Check if it's a valid Indian mobile number (starts with 6, 7, 8, or 9)
            if (!/^[6-9]/.test(cleanMobile)) {
                this.mobileError = 'Please enter a valid Indian mobile number';
            }
            const blacklisted = this.blacklist.find(item => item.mobile === cleanMobile);
            if(blacklisted){
                this.mobileError = blacklisted.blacklistedReason;
            }
        }
    },
    sendOTP(){
        // Validate before submitting
        this.validateMobile();
        
        if (this.mobileError || !this.mobile || this.mobile.length !== 10) {
            if (!this.mobileError) {
                this.mobileError = 'Please enter a valid 10-digit mobile number';
            }
            return;
        }
        
        const fullMobile = `+91${this.mobile}`;
        this.guest = createResource({
            url:'rewards_extension.auth.check_existing_wanumber',
            method:"GET",
            params:{
                mobile: fullMobile
            }
        })
        this.guest.fetch().then((res)=>{
            if(res.status == 1){
                this.blacklist.push({mobile:this.mobile,blacklistedReason:'Whatsapp not associated with this number',blacklist:'Full'})
                this.validateMobile(this.mobile)
            }
            if(res.status == 3) {
                this.otpGenerated = true
            }
        })
    },
    login(){
        //Validating OTP before submitting
        this.validateOTP();
        const fullMobile = `+91${this.mobile}`;
        if(this.otpEntered.length == 6){
            this.otpGuest = createResource({
                    url:'rewards_extension.auth.validate_otp',
                    method:"GET",
                    params:{
                        mobile: fullMobile,
                        otp: this.otpEntered
                    }
                }
            )
            this.otpGuest.fetch().then((res)=>{
                console.log(res)
            })
        }
    }
   }
}
</script>
<script setup>
import { Card,TextInput,Button } from 'frappe-ui';
</script>
<style scoped>
.login{
    background-color: v-bind(bgColor);
}
</style>