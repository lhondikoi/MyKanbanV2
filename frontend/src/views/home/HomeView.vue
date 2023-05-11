<template>
    <div class="main" id="home-main">
        <h3>Hi, {{ username }}!</h3>
    </div>
</template>

<script>
export default {
    name: 'HomeView',
    data() {
        return {
            username: "",
        }
    },
    props: {
        userId: Number
    },
    created() {
        fetch('http://localhost:5000/api/user', {
            headers: {
                'Authentication-Token': localStorage.auth_token
            }
        })
        .then(async r => {
            if (r.ok) {
                return r.json();
            } else {
                throw await r.json();
            }
        })
        .then(d => {
            this.username = d.username;
        })
    }
}
</script>

<style>
#home-main {
    display: flex;
    flex-direction: column;
    padding: 50px;
}
</style>