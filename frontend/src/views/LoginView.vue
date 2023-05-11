<template>
	<div class="login">
		<div id="left">
			<div>
				<img src="@/assets/logo.svg"/>
				<h1>MyKanban</h1>
			</div>
		</div>
		<div id="right">
			<div>
				<div>
					<form id="login-form" @submit.prevent="login">
						<input type="text" v-model="email" placeholder="Enter your email">
						<input type="password" v-model="pword" placeholder="Enter your password">
						<input class="btn" type="submit" value="Login">
					</form>
					<p>
						Don't have an account?
						<button class="btn" @click="$router.push({name: 'signup'})">Sign up</button>
					</p>
				</div>
			</div>
		</div>
		<Popup @close-dialog="closeDlg" v-if="msg" :msg-body="msgBody"/>
	</div>
</template>

<script>
import Popup from '@/components/Popup.vue'
export default {
	data() {
		return {
			email: "",
			pword: "",
			remember: false,
			msg: false,
			msgBody: ''
		}
	},
	components: {
		Popup
	},
	methods: {
		login() {
			if (this.email != "" && this.pword != "") {
				fetch('http://localhost:5000/login?include_auth_token', {
					method: 'POST',
					// credentials: 'include',
					// ERROR when above line is included:
					// Access to fetch at 'http://localhost:5000/login?include_auth_token' from origin 'http://localhost:8080' has been blocked by CORS policy: Response to preflight request doesn't pass access control check: The value of the 'Access-Control-Allow-Credentials' header in the response is '' which must be 'true' when the request's credentials mode is 'include'.
					// LoginView.vue?e922:34 POST http://localhost:5000/login?include_auth_token net::ERR_FAILED
					headers: {
						'Content-Type': 'application/json'
					},
					body: JSON.stringify({
						"email": this.email,
						"password": this.pword
					})
				})
				.then(async r=>{
					if (r.ok) {
						return r.json()
					} else {
						throw await r.json();
					}
				})
				.then(d=>{
					localStorage.auth_token = d.response.user.authentication_token;
					this.$router.push({name: 'dashboard'});
					this.email = "";
					this.pword = "";
				})
				.catch(e=>{
					this.msg = true;
					let msgs = ""
					for (let error of e.response.errors) {
						msgs += error + " "
					}
					this.msgBody = msgs
				})
			}
		},
		closeDlg(type, identifier) {
            if (type === 'msg') {
                this.msg = false;
                this.msgBody = ""
            }
            if (type === 'edit-board') {
                this.editBoardName = false;
                this.editBoardNameValue = ""
            }
            if (type === 'add-entity' && identifier == 'Board') {
                this.addNewBoard = false;
            }
            if (type === 'add-entity' && identifier == 'List') {
                this.addNewList = false;
            }
        }
	}
}
</script>

<style scoped>
.login {
	display: grid;
	grid-template-columns: 1fr 1fr;
	height: 100vh;
	background: var(--offwhite)
}

#left {
	display: grid;
	place-items: center;
}

#left > div {
	display: grid;
	place-items: center;
}

#left img {
	width: 40%;
}

#right {
	display: grid;
	place-items: center;
}

#right > div {
	background: var(--bluishgrey);
	height: 300px;
	width: 360px;
	padding: 20px;
	display: grid;
	place-items: center;
	border-radius: 20px;
}

#right p {
	color: white;
}

#login-form {
	width: 300px;
	display: flex;
	flex-direction: column;
	gap: 10px;
}

#login-form input[type="text"],
#login-form input[type="password"],
#login-form input[type="submit"] {
	font-size: 1em;
	padding: 10px;
	border: none;
	border-radius: 5px;
}

@media screen and (max-width: 700px) {
	.login {
		grid-template-columns: 1fr;
		grid-template-rows: 1fr 3fr;
		background: var(--bluishgrey);
	}
	
	#left {
		padding-top: 40px;
		color: white;
		background: var(--bluishgrey);
	}
}
</style>