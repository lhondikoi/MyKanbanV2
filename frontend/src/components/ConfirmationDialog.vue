<template>
    <div id="confirm">
        <p>{{ confirmMsg }}</p>
        <slot></slot>
        <div class="btns">
            <button class="btn" @click="$emit('confirm', true, 'yes')">Yes</button>
            <button class="btn" @click="$emit('confirm', true, 'no')">No</button>
        </div>
    </div>
</template>

<script>
export default {
    props: {
        confirmMsg: String
    }
}
</script>

<style>
#confirm {
    position: fixed;
    top: 50vh;
    left: 50vw;
    transform: translate(-50%, -50%);
    padding: 20px;
    background: white;
    border-radius: 25px;
    box-shadow: 0 10px 10px 0px rgba(0,0,0,0.2);
}
.btns {
    display: flex;
    justify-content: flex-end;
    gap: 10px
}
</style>