<template>
    <!-- <div class="login flex justify-center items-center py-4">
        <h1>Login Page</h1>
    </div> -->
    <div class="m-3 flex flex-row items-center justify-center py-4 vertical_flexbox ">
        <Card title="Get Started" class="w-full login max-w-md max-vertical_flexbox ">
            <form class="flex flex-col space-y-2 w-full" @submit.prevent="submit">
            <div>
                <TextInput
                    :type="'tel'"
                    :ref_for="true"
                    size="sm"
                    variant="subtle"
                    placeholder="+91-xxxxxxxxx"
                    :disabled="false"
                    v-model="mobile"
                />
            </div>
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
                @click="loginUser"
            >
                Login
            </Button>
            <!-- <Button :loading="session.login.loading" variant="solid"
            >Login</Button
            > -->
        </form>
        </Card>
    </div>
</template>
<script>
import { ref } from "vue";
import { createResource } from 'frappe-ui';
// const bgColor=ref("red")
export default {
   name: 'Login',
   props: {bgColor:{type:String,required:true}},
   data(){
    return {
        mobile:ref(''),
        user: ref({})
    }
},
   methods:{
      loginUser(){
        //   this.checkIfUserExists(this.mobile)
        this.user = createResource({
            url:'rewards_extension.auth.check_existing_username',
            method:"GET",
            params:{
                mobile:this.mobile
            }
        })
        this.user.fetch().then((res)=>{
            console.log(res)
        })
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