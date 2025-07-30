import { userResource } from "@/data/user"
import { createRouter, createWebHistory } from "vue-router"
import { session } from "./data/session"

const routes = [
	{
		path: "/:id?",
		name: "Home",
		component: () => import("@/pages/Home.vue"),
		props: true,
	},
	{
		name: "Login",
		path: "/account/login/:id?",
		props: true,
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
  	// Preserve deal ID when redirecting to Home
  	const dealId = to.params.id
  	next({ name: "Home", params: { id: dealId } })
  } else if (to.name !== "Login" && !isLoggedIn) {
  	// Pass current deal ID to login page
  	const dealId = to.params.id
  	next({ name: "Login", params: { id: dealId } })
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
