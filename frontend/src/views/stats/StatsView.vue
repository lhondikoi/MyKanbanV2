<template>
    <div class="main" id="stats-main">
        <section class="stats" id="piechart-section">
            <div class="hdr">
                <h3>Card Breakdown</h3>
                <form @submit.prevent>
                    <label for="list-select">Card breakdown for a particular list: </label>
                    <select id="list-select" v-model="breakdownListId">
                        <option value="-1">None</option>
                        <option v-for="list in userLists" :value="list.list_id">
                            {{ list.board_name + "-" + list.list_name }}
                        </option>
                    </select>
                </form>
            </div>
            <p class="txt">This chart shows you the proportion of completed, pending and overdue cards across all your boards or a particular list.</p>
            <PieChart class="chart" :user-id="userId" :key="breakdownListId" :list-id="breakdownListId"/>
        </section>
        <section class="stats" id="timeline-section">
            <h3 class="hdr">Cards completed per day</h3>
            <p class="txt">This chart shows you the number of cards you have completed per day in the last week.</p>
            <LineChart class="chart" :user-id="userId"/>
        </section>
    </div>
</template>

<script>
import PieChart from '@/views/stats/PieChart.vue'
import LineChart from '@/views/stats/LineChart.vue'

export default {
    name: 'StatsView',
    data() {
        return {
            breakdownListId: -1,
            userLists: []
        }
    },
    props: {
        userId: Number
    },
    created() {
        fetch('http://localhost:5000/api/lists', {
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
            this.userLists = d
        })
        .catch(e => {
            console.log(e)
        })
    },
    methods: {
    },
    components: {
        PieChart, LineChart
    }
}
</script>

<style>
#stats-main {
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-template-rows: 1fr 1fr 1fr;
    padding: 20px;
    gap: 20px;
    overflow: auto;
}

#list-select {
    width: 50%;
    padding: 5px;
    border-radius: 5px;
    margin-top: 10px;
}

.stats {
    display: grid;
    grid-template-columns: 2fr 1fr;
    grid-template-rows: 2fr 1fr;
    /* height: 300px; */
    gap: 10px;
}

.hdr {
    /* background: red; */
    grid-column: 1 / 2;
    grid-row: 2 / 3;
    margin: 0;
}

.txt {
    /* background: yellow; */
    margin: 0;
}

.chart {
    /* background: green; */
    grid-row: 1 / 2;
    grid-column: 1 / 3;
}

.stats {
    background: #fff;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0px 0px 5px 0px #888;
}

@media screen and (max-width: 800px) {
	#stats-main {
        grid-template-columns: 1fr;
    }

    .stats {
        grid-template-columns: 1fr;
    }
}
</style>