<template>
    <div v-if="fetched" class="main" id="settings-main">
        <form @submit.prevent="updatePrefs" id="preferences">
            <div class="form-section">
                <span>Monthly report format:</span>
                <div>
                    <label for="html">
                        <input type="radio" id="html" value="html" v-model="monthy_report_format">
                        HTML
                    </label>
                    <label for="pdf">
                        <input type="radio" id="pdf" value="pdf" v-model="monthy_report_format">
                        PDF
                    </label>
                </div>
            </div>
            <div class="form-section">
                <label for="reminders">Daily reminders on GSpace:</label>
                <div>
                <label for="yes">
                    <input type="radio" id="yes" value="true" v-model="daily_reminders">
                    Yes
                </label>
                <label for="no">
                    <input type="radio" id="no" value="false" v-model="daily_reminders">
                    No
                </label>
                </div>
            </div>
            <input class="btn" type="submit" value="Update preferences">
        </form>
        <Popup @close-dialog="closeDlg" v-if="msg" :msg-body="msgBody"></Popup>
    </div>
</template>

<script>
import Popup from '@/components/Popup.vue'

export default {
    data() {
        return {
            msg: false,
            msgBody: "",
            fetched : false,
            monthy_report_format : "",
            daily_reminders : null
        }
    },
    created() {
        fetch('http://localhost:5000/api/user', {
            method: 'GET',
            headers: {
                'Authentication-Token' : localStorage.auth_token
            }
        })
        .then( async r => {
            if (r.ok) {
                return r.json();
            } else {
                throw await r.json();
            }
        })
        .then(d => {
            this.fetched = true;
            this.monthy_report_format = d.monthly_report_format
            this.daily_reminders = d.send_daily_reminders
        })
    },
    methods: {
        updatePrefs() {
            fetch('http://localhost:5000/api/settings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authentication-Token': localStorage.auth_token
                },
                body: JSON.stringify({
                    monthly_report_format: this.monthy_report_format,
                    daily_reminders: this.daily_reminders == "true" ? "True" : "False"
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
                this.msg = true;
                this.msgBody = d.message;
            })
            .catch(e => {
                console.log(e);
            })
        },
        closeDlg(type, identifier) {
            if (type === 'msg') {
                this.msg = false;
                this.msgBody = ""
            }
        }
    },
    props: {
        userId: Number
    },
    components: {
        Popup
    }
}
</script>

<style scoped>
#settings-main {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 20px 0;
}

#preferences {
    display: flex;
    flex-direction: column;
    width: 360px;
    gap: 10px;
}

.form-section {
    display: flex;
    justify-content: space-between;
    align-items: center;
}
</style>