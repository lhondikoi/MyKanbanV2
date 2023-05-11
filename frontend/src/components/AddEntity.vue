<template>
    <div id="add-entity">
        <p>Add {{ entity }}</p>
        <input ref="newBoardInput" type="text" v-model="newEntityName" @keyup.enter="$emit('add-entity', false, newEntityName)">
        <button class="modal-btn" @click="$emit('add-entity', false, newEntityName)">Add {{ entity }}</button>
        <button class="close-btn" @click="$emit('close-dialog', 'add-entity', entity)"><i class="bi bi-x"></i></button>
    </div>
</template>

<script>
export default {
    data() {
        return {
            newEntityName: ""
        }
    },
    mounted() {
        this.$refs.newBoardInput.focus();
    },
    props: {
        entity: String
    }
}
</script>

<style scoped>
input[type="text"] {
    border: none;
    border-bottom: 1px solid #aaa;
    padding-bottom: 0.3em;
}

input[type="text"]:focus, input[type="text"]:active {
    outline: none;
    border-bottom: 1px solid #333;
} 

.modal-btn {
    border: none;
    padding: 5px 0;
    border-radius: 5px;
    background: var(--slightlydarkbluishgrey);
    color: white
}

.modal-btn:hover {
    cursor: pointer;
    background: var(--darkgrey);
}

p {
    margin: 0;
}

#add-entity {
    position: fixed;
    top: 50vh;
    left: 50vw;
    transform: translate(-50%, -50%);
    background: white;
    padding: 25px;
    border-radius: 20px;

    display: flex;
    flex-direction: column;
    gap: 20px;
    width: 300px;
    box-shadow: 0 10px 10px 0px rgba(0,0,0,0.2);
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