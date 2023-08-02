const cvas = document.getElementById('my_pie_chart')
const ctz = cvas.getContext('2d');
const DATA_COUNT = asset_name.length;

const my_pie_chart = new Chart(ctz, {
    type: 'pie',
    data: {
labels: asset_name,
datasets: [{
label: 'Stock Investments',
   data: percentage_of_assets,
   backgroundColor:["#483D8B", "#6A5ACD", "#191970", "#00008B", "#0000CD", "#4169E1", "#4682B4", "#6495ED", "#1E90FF", "#01FF70", "#00BFFF", "#87CEEB", "#87CEFA", "#B0E0E6", "#000080", "#E0FFFF", "#00CED1", "#008080"]
}]
    },
    options: {
        responsive: false,
        radius: 200,
        interactions: {
            intersect: false,
            mode: 'average'
        },
        title: {
        display: true,
        text: 'Positions'
        },
        animation: {
        animateScale: true
        },
        plugins: {
        legend: {
        labels: {
        font: {
        size: 20,
        family: 'Helvetica Neue'
        }
        }
        },
        datalabels: {
        color: 'black',
        labels: {
        title: {
        font: {
        weight: 'bold',
        size: 30,
        family: 'Helvetica Neue'
        }
        }
        },
        formatter: function(value, context) {
          return value + '%';
          }
        }
        }
    },
    plugins: [ChartDataLabels]
});
