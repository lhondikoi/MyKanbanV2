<template>
    <div class="main" v-if="loading">
        Please wait. Loading data...
    </div>

    <div v-else-if="noBoards" class="main" id="no-boards">
        <div id="no-board-warn">
            <p>You don't have any boards.</p>
            <button class="btn" @click="addBoard(true, '')">Add Board</button>
        </div>

        <Popup @close-dialog="closeDlg" v-if="msg" :msg-body="msgBody"></Popup>
        <AddEntity entity="Board" @add-entity="addBoard" @close-dialog="closeDlg" v-if="addNewBoard"></AddEntity>
    </div>

    <div v-else class="main" id="list-main" :class="[!navCollapse ? 'nav-open' : 'nav-close']">

        <div id="board-nav">
            <span class="board-nav-hdr"><span><i class="bi bi-grid-1x2"></i>This board</span></span>
            <span class="board-nav-elem" @click="exportBoard(boardId)"><span><i class="bi bi-filetype-csv"></i>Export all lists</span></span>
            <span class="board-nav-hdr"><span><i class="bi bi-grid-1x2-fill"></i>Other boards</span></span>
            <span class="board-nav-elem" v-for="board in boards">
                <router-link :to="{ name: 'lists', params: { userId: userId, boardId: board.board_id } }">{{
                    board.board_name
                }}</router-link>
            </span>
            <button class="btn collapse-button" @click="toggleCollapse">
                <div class="corner collapse-button-top">
                    <div class="cutout cutout-top"></div>
                </div><i class="bi" :class="[navCollapse ? 'bi-caret-right-fill' : 'bi-caret-left-fill']"></i>
                <div class="corner collapse-button-bottom">
                    <div class="cutout cutout-bottom"></div>
                </div>
            </button>
        </div>

        <div :id="[lists.length === 0 ? 'empty-board' : 'board-lists']">
            <span v-if="pollerId !== null" id="progress-bar" :style="{ width: progressBarWidth + '%' }"></span>
            <div v-if="lists.length === 0" id="no-list-warn">
                <p>This board doesn't have any lists.</p>
                <button class="btn" @click="addList(true, '')">Add List</button>
            </div>
            <div v-else class="list" v-for="(list, l_index) in lists" @drop="onDrop($event, l_index, list.list_id)"
                @dragenter.prevent @dragover.prevent>
                <div class="list-hdr">
                    <div class="list-title">
                        <input ref="rename" v-if="renameList && renameListIndex === l_index" type="text"
                            @keyup.esc="toggleRename(l_index, true)" @keyup.enter="editList(list.list_id, l_index)"
                            v-model="list.list_name">
                        <strong ref="titles" v-else>{{ list.list_name }}</strong>
                        <button v-if="!renameList || renameListIndex != l_index" @click="toggleRename(l_index, true)"
                            class="btn btn-transparent"><i class="bi bi-pencil-square"></i></button>
                        <button v-else-if="renameList && renameListIndex === l_index"
                            @click="toggleRename(l_index, true)" class="btn btn-transparent"><i
                                class="bi bi-x-lg"></i></button>
                    </div>
                    <button @click="toggleDropdown(l_index)" class="btn btn-transparent"><i
                            class="bi bi-three-dots"></i></button>
                    <div v-if="dropdownOpen && dropdownOpenIndex === l_index" class="dropdown-menu">
                        <div class="dropdown-tip"></div>
                        <ul class="dropdown-list">
                            <li @click="delList(false, '', list.list_id, l_index)">Delete list<i
                                    class="bi bi-trash3"></i></li>
                            <li @click="exportList(list.list_id, l_index)">Export list<i class="bi bi-filetype-csv"></i>
                            </li>
                        </ul>
                    </div>
                </div>

                <div class="cards">
                    <div v-for="(card, c_index) in list.cards" class="card"
                        :class="[card.completed ? 'completed-card' : !card.deadline ? 'pending-card' : new Date(card.deadline).getTime() < new Date().getTime() ? 'overdue-card' : 'pending-card']"
                        draggable="True" @dragstart="startDrag($event, l_index, c_index, card.card_id)"
                        @dragenter.prevent @dragover.prevent>
                        <div v-if="editCard && editCardIndex === c_index && editCardListIndex === l_index"
                            class="card-edit">
                            <form
                                @submit.prevent="editCardDetails(card.card_id, card.title, card.content, card.deadline)">
                                <input type="text" ref="editCardTitle" v-model="card.title" placeholder="Enter a title">
                                <textarea v-model="card.content" cols="25" rows="5"
                                    placeholder="Give a description"></textarea>
                                <label for="deadline">Deadline</label>
                                <input id="deadline" v-model="card.deadline" type="datetime-local">
                                <input type="submit" value="Save">
                            </form>
                            <button @click="toggleEditCard(l_index, c_index)">Cancel</button>
                        </div>
                        <div v-else-if="!editCard || editCardIndex !== c_index || editCardListIndex !== l_index"
                            class="card-card">
                            <span>{{ card.title }}</span>
                            <div v-if="card.content" class="card-inner card-content">
                                <i class="bi bi-justify-left"></i>
                                <span>{{ card.content }}</span>
                            </div>
                            <div v-if="card.deadline" class="card-inner card-deadline">
                                <i class="bi bi-clock-history"></i>
                                <span>{{ parseDate(card.deadline) }}</span>
                            </div>
                            <div class="card-card-btns">
                                <button class="btn btn-transparent" @click="delCard(l_index, c_index, card.card_id)"><i class="bi bi-trash3"></i></button>
                                <button class="btn btn-transparent" @click="toggleEditCard(l_index, c_index)"><i class="bi bi-pencil-square"></i></button>
                                <input @click="completeCard(l_index, c_index, card.card_id, card.completed ? false : true)"
                                    type="checkbox" :checked="card.completed ? true : false">
                            </div>
                        </div>
                    </div>
                </div>

                <AddCard v-if="addNewCard && addNewCardListIndex === l_index" @add-card="addCard" @cancel-add-card="toggleAddCard(list.list_id, l_index)"></AddCard>
                <button v-if="!addNewCard || addNewCardListIndex != l_index" @click="toggleAddCard(list.list_id, l_index)" class="btn">Add Card</button>
                <button v-else-if="addNewCard && addNewCardListIndex === l_index" @click="toggleAddCard(list.list_id, l_index)" class="btn">Cancel</button>
            </div>
            <button v-if="lists.length !== 0" class="btn" @click="addList(true, '')">Add List</button>

            <AddEntity entity="List" @add-entity="addList" @close-dialog="closeDlg" v-if="addNewList"></AddEntity>
            <ConfirmationDialog v-if="delListModal" confirm-msg="Are you sure you want to delete this list?"
                @confirm="delList">
                <template v-if="delListModal && delListHasCards">
                    <span>Move cards to:</span>
                    <select class="move-lists" v-model="moveListId">
                        <option v-for="list in moveToLists" :value="list.list_id">
                            {{ list.list_name }}
                        </option>
                    </select>
                </template>
            </ConfirmationDialog>
        </div>
        <Popup @close-dialog="closeDlg" v-if="msg" :msg-body="msgBody"></Popup>
    </div>
</template>

<script>
import AddEntity from '@/components/AddEntity.vue'
import AddCard from '@/views/lists/AddCard.vue'
import ConfirmationDialog from '@/components/ConfirmationDialog.vue'
import Popup from '@/components/Popup.vue'

export default {
    name: 'ListView',
    data() {
        return {
            loading: true,

            boards: [],
            noBoards: false,
            lists: [],
            navCollapse: false,

            addNewBoard: false,
            addNewList: false,
            addNewCard: false,
            addNewCardListId: -1,
            addNewCardListIndex: -1,

            delListModal: false,
            delListHasCards: false,
            delListId: -1,
            delListIndex: -1,
            moveListId: -1,

            renameList: false,
            renameListIndex: -1,
            renameInitial: '',

            editCard: false,
            editCardIndex: -1,
            editCardListIndex: -1,
            initialCardTitle: "",
            initialCardContent: "",
            initialCardDeadline: "",

            dropdownOpen: false,
            dropdownOpenIndex: -1,

            msg: false,
            msgBody: '',

            pollerId: null,
            progressBarWidth: 0,
        }
    },
    created() {
        fetch(`http://localhost:5000/api/boards`, {
            headers: {
                'Authentication-Token': localStorage.auth_token
            }
        })
            .then(r => { if (r.ok) { return r.json() } })
            .then(d => {
                this.boards = d
                if (this.boards.length === 0) {
                    this.noBoards = true;
                    this.loading = false;
                    return;
                }
                if (this.boardId == -1) {
                    this.$router.push({ name: 'lists', params: { userId: this.userId, boardId: this.boards[0].board_id } })
                    return;
                }
                fetch(`http://localhost:5000/api/boardlists/${this.boardId}`, {
                    headers: {
                        'Authentication-Token': localStorage.auth_token
                    }
                })
                    .then(r => { if (r.ok) { return r.json() } })
                    .then(d => {
                        this.lists = d;
                        this.loading = false;
                    })
            })
    },
    methods: {
        startDrag(event, list_idx, card_idx, card_id) {
            event.dataTransfer.dropEffect = 'move';
            event.dataTransfer.effectAllowed = 'move';
            event.dataTransfer.setData('listIndex', list_idx)
            event.dataTransfer.setData('cardIndex', card_idx)
            event.dataTransfer.setData('cardId', card_id)
        },
        onDrop(event, list_idx, list_id) {
            if (event.dataTransfer.getData('listIndex') != list_idx) {
                if (this.lists[list_idx].cards.find(card => card.card_id > event.dataTransfer.getData('cardId')) !== undefined) {
                    this.lists[list_idx].cards.splice(
                        this.lists[list_idx].cards.indexOf(this.lists[list_idx].cards.find(card => card.card_id > event.dataTransfer.getData('cardId'))) === 0 ? 0 : this.lists[list_idx].cards.indexOf(this.lists[list_idx].cards.find(card => card.card_id > event.dataTransfer.getData('cardId'))),
                        0,
                        this.lists[event.dataTransfer.getData('listIndex')].cards[event.dataTransfer.getData('cardIndex')]
                    );
                } else {
                    this.lists[list_idx].cards.push(this.lists[event.dataTransfer.getData('listIndex')].cards[event.dataTransfer.getData('cardIndex')])
                }
                this.lists[event.dataTransfer.getData('listIndex')].cards.splice(event.dataTransfer.getData('cardIndex'), 1);
                fetch(`http://localhost:5000/api/card/${event.dataTransfer.getData('cardId')}/move_to_list/${list_id}`, {
                    method: 'PUT',
                    headers: {
                        'Authentication-Token': localStorage.auth_token
                    }
                })
                    .then(async r => { if (r.ok) { return r.json() } else { throw await r.json() } })
                    .then(d => {
                        this.msg = true;
                        this.msgBody = "Moved successfully"
                    })
                    .catch(e => console.log(e))
            }


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
                        .then(r => {
                            if (r.ok) {
                                return r.json()
                            }
                        })
                        .then(d => {
                            this.boards.push(d);
                            this.$router.push({ name: 'lists', params: { userId: this.userId, boardId: d.board_id } })
                            this.addNewBoard = false;
                        })
                } else {
                    this.addNewBoard = false;
                }
            }
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
                        console.log(d)
                        this.pollTask(d.task_id);
                    })
                    .catch(e => console.log(e))
            };
        },
        addList(open_modal, list_name) {
            if (open_modal) {
                this.addNewList = true;
            } else {
                if (list_name != '') {
                    fetch('http://localhost:5000/api/list', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authentication-Token': localStorage.auth_token
                        },
                        body: JSON.stringify({
                            'board_id': this.boardId,
                            'list_name': list_name
                        })
                    })
                        .then(r => { if (r.ok) { return r.json() } })
                        .then(d => {
                            this.lists.push(d);
                            this.addNewList = false;
                        })
                } else {
                    this.addNewList = false;
                }
            }
        },
        delList(confirmed, action, l_id, l_idx) {
            if (!confirmed) {
                this.toggleDropdown(l_idx);
                this.delListId = l_id;
                this.delListIndex = l_idx;
                this.delListModal = true;
                this.delListHasCards = this.lists[l_idx].cards.length != 0 ? true : false;
                if (this.delListHasCards) {
                    this.moveToLists = this.lists.filter(l => l.list_id != this.delListId);
                }
            } else {
                if (action === 'yes') {
                    if (this.moveListId === -1) {
                        fetch(`http://localhost:5000/api/list/${this.delListId}`, {
                            method: 'DELETE',
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
                                this.delListModal = false;
                                this.lists.splice(this.delListIndex, 1);

                                this.msg = true;
                                this.msgBody = d;

                                this.delListId = -1;
                                this.delListIndex = -1;
                                this.delListHasCards = false;
                                this.moveToLists = [];
                            })
                            .catch(e=>console.log(e))
                    } else {
                        fetch(`http://localhost:5000/api/list/${this.delListId}/delete_move/${this.moveListId}`, {
                            method: 'DELETE',
                            headers: {
                                'Authentication-Token': localStorage.auth_token
                            }
                        })
                            .then(r => { if (r.ok) { return r.json() } })
                            .then(d => {
                                this.delListModal = false;
                                // check if the list the cards need to be moved to has a cards property
                                // if yes, then leave it be, if no (meaning list has no cards) initialize a cards : [] key-value pair on the list Object
                                // then push the cards of the deleted list to the new list
                                // then delete the old list
                                this.lists.filter((l) => { return l.list_id === this.moveListId })[0].cards = this.lists.filter((l) => { return l.list_id === this.moveListId })[0].cards ? this.lists.filter((l) => { return l.list_id === this.moveListId })[0].cards : []
                                this.lists.filter((l) => { return l.list_id === this.moveListId })[0].cards.push(...this.lists[this.delListIndex].cards)
                                this.lists.splice(this.delListIndex, 1)

                                this.msg = true;
                                this.msgBody = d;
                                this.delListId = -1;
                                this.delListIndex = -1;
                                this.delListHasCards = false;
                                this.moveListId = -1;
                                this.moveToLists = [];
                            })
                    }
                } else {
                    this.delListModal = false;

                    this.delListId = -1;
                    this.delListIndex = -1;

                    this.moveListId = -1;
                }
            }
        },
        editList(l_id, l_idx) {
            if (this.lists[l_idx].list_name.length >= 4) {
                fetch(`http://localhost:5000/api/list/${l_id}`,
                {
                        method: 'PUT',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authentication-Token': localStorage.auth_token
                        },
                        body: JSON.stringify({
                            'list_name': this.lists[l_idx].list_name
                        })
                    }
                )
                .then(async r => {
                    if (r.ok) {
                            return r.json()
                        } else {
                            throw await r.json();
                        }
                    })
                    .then(d => {
                        this.toggleRename(l_idx, false);
                    })
                    .catch(e=> {
                        this.toggleRename(l_idx, true);
                    })
            }
        },
        exportList(l_id, l_idx) {
            this.toggleDropdown(l_idx)
            if (this.pollerId !== null) {
                this.msg = true;
                this.msgBody = "Please wait for the previous export task to finish."
            } else {
                fetch(`http://localhost:5000/api/list/${l_id}/export`, {
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
                    .catch(e => console.log(e))
            }
        },
        pollTask(task_id) {
            this.pollerId = setInterval(() => {
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
                    .then(d => {
                        console.log(d)
                        this.progressBarWidth = parseInt((d.current / d.total) * 100);
                        if (d.state == 'SUCCESS' || d.state == 'FAILURE') {
                            clearInterval(this.pollerId);
                            this.pollerId = null;
                            this.progressBarWidth = 0;
                            this.downloadExport(d.result.file_name);
                        }
                    })
                    .catch(e => {
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
                .then(blob => {
                    window.location.assign(window.URL.createObjectURL(blob));
                    this.msg = true;
                    this.msgBody = "Your file is ready for downloading"
                });
        },
        addCard(title, content, deadline) {
            fetch('http://localhost:5000/api/card', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authentication-Token': localStorage.auth_token
                },
                body: JSON.stringify({
                    'list_id': this.addNewCardListId,
                    'title': title,
                    'content': content,
                    ...(deadline && {'deadline': deadline + ":00"})
                })
            })
                .then(async r => {
                    if (r.ok) {
                        return r.json();
                    } else {
                        throw await r.json();
                    }
                })
                .then(d => {
                    this.lists[this.addNewCardListIndex].cards.push(d);
                    this.addNewCard = false;
                    this.addNewCardListId = -1;
                    this.addNewCardListIndex = -1;
                    this.msg = true;
                    this.msgBody = "Successfully added card!"
                })
                .catch(e => console.log(e))
        },
        editCardDetails(c_id, title, content, deadline) {
            console.log(deadline);
            fetch(`http://localhost:5000/api/card/${c_id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authentication-Token': localStorage.auth_token
                },
                body: JSON.stringify({
                    'card_id': c_id,
                    ...(title != this.initialCardTitle && 4 <= title <= 50 && { 'title': title }),
                    ...(content != this.initialCardContent && { 'content': content }),
                    ...(deadline != this.initialCardDeadline && { 'deadline': deadline + ":00" })
                })
            })
                .then(async r => {
                    if (r.ok) {
                        return r.json()
                    } else {
                        throw await r.json()
                    }
                })
                .then(d => {
                    this.lists[this.editCardListIndex].cards[this.editCardIndex] = d;
                    this.editCard = false;
                    this.editCardIndex = -1;
                    this.editCardListIndex = -1;
                    this.initialCardTitle = ""
                    this.initialCardContent = ""
                    this.initialCarddeadline = ""
                })
        },
        completeCard(l_idx, c_idx, c_id, status) {
            fetch(`http://localhost:5000/api/card/${c_id}/complete`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authentication-Token': localStorage.auth_token
                },
                body: JSON.stringify({
                    'completed': status
                })
            })
                .then(r => { if (r.ok) { return r.json() } })
                .then(d => { if (d === 'Successfully updated') { this.lists[l_idx].cards[c_idx].completed = status } })
        },
        delCard(l_idx, c_idx, c_id) {
            fetch(`http://localhost:5000/api/card/${c_id}`, {
                method: 'DELETE',
                headers: {
                    'Authentication-Token': localStorage.auth_token
                }
            })
                .then(async r => { if (r.ok) { return r.json() } })
                .then(d => {
                    this.lists[l_idx].cards.splice(c_idx, 1);
                    this.msg = true;
                    this.msgBody = d;
                })
        },
        toggleCollapse() {
            this.navCollapse = !this.navCollapse;
        },
        toggleDropdown(l_idx) {
            if (!this.dropdownOpen) {
                this.dropdownOpen = true;
                this.dropdownOpenIndex = l_idx
            } else {
                if (l_idx === this.dropdownOpenIndex) {
                    this.dropdownOpen = false;
                    this.dropdownOpenIndex = -1
                } else {
                    this.dropdownOpenIndex = l_idx
                }
            }
        },
        toggleRename(l_idx, reset) {
            if (!this.renameList) {
                this.renameList = true;
                this.renameListIndex = l_idx;
                this.renameInitial = this.lists[l_idx].list_name;
                this.$nextTick(() => {
                    this.$refs.rename[0].focus();
                })
            } else {
                if (l_idx === this.renameListIndex) {
                    if (reset) {
                        this.lists[l_idx].list_name = this.renameInitial;
                    }
                    this.renameList = false;
                    this.renameListIndex = -1;
                    this.renameInitial = '';
                } else {
                    this.lists[this.renameListIndex].list_name = this.renameInitial;
                    this.renameListIndex = l_idx;
                    this.renameInitial = this.lists[l_idx].list_name;
                    this.$nextTick(() => {
                        this.$refs.rename[0].focus()
                    });
                }
            }
        },
        toggleAddCard(l_id, l_index) {
            if (!this.addNewCard) {
                this.addNewCard = true;
                this.addNewCardListId = l_id
                this.addNewCardListIndex = l_index;
            } else if (this.addNewCardListIndex === l_index) {
                this.addNewCard = false;
                this.addNewCardListId = -1;
                this.addNewCardListIndex = -1;
            } else {
                this.addNewCardListId = l_id;
                this.addNewCardListIndex = l_index;
            }
        },
        toggleEditCard(l_idx, c_idx) {
            if (!this.editCard) {
                this.editCard = true;
                this.editCardIndex = c_idx;
                this.editCardListIndex = l_idx;
                this.initialCardTitle = this.lists[l_idx].cards[c_idx].title
                this.initialCardContent = this.lists[l_idx].cards[c_idx].content
                this.initialCarddeadline = this.lists[l_idx].cards[c_idx].deadline
            } else if (this.editCardIndex === c_idx && this.editCardListIndex === l_idx) {
                this.lists[l_idx].cards[c_idx].title = this.initialCardTitle
                this.lists[l_idx].cards[c_idx].content = this.initialCardContent
                this.lists[l_idx].cards[c_idx].deadline = this.initialCarddeadline
                this.editCard = false;
                this.editCardIndex = -1;
                this.editCardListIndex = -1;
            } else {
                this.lists[this.editCardListIndex].cards[this.editCardIndex].title = this.initialCardTitle
                this.lists[this.editCardListIndex].cards[this.editCardIndex].content = this.initialCardContent
                this.lists[this.editCardListIndex].cards[this.editCardIndex].deadline = this.initialCarddeadline
                this.editCardIndex = c_idx;
                this.editCardListIndex = l_idx;
                this.initialCardTitle = this.lists[l_idx].cards[c_idx].title
                this.initialCardContent = this.lists[l_idx].cards[c_idx].content
                this.initialCarddeadline = this.lists[l_idx].cards[c_idx].deadline
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
        }, parseDate(timestamp) {
            let dt = Date.parse(timestamp)
            let datetime = new Date(dt)
            return datetime.toDateString();
        }                            
    },
    props: {
        userId: Number,
        boardId: Number
    },
    components: {
        AddEntity, AddCard, ConfirmationDialog, Popup
    }
}
</script>

<style scoped>
input[type="text"] {
    border: none;
    font-size: 0.9em;
    border-bottom: 1px solid #aaa;
    padding-bottom: 0.3em;
}

input[type="text"]:focus,
input[type="text"]:active {
    outline: none;
    border-bottom: 1px solid #333;
}

a {
    color: inherit;
    text-decoration: none;
}

#no-boards {
    display: grid;
    place-items: center;
}

#no-boards > #no-board-warn,
#no-list-warn {
    display: flex;
    flex-direction: column;
    align-items: center;
}

.dropdown-menu {
    position: absolute;
    top: 0;
    right: 0;
    z-index: 1;
    transform: translate(calc(100% - 40px), 30px);
}

.dropdown-list {
    list-style: none outside none;
    border-radius: 5px;
    box-shadow: 0px 0px 2px 1px rgba(0, 0, 0, 0.35);
    display: flex;
    margin: 0;
    padding: 0;
    padding-top: 8px;
    background: #fff;
    flex-direction: column;
    min-width: 150px;
    overflow: hidden;
}

.dropdown-tip {
    background: #fff;
    width: 10px;
    height: 10px;
    margin: 0;
    transform: translate(130%, 50%) rotate(45deg);
    box-shadow: 0px 0px 2px 1px rgba(0, 0, 0, 0.35);
    clip-path: inset(-2px 0px 0px -2px)
}

.dropdown-list>li {
    padding: 8px;
    font-size: 0.9em;
    display: flex;
    justify-content: space-between;
}

.dropdown-list>li:hover {
    cursor: pointer;
    background: rgba(0, 0, 0, 0.2)
}

.dropdown-menu:has(> li.hover) .dropdown-tip {
    background: rgba(0, 0, 0, 0.2)
}

#list-main {
    overflow: hidden;
    display: grid;
    -webkit-transition: 250ms ease-out;
    -moz-transition: 250ms ease-out;
    -o-transition: 250ms ease-out;
    transition: 250ms ease-out;
}

.nav-open {
    grid-template-columns: 200px 1fr;
}

.nav-close {
    grid-template-columns: 0px 1fr;
}

#board-nav {
    color: var(--darkgrey);
    display: flex;
    flex-direction: column;
    background: #fff;
    position: relative;
    border-right: 1px solid var(--slightlydarkbluishgrey);
}

.board-nav-hdr {
    overflow: hidden;
}

.board-nav-hdr>* {
    display: flex;
    gap: 10px;
    width: 180px;
    padding: 10px;
    font-size: 0.9em;
    font-weight: 600;
    color: #333;
    position: relative;
}

.board-nav-hdr>*::after {
    content: '';
    bottom: 0;
    left: 5px;
    width: 190px;
    position: absolute;
    border-bottom: 1px solid var(--slightlydarkbluishgrey);
}

.board-nav-elem {
    overflow: hidden;
}

.board-nav-elem:hover {
    cursor: pointer;
    background: var(--darkblue);
    color: white;
}

.board-nav-elem>* {
    padding: 10px 20px;
    width: 160px;
    display: flex;
    gap: 5px;
}

.collapse-button {
    color: var(--darkgrey);
    border: none;
    position: absolute;
    right: 0;
    top: 0;
    transform: translate(100%, calc((100vh - 40px)/2 - 50%));
    border-right: 1px solid var(--slightlydarkbluishgrey);
    background: #fff;
    height: 60px;
    width: 20px;
    padding: 0;
    border-radius: 0 10px 10px 0;
    z-index: 1;
}

.collapse-button:hover {
    cursor: pointer;
}

.corner {
    position: absolute;
    height: 10px;
    width: 10px;
    background: inherit;
    overflow: hidden;
}

.collapse-button-top {
    top: 0;
    transform: translateY(-100%);
}

.collapse-button-bottom {
    bottom: 0;
    transform: translateY(100%);
}

.cutout {
    height: 20px;
    width: 20px;
    background: var(--offwhite);
    border: 1px solid var(--slightlydarkbluishgrey);
    border-radius: 50%;
    position: absolute;
}

.cutout-top {
    position: absolute;
    bottom: 0;
}

.cutout-bottom {
    position: absolute;
    top: 0;
}

#empty-board {
    display: grid;
    place-items: center;
}

#board-lists {
    position: relative;
    display: flex;
    padding: 10px 10px 10px 30px;
    gap: 15px;

    align-items: flex-start;
    justify-content: flex-start;
    align-content: flex-start;
    overflow: auto;
}

#progress-bar {
    position: absolute;
    top: 0;
    left: 0;
    height: 5px;
    background: red;
    /* fallbacks for google, mozila & opera respectively */
    -webkit-transition: 250ms ease-in-out;
    -moz-transition: 250ms ease-in-out;
    -o-transition: 250ms ease-in-out;
    transition: 250ms ease-in-out;
}

.list {
    display: flex;
    flex-direction: column;
    position: relative;
    gap: 10px;
    background: white;
    color: #333;
    box-shadow: 2px 2px 5px 1px rgba(85, 85, 85, 0.342);
    padding: 10px;
    border-radius: 5px;
    min-width: 250px;
    max-width: 250px;
}

.list-hdr {
    display: flex;
    justify-content: space-between;
}

.cards {
    display: flex;
    flex-direction: column;
    gap: 10px;
    background: white;
    color: #333;
    min-height: 10px;
    max-height: 480px;
    overflow: auto;
}

.card {
    border-radius: 5px;
    padding: 8px;
    background: rgb(233, 237, 238);
}

.card-card {
    display: flex;
    flex-direction: column;
    gap: 8px;
    align-items: stretch;
    justify-content: space-between;
}

.card-card-btns {
    display: flex;
    justify-content: space-between;
    position: relative;
}

.card-card-btns::before {
    left: 1%;
    position: absolute;
    height: 1px;
    width: 98%;
    content: '';
    background: #888;
}

.card-inner {
    padding-left: 5px;
    display: flex;
    gap: 10px;
    color: #555;
    font-size: 0.9em;
}

.pending-card {
    border-left: 8px solid rgb(150, 150, 150);
}

.overdue-card {
    border-left: 8px solid rgb(255, 94, 94);
}

.completed-card {
    border-left: 8px solid rgb(108, 238, 108);
}
</style>