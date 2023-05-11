<template>
    <div>
        <form class="add-card" @submit.prevent="addCard">
            <!-- bubble: focusin, focusout -->
            <!-- not bubble: focus, blur -->
            <input type="text" ref="cardTitle" v-model="newCardTitle" placeholder="Enter a title">
            <textarea v-model="newCardContent" cols="25" rows="5" placeholder="Give a description"></textarea>
            <label for="deadline">Deadline</label>
            <input id="deadline" v-model="newCardDeadline" type="datetime-local">
            <input type="submit" value="Add" >
        </form>
    </div>
</template>

<script>
export default {
    data() {
        return {
            newCardTitle: "",
            newCardContent: "",
            newCardDeadline: null,
        }
    },
    mounted() {
        this.$refs.cardTitle.focus();
    },
    methods: {
        addCard() {
            if (4 <= this.newCardTitle.length <= 50) {
                this.$emit('add-card', this.newCardTitle, this.newCardContent, this.newCardDeadline)
            }
        }
    }
}
</script>

<style scoped>
.add-card {
    position: relative;
    display: flex;
    flex-direction: column;
    padding: 5px;
}

.close-btn {
    border: none;
    background: none;
    position: absolute;
    top: 10px;
    right: 10px;
    line-height: 1.2em;
    border-radius: 50%;
}

.close-btn:hover {
    background: #ccc;
}
</style>