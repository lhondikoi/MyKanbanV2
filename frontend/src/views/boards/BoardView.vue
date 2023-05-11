<template>
    <div v-if="boards.length === 0" class="main" id="no-boards">
        <div id="no-board-warn">
            <p>You don't have any boards.</p>
            <button class="btn" @click="addBoard(true, '')">Add Board</button>
        </div>
        <Popup @close-dialog="closeDlg" v-if="msg" :msg-body="msgBody"></Popup>
        <AddEntity entity="Board" @add-entity="addBoard" @close-dialog="closeDlg" v-if="addNewBoard"></AddEntity>
    </div>
    <div v-else class="main" id="board-main">
        <div class="board" v-for="(board, index) in boards">
            <div class="board-title">
                <input v-if="renameBoard && renameBoardIndex === index" type="text" @keyup.esc="toggleRename(index, true)" @keyup.enter="editBoard(board.board_id, index)" v-model="board.board_name">
                <strong v-else class="board-name" @click="openListView(board.board_id)">{{ board.board_name }}</strong>
                <button v-if="!renameBoard || renameBoardIndex != index" @click="toggleRename(index, true)" class="btn btn-transparent"><i class="bi bi-pencil-square"></i></button>
                <button v-else-if="renameBoard && renameBoardIndex === index" @click="toggleRename(index, true)" class="btn btn-transparent"><i class="bi bi-x-lg"></i></button>
            </div>
            <div class="board-btns">
                <button class="board-btn" @click="delBoard(false, '', board.board_id, index)"><i class="bi bi-trash-fill"></i></button>
                <button class="board-btn" @click="exportBoard(board.board_id)"><i class="bi bi-filetype-csv"></i></button>
            </div>
        </div>
        <button @click="addBoard(true, '')">Add Board</button>
        
        <Popup @close-dialog="closeDlg" v-if="msg" :msg-body="msgBody"></Popup>
        <AddEntity entity="Board" @add-entity="addBoard" @close-dialog="closeDlg" v-if="addNewBoard"></AddEntity>
        <EditBoard @edit-board-name="editBoard" @close-dialog="closeDlg" v-if="editBoardName" :currentBoardName="editBoardNameValue"></EditBoard>
        <ConfirmationDialog v-if="delBoardModal" confirm-msg="Are you sure you want to delete this board?" @confirm="delBoard"></ConfirmationDialog>
    </div>
</template>

<script>
import ConfirmationDialog from '@/components/ConfirmationDialog.vue'
import AddEntity from '@/components/AddEntity.vue'
import Popup from '@/components/Popup.vue';

export default {
    name: 'BoardView',
    data() {
        return {
            boards: [],
            
            msg: false,
            msgBody: "",

            addNewBoard: false,

            renameBoard: false,
            renameBoardIndex: -1,
            renameInitial: '',

            editBoardName: false,
            editBoardNameValue: "",
            editBoardNameId: -1,
            editBoardNameIndex: -1,

            delBoardModal: false,
            delBoardId: -1,
            delBoardIndex: -1,

            pollerId: null,
        }
    },
    methods: {
        openListView(board_id) {
            this.$router.push({name: 'lists', params: {userId: this.userId, boardId: board_id}})
        },
        exportBoard(board_id) {
            if (this.pollerId !== null) {
                this.msg = True;
                this.msgBody = "Please wait for the previous export task to finish."
            } else {
                fetch(`http://localhost:5000/api/board/${board_id}/export`, {
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
                    this.pollTask(d.task_id);
                })
                .catch(e=>console.log(e))
            };
        },
        pollTask(task_id) {
            this.pollerId = setInterval(()=>{
                fetch(`http://localhost:5000/api/task/${task_id}`, {
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
                .then(d=>{
                    this.progressBarWidth = parseInt((d.current / d.total) * 100);
                    if (d.state == 'SUCCESS' || d.state == 'FAILURE') {
                        clearInterval(this.pollerId);
                        this.pollerId = null;
                        this.progressBarWidth = 0;
                        this.downloadExport(d.result.file_name);
                    }
                })
                .catch(e=>{
                    console.log(e);
                    clearInterval(this.pollerId);
                    this.pollerId = null;
                    this.progressBarWidth = 0;
                })
            }, 1000)
        },
        downloadExport(file_name) {
            fetch(`http://localhost:5000/download/${file_name}`, {
                headers: {
                    'Authentication-Token': localStorage.auth_token
                }
            })
            .then(r => {
                return r.blob()
            })
            .then( blob => {
                window.location.assign(window.URL.createObjectURL(blob));
                this.msg = true;
                this.msgBody = "Your file is ready for downloading"
            });
        },
        addBoard(open_modal, board_name) {
            if (open_modal) {
                this.addNewBoard = true;
            } else {
                if (board_name != '') {
                    fetch(`http://localhost:5000/api/board`,
                    {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authentication-Token': localStorage.auth_token
                        },
                        body: JSON.stringify({
                            'user_id': this.userId,
                            'board_name': board_name
                        })
                    })
                    .then(r=>{
                        if (r.ok) {
                            return r.json()
                        }
                    })
                    .then(r=>{
                        this.boards.push(r);
                        this.addNewBoard = false;
                    })
                } else {
                    this.addNewBoard = false;
                }
            }
        },
        delBoard(confirmed, action, board_id, b_idx) {
            if (!confirmed) {
                this.delBoardModal = true;
                this.delBoardId = board_id;
                this.delBoardIndex = b_idx;
            } else {
                if (action === 'yes') {
                    fetch(`http://localhost:5000/api/board/${this.delBoardId}`,{
                        method: 'DELETE',
                        headers: {
                            'Authentication-Token': localStorage.auth_token
                        }
                    })
                    .then(async r=>{
                        if (r.ok) {return r.json()}
                        else {throw await r.json()}
                    })
                    .then(d=>{
                        this.msg = true;
                        this.msgBody = d;
                        this.boards.splice(this.delBoardIndex, 1);
                    })
                    .catch(e=>console.log(e))
                }
                this.delBoardModal = false;
                this.delBoardId = -1;
                this.delBoardIndex = -1;
            }
        },
        editBoard(b_id, b_idx) {
            if (this.boards[b_idx].board_name.length >= 4) {
                fetch(`http://localhost:5000/api/board/${b_id}`,
                {
                        method: 'PUT',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authentication-Token': localStorage.auth_token
                        },
                        body: JSON.stringify({
                            'board_name': this.boards[b_idx].board_name
                        })
                    }
                )
                .then(async r => {
                    if (r.ok) {
                        return r.json()
                    } else {
                        throw await r.json()
                    }
                })
                .then(d=>{
                    this.toggleRename(b_idx, false);
                })
                .catch(e=>{
                    this.toggleRename(b_idx, true);
                })
            }
        },
        toggleRename(b_idx, reset) {
            if (!this.renameBoard) {
                this.renameBoard = true;
                this.renameBoardIndex = b_idx;
                this.renameInitial = this.boards[b_idx].board_name;
            } else {
                if (b_idx === this.renameBoardIndex) {
                    if (reset) {
                        this.boards[b_idx].board_name = this.renameInitial;
                    }
                    this.renameBoard = false;
                    this.renameBoardIndex = -1
                    this.renameInitial = ''
                } else {
                    this.renameBoardIndex = b_idx;
                    this.renameInitial = this.boards[b_idx].board_name;
                }
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
    },
    created() {
        fetch(`http://localhost:5000/api/boards`, {
            headers: {
                'Authentication-Token': localStorage.auth_token
            }
        })
        .then(r=>{if (r.ok){ return r.json()}})
        .then(d=>this.boards = d)
    },
    props: {
        userId: Number.parseInt()
    },
    components: {
        Popup, AddEntity, ConfirmationDialog
    }
}
</script>

<style>
#board-main {
    display: flex;
    padding: 10px;
    flex-wrap: wrap;
    gap: 15px;
    
    align-items: flex-start;
    justify-content: flex-start;
    align-content: flex-start;
}

.board {
    position: relative;
    width: 200px;
    height: 100px;
    background: white;
    color: #333;
    border-radius: 5px;
    padding: 10px;
    box-shadow: 2px 2px 5px 1px rgba(85, 85, 85, 0.342);
    border-bottom: 10px solid var(--darkblue);
    
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
}

.board-name {
    width: 90%;
}

.board-name i {
    display: none;
}

.board-name:hover {
    cursor: pointer;
}

.board-btns {
    display: none;
    position: absolute;
    top: 10px;
    right: 10px;
}

.board:hover .board-btns {
    display: flex;
    flex-direction: column;
    align-self: flex-start;
    gap: 5px;
}

.board-btn {
    border: 0;
    width: 25px;
    height: 25px;
    border-radius: 50%;
    /* padding: 3px; */
    background:rgb(255, 255, 255);

    display: flex;
    align-items: center;
    justify-content: center;
}

.board-btn:hover {
    background:rgb(0, 255, 136);
}

#no-boards {
    display: grid;
    place-items: center;
}

#no-board-warn {
    display: flex;
    flex-direction: column;
    align-items: center;
}
</style>