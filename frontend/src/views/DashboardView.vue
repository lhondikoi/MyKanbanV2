<template>
	<div v-if="user.id != null" id="dashboard">
		<div id="title-bar">
			<h3>MyKanban</h3>
		</div>
		<div id="nav-bar">
			<div id="nav">
				<router-link class="nav-elem" :to="{ name: 'home', params: { userId: user.id } }">
					<i class="bi bi-house-door-fill"></i>
				</router-link>
				<router-link class="nav-elem" :to="{ name: 'boards', params: { userId: user.id } }">
					<i class="bi bi-grid-1x2-fill"></i>
				</router-link>
				<router-link class="nav-elem" :to="{ name: 'lists', params: { userId: user.id, boardId: -1 } }">
					<i class="bi bi-kanban"></i>
				</router-link>
				<router-link class="nav-elem" :to="{ name: 'stats', params: { userId: user.id } }">
					<i class="bi bi-bar-chart-line"></i>
				</router-link>
			</div>
			<div id="usr">
				<router-link class="nav-elem" :to="{ name: 'settings', params: { userId: user.id } }"><i class="bi bi-gear"></i></router-link>
				<span @click="logout" class="nav-elem" id="logout-btn"><i class="bi bi-box-arrow-right"></i></span>
			</div>
		</div>
		<router-view :key="$route.fullPath" />
	</div>
</template>

<script>
export default {
	name: 'Dashboard',
	data() {
		return {
			user: {
				id: null,
				username: null,
				email: null,
				created: null,
			},
		}
	},
	created() {
		fetch('http://localhost:5000/api/user', {
			headers: {
				'Content-Type': 'application/json',
				'Authentication-Token': localStorage.auth_token
			}
		})
			.then(r => {
				if (r.ok) {
					return r.json();
				} else {
					return Promise.reject(r);
				}
			})
			.then(r => {
				this.user = r;
			})
			.catch(e => console.log(e))
	},
	methods: {
		logout() {
			fetch('http://localhost:5000/logout', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				// flask security somehow requires an empty body to be sent to return a json response on a POST request
				body: JSON.stringify({})
			})
				.then(r => { if (r.ok) { return r.json() } })
				.then(d => {
					localStorage.removeItem('auth_token')
					this.$router.push({ name: 'login' })
				})
		}
	}
}
</script>

<style>
:root {
	--offwhite: #F1F1F1;
	--darkgrey: #202020;
	--bluishgrey: #7E909A;
	--slightlydarkbluishgrey: #5D6E79;
	--darkblue: #1C4E80;
	--lightblue: #A5D8DD;
	--orange: #EA6A47;
	--mediumblue: #0091D5;
}

#dashboard {
	display: grid;
	grid-template-columns: 60px 1fr;
	grid-template-rows: 40px 1fr;
	height: 100vh;
}

#title-bar {
	grid-row: 1 / 2;
	grid-column: 1 / 3;
	background: var(--darkblue);
	color: white;
	display: flex;
	align-items: center;
	justify-content: center;
}

#nav-bar {
	grid-row: 2 / 3;
	grid-column: 1 / 2;
	background: var(--darkgrey);

	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: space-between;
	gap: 10px;
	padding: 20px 0;
}

#nav, #usr {
	display: flex;
	flex-direction: column;
	gap: 20px;
}

.nav-elem {
	background: #333;
	color: var(--offwhite);
	height: 40px;
	width: 40px;
	display: block;
	border-radius: 10px;
	display: grid;
	place-items: center;
}

#logout-btn {
	transition: 250ms ease-in;
	background: red;
}

#logout-btn:hover {
	background: rgb(255, 37, 37);
	cursor: pointer;
}

.nav-elem:hover {
	background: #444;
}

.main {
	background: var(--offwhite);
}

.btn {
	color: #fff;
	border: none;
	min-width: max-content;
	padding: 5px;
	background: var(--slightlydarkbluishgrey);
	border-radius: 5px;
}

.btn:hover {
	cursor: pointer;
}

.btn:focus,
.btn:active {
	/* outline: 1px dashed grey; */
	outline: none;
}

.btn-transparent {
	/* This class must be below .btn class as it is
    over-riding the color and background properties */
	color: #000;
	background: none;
}


[v-cloak] {
	display: none;
}
</style>
