import { userResource } from "@/data/user"
import { createRouter, createWebHistory } from "vue-router"
import { session } from "./data/session"

const routes = [
	{
		path: "/",
		name: "Home",
		component: () => import("@/pages/Home.vue"),
	},
	{
		name: "Login",
		path: "/account/login",
		component: () => import("@/pages/Login.vue"),
	},
]

const router = createRouter({
	history: createWebHistory("/deals"),
	routes,
})

// Global loading state management
let appInstance = null

export const setAppInstance = (app) => {
  appInstance = app
}

router.beforeEach(async (to, from, next) => {
  // Set global loading state
  if (appInstance && appInstance.isLoading !== undefined) {
    appInstance.isLoading = true
  }
  
  // Existing authentication logic
  let isLoggedIn = session.isLoggedIn
  try {
    await userResource.promise
  } catch (error) {
    isLoggedIn = false
  }

  if (to.name === "Login" && isLoggedIn) {
    next({ name: "Home" })
  } else if (to.name !== "Login" && !isLoggedIn) {
    next({ name: "Login" })
  } else {
    next()
  }
})

router.afterEach(() => {
  if (appInstance && appInstance.isLoading !== undefined) {
    // Add slight delay so spinner is visible
    setTimeout(() => {
      appInstance.isLoading = false
    }, 300)
  }
})

export default router
