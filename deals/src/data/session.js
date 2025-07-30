import router from "@/router"
import { createResource } from "frappe-ui"
import { computed, reactive } from "vue"

import { userResource } from "./user"

export function sessionUser() {
	const cookies = new URLSearchParams(document.cookie.split("; ").join("&"))
	let _sessionUser = cookies.get("user_id")
	if (_sessionUser === "Guest") {
		_sessionUser = null
	}
	return _sessionUser
}

export const session = reactive({
	login: createResource({
		url: "login",
		makeParams({ email, password }) {
			return {
				usr: email,
				pwd: password,
			}
		},
		onSuccess(data) {
			console.log(data)
			userResource.reload()
			session.user = sessionUser()
			session.first_name = data.first_name
			session.mobile_no = data.mobile_no
			session.user_image = data.user_image // Add user image from login response
			session.login.reset()
			
			// Redirect to original URL or home with ID
			const redirectPath = router.currentRoute.value.query.redirect ||
								(router.currentRoute.value.params.id
									? `/${router.currentRoute.value.params.id}`
									: (data.default_route || "/"))
			router.replace(redirectPath)
		},
	}),
	logout: createResource({
		url: "logout",
		onSuccess() {
			userResource.reset()
			session.user = sessionUser()
			session.first_name = null
			session.mobile_no = null
			session.user_image = null // Clear user image on logout
			router.replace({ name: "Login" })
		},
	}),
	user: sessionUser(),
	first_name: null,
	mobile_no: null,
	user_image: null, // Add user_image property
	isLoggedIn: computed(() => !!session.user),
})
