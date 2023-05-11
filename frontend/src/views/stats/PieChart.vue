<template>
    <div id="chart">
        <canvas ref="piechart"></canvas>
    </div>
</template>

<script>
import Chart from 'chart.js'

export default {
    name: 'PieChart',
    data() {
        return {
            fetched: false,
            pieChartData: {
                type: "doughnut",
                data: {
                    labels: [
                        'Completed',
                        'Pending',
                        'Overdue'
                    ],
                    datasets: [{
                        label: 'Overall card breakdown',
                        data: [],
                        backgroundColor: [
                            'rgb(0, 255, 50)',
                            'rgb(255, 150, 0)',
                            'rgb(255, 50, 20)'
                        ],
                        hoverOffset: 4
                    }]
                },
            }
        }
    },
    mounted() {
        fetch(`http://localhost:5000/api/stats/breakdown`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authentication-Token': localStorage.auth_token
            },
            body: JSON.stringify({
                user_id: this.userId,
                list_id: this.listId
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
                this.pieChartData.data.datasets[0].data = [d.completed, d.pending, d.overdue]
                new Chart(this.$refs.piechart, this.pieChartData);
            })
            .catch(e => {
                console.log(e);
            })
    },
    props: {
        userId: Number,
        listId: Number
    }
}
</script>


<style>
#chart {
    width: 100%;
}
</style>