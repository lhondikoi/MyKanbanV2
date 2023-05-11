<template>
    <div id="chart">
        <canvas ref="linechart"></canvas>
    </div>
</template>

<script>
import Chart from 'chart.js'

export default {
    name: 'LineChart',
    data() {
        return {
            fetched: false,
            lineChartData: {
                type: "line",
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Cards completed per day',
                        data: [],
                        fill: false,
                        borderColor: 'rgb(75, 192, 192)',
                        tension: 0.5
                    }]
                },
            }
        }
    },
    mounted() {
        let end_date = new Date()
        let start_date = new Date()
        start_date.setDate(start_date.getDate() - 7)
        console.log(start_date.toISOString().split('T')[0], end_date.toISOString().split('T')[0])
        fetch(`http://localhost:5000/api/stats/timeline`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authentication-Token': localStorage.auth_token
            },
            body: JSON.stringify({
                user_id: this.userId,
                start_date: start_date.toISOString().split('T')[0],
                end_date: end_date.toISOString().split('T')[0]
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
                console.log(d)
                this.lineChartData.data.labels = d.dates
                this.lineChartData.data.datasets[0].data = d.completed
                new Chart(this.$refs.linechart, this.lineChartData);
            })
            .catch(e => {
                console.log(e);
            })
    },
    props: {
        userId: Number
    }
}
</script>


<style>
#chart {
    width: 100%;
}
</style>