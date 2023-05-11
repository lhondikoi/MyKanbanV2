<template>
	<div class="signup">
		<div id="left">
			<div>
				<img src="@/assets/logo.svg"/>
				<h1>MyKanban</h1>
			</div>
		</div>
		<div id="right">
			<div>
				<div>
					<form id="signup-form" @submit.prevent="signup">
						<input type="text" v-model="email" placeholder="Enter your email">
						<input type="text" v-model="uname" placeholder="Enter a username">
						<input type="password" v-model="pword" placeholder="Enter your password">
						<input class="btn" type="submit" value="Signup">
					</form>
					<p>Already have an account?
						<button class="btn" @click="$router.push({name: 'login'})">Log in</button>
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
			uname: "",
			pword: "",
			msg: false,
			msgBody: ""
		}
	},
	methods: {
		signup() {
			if (this.email != "" && this.uname != "" && this.pword != "") {
				fetch('http://localhost:5000/signup', {
					method: 'POST',
					headers: {
						'Content-Type': 'application/json'
					},
					body: JSON.stringify({
						"email": this.email,
						"username": this.uname,
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
					console.log(d);
					this.login(this.email, this.pword);
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
		login(email, password) {
			fetch('http://localhost:5000/login?include_auth_token', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					"email": email,
					"password": password
				})
			})
			.then(async r => {
				if (r.ok) {
					return r.json();
				} else {
					throw await r.json();
				}
			})
			.then(d=>{
				localStorage.auth_token = d.response.user.authentication_token;
					this.$router.push({name: 'dashboard'});
					this.email = "";
					this.uname = "";
					this.pword = "";
			})
			.catch(e=>console.log(e))
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
	},
	components: {
		Popup
	},
}
</script>

<style scoped>
.signup {
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

#signup-form {
	width: 300px;
	display: flex;
	flex-direction: column;
	gap: 10px;
}

#signup-form input[type="text"],
#signup-form input[type="password"],
#signup-form input[type="submit"] {
	font-size: 1em;
	padding: 10px;
	border: none;
	border-radius: 5px;
}

@media screen and (max-width: 700px) {
	.signup {
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