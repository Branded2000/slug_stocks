var ctx = document.getElementById('chart').getContext('2d');
ctx.canvas.width = 1200;
ctx.canvas.height = 400;

const barData = {};

var chart = new Chart(ctx, {
    type: 'candlestick',
    data: {
        datasets: [{
            label: symbol + " (1 day)",
            data: barData
        }]
    },
    options: {
        responsive: false
    }

});

get_data();

const convertTime = timeStr => { //transform 12hr to 24hr
    const [time, modifier] = timeStr.split(' ');
    let [hours, minutes] = time.split(':');
    if (hours === '12') {
       hours = '00';
    }
    if (modifier === 'PM') {
       hours = parseInt(hours, 10) + 12;
    }
    return `${hours}:${minutes}`;
 };

function getTime(unixTime){ //gets date and actual time
    var options = { day: '2-digit', month: 'short' , year: 'numeric', hour: '2-digit',  minute: '2-digit'};
    var dateObject = new Date(unixTime);
    var humanDateFormat = dateObject.toLocaleString("en-US", options);
    const date_time = humanDateFormat.split(",");
    const time = convertTime(date_time[2].substring(1));
    const day_month = date_time[0].split(" ");
    return ( day_month[1] + " " + day_month[0] + date_time[1] + " " + time + " " + "PST");
}

async function get_data(){
    const url = "https://api.tdameritrade.com/v1/marketdata/"+symbol+"/pricehistory?frequencyType=minute&frequency=10&periodType=day&period=1";
    const config = {headers:{'Authorization' : 'Bearer ' + user_access_token}};
    const response = await fetch(url,config);
    var data = await response.json();
    var candles = data['candles'];
    var all_data = [];
    for(i in candles){
        all_data.push({
            x: luxon.DateTime.fromRFC2822(getTime(candles[i]['datetime'])).valueOf(),
            o: candles[i]['open'],
            h: candles[i]['high'],
            l: candles[i]['low'],
            c: candles[i]['close'],
        });
    }
    chart.data.datasets[0].data = all_data;
    chart.update();
}