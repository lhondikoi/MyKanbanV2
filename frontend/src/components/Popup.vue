<template>
    <div class="popup" :class="{'fade-away': hide}">
        <p>{{msgBody}}</p>
        <button class="close-btn" @click="$emit('close-dialog', 'msg')"><i class="bi bi-x-lg"></i></button>
    </div>
</template>

<script>
export default {
    data() {
        return {
            hide: false
        }
    },
    props: {
        msg: Boolean,
        msgBody: String,
    },
    mounted() {
        setTimeout(()=>{
            this.hide = true;
        }, 1000)
        setTimeout(()=>{
            this.$emit('close-dialog', 'msg');
        }, 2100)
    },
}
</script>

<style scoped>
.close-btn {
    border: none;
    background: none;
    position: absolute;
    top: 4px;
    right: 4px;
    padding: 4px;
    border-radius: 50%;
}

.close-btn:hover {
    background: #ccc;
}

.popup {
    position: absolute;
    top: 20px;
    right: 20px;
    background: white;
    padding: 0 40px;
    border-radius: 10px;
    opacity: 1;
    box-shadow: 0 5px 5px 0px rgba(0,0,0,0.2);
    transition: 1s ease-in-out;
}

.fade-away {
    transform: translate(0 ,-50vh);
    opacity: 0;
}
</style>