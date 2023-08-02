const canvas = document.getElementById('user_live_chart')
const ctx = canvas.getContext('2d');
let USER_DATA = {};
var CURRENT_OPTION = 'default';
var CURRENT_OPTION_DESCRIPTION = 'Your Investments Performance (1 Day)';
var DATA_LABELS = false;


const plugin = {
    id: 'plugin',
    beforeDraw: (chart, args, options) => {
        const {
            ctx,
            chartArea: {top, bottom, left, right, width, height},
            scales: {x, y }
            } = chart;
        console.log(ctx);
        ctx.save();
        ctx.globalCompositeOperation = 'destination-over';
        ctx.fillStyle = 'rgb(60,60,60)';
        ctx.fillRect(left, top, width, height);
        ctx.restore();
    },
};

const user_live_chart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: init_time,
        datasets:[{
            label: CURRENT_OPTION_DESCRIPTION,
            data: init_val,
            fill: false,
            borderColor: init_color,
            backgroundColor: [init_color],
        }]
    },
    plugins: [plugin,ChartDataLabels],
    options: {
        //onClick: chartOnClick,
        responsive: false,
        interactions: {
            intersect: false,
            mode: 'average'
        },
        layout: {
            padding: 15
        },
        tooltips: {
            mode: 'index',
            inrtersect: false
        },
        hover: {
            mode: 'index',
            intersect: false
        },
        plugins: {
            legend: {
                labels: {
                    font: {
                        size: 25,
                            weight: 'bold'
                    }
                }
            },
            datalabels: {
                color: 'white',
                anchor: (context) => {
                    const anchor_arr = [];
                    if((context.dataIndex%2) == 0){
                        anchor_arr.push('end');
                    }
                    else{
                        anchor_arr.push('start');
                    }
                    return anchor_arr;
                },
                align: (context) => {
                    const align_arr = [];
                    if((context.dataIndex%2) == 0){
                        align_arr.push('end');
                    }
                    else{
                        align_arr.push('start');
                    }
                    return align_arr;
                },
                offset: 5,
                backgroundColor: 'black',
                borderColor: 'blue',
                borderWidth: 1,
                borderRadius: 7,
                formatter: function(value,context){
                    return value.toFixed(2);
                },
                font: {
                    size: 10,
                    weight: 'bold'
                },
                display: DATA_LABELS,
            }
        },
        scales: {
            y: {
                offset: true 
            }
        }
    }
});

function chartOnClick(evt){
    let chart = evt.chart
	// const points = chart.getElementsAtEventForMode(evt, 'nearest', {}, true);

    // console.log(points);
    // points[0].element.$datalabels[0]._config.display = true;
    // if (points.length) {
    //     const firstPoint = points[0];
    //     //var label = myChart.data.labels[firstPoint.index];
    //     //var value = myChart.data.datasets[firstPoint.datasetIndex].data[firstPoint.index];
    //     let datasetIndex = firstPoint.datasetIndex, index = firstPoint.index;
        
    //     if (firstPoint.element.hidden != true) {
    //     	chart.hide(datasetIndex, index);
    //     } else {
    //     	chart.show(datasetIndex, index);
    //     }
    // }
}

function display_data_labels(){
    if(DATA_LABELS == 'auto'){
        DATA_LABELS = 'NOauto';
        user_live_chart.options.plugins.datalabels.display = false;
    }
    else{
        DATA_LABELS = 'auto';
        user_live_chart.options.plugins.datalabels.display = DATA_LABELS;
    }
    user_live_chart.update();
}

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

function check_same_time(time1,time2){
    if(time2 == null){
        return true;
    }
    t1 = time1.split(" ");
    t2 = time2.split(" ");
    return t1[1] === t2[1];
}

function fixed_date(date){ //fixes date 11/7/2022 -> 11/07/2022
    const s_date = date.split("/");
    const nums = ['0','1','2','3','4','5','6','7','8','9'];
    for(var i in nums){
        if(nums[i] == s_date[1]){
            return s_date[0] + "/0" + s_date[1] + "/" + s_date[2];
        }
    }
    return date;
}

function getTime(unixTime){ //gets date and actual time
    var options = {  month: 'short', day: 'numeric' , year: 'numeric', hour: '2-digit',  minute: '2-digit'};
    var dateObject = new Date(unixTime);
    var humanDateFormat = dateObject.toLocaleString("en-US", options);
    const date_time = humanDateFormat.split(",");
    const time = convertTime(date_time[2].substring(1));
    return fixed_date(date_time[0]) + date_time[1] + " " + time;
}

function same_length_lists(lengths,times,values_list){
    var to_return = [];
    var min_length = 10000;
    for(const [key,val] of Object.entries(lengths)){
        if(lengths[key] < min_length){min_length = lengths[key];}
    }
    //console.log('MIN: ' + min_length);
    for(const [key,val] of Object.entries(values_list)){
        var diff = lengths[key] - min_length;
        //console.log('DIFF: ' + diff);
        for(var i = 0; i <= diff; i++){
            values_list[key].shift();
        }
    }
    for(var i = 0; i <= (times.length - min_length); i++){
        times.shift();
    }
    to_return.push(times);//times at position 0
    to_return.push(values_list);//vals at positon 1
    return to_return;
}

async function update_graph_to_option(option){
    if(CURRENT_OPTION == option){return;}
    if(CURRENT_OPTION == "default"){
        option = "a";
    }
    CURRENT_OPTION = option;
    if(asset_name[0] == 'NO ASSETS'){
        return;
    }
    console.log("\nOPTION: " + option + "\n");
    const current_unix_time = Date.now();
    const url_part_one = "https://api.tdameritrade.com/v1/marketdata/"
    var url_part_two = '';

    switch (option){
        case 'a':
            CURRENT_OPTION_DESCRIPTION = 'Your Investments Performance (1 Days)';
            url_part_two = "/pricehistory?frequencyType=minute&frequency=10&periodType=day&period=1"//&endDate="+current_unix_time+"&startDate="+(parseInt(current_unix_time) - 86400000);
            break;
        case 'b':
            CURRENT_OPTION_DESCRIPTION = 'Your Investments Performance (1 Week)';
            url_part_two = "/pricehistory?frequencyType=minute&frequency=30&periodType=day&period=5";
            break;
        case 'c':
            CURRENT_OPTION_DESCRIPTION = 'Your Investments Performance (1 Month)';
            url_part_two = "/pricehistory?frequencyType=daily&frequency=1&periodType=month&period=1";
            break;
        case 'd':
            CURRENT_OPTION_DESCRIPTION = 'Your Investments Performance (3 Months)';
            url_part_two = "/pricehistory?frequencyType=daily&frequency=1&periodType=month&period=3";
            break;
        case 'e':
            CURRENT_OPTION_DESCRIPTION = 'Your Investments Performance (1 Year)';
            url_part_two = "/pricehistory?frequencyType=weekly&frequency=1&periodType=year&period=1";
            break;
        case 'f':
            CURRENT_OPTION_DESCRIPTION = 'Your Investments Performance (5 Years)';
            url_part_two = "/pricehistory?frequencyType=monthly&frequency=1&periodType=year&period=5";
            break;
    }

    var list_of_val = {};
    var lengths = {};
    var times = [];
    for(var ticker in asset_name){
        const url = url_part_one+asset_name[ticker]+url_part_two;
        const config = {headers:{'Authorization' : 'Bearer ' + user_access_token}};
        const response = await fetch(url,config);
        var data = await response.json();
        var time_val = data['candles'];
        var temp_val = [];
        for(var i in time_val){
            if(ticker == 0){times.push(getTime(time_val[i]['datetime']));}
            temp_val.push(((time_val[i]['close'])*quantity[ticker]));
        }
        list_of_val[asset_name[ticker]] = temp_val;
        lengths[asset_name[ticker]] = parseInt(time_val.length);
    };
    console.log(lengths);

    var values_time_table = same_length_lists(lengths,times,list_of_val);
    console.log(values_time_table);
    let df = new dfd.DataFrame(values_time_table[1]);
    let sum_vals = df.sum();
    let fixed_sum_vals = sum_vals['$data'];
    for(i in fixed_sum_vals){
        fixed_sum_vals[i] = fixed_sum_vals[i];
    }
    user_live_chart.data.labels = values_time_table[0];
    user_live_chart.data.datasets[0].data = fixed_sum_vals;

    if (sum_vals.tail(1)['$data'][0] >= iv){
        user_live_chart.data.datasets[0].borderColor= 'rgb(0, 255, 0)';
        user_live_chart.data.datasets[0].backgroundColor.shift();
        user_live_chart.data.datasets[0].backgroundColor.push('rgb(0, 255, 0)');}
    else{
        user_live_chart.data.datasets[0].borderColor= 'rgb(255, 0, 0)';
        user_live_chart.data.datasets[0].backgroundColor.shift();
        user_live_chart.data.datasets[0].backgroundColor.push('rgb(255, 0, 0)');}
     
    user_live_chart.data.datasets[0].label = CURRENT_OPTION_DESCRIPTION;
    user_live_chart.update();
}

async function getapi() { //makes call to api for stock info
    const current_unix_time = Date.now();
    const unix_time_a_day_ago = parseInt(current_unix_time) - 86400000;
    for(var ticker in asset_name){
        const url = "https://api.tdameritrade.com/v1/marketdata/"+asset_name[ticker]+"/pricehistory?frequencyType=minute&frequency=5&endDate="+current_unix_time+"&startDate="+unix_time_a_day_ago;
        const config = {headers:{'Authorization' : 'Bearer ' + user_access_token}};
        const response = await fetch(url,config);
        var data = await response.json();
        let latest_data = parseInt(data['candles']['length']) - 1;
        if(ticker == 0){
            USER_DATA['length'] = latest_data + 1;
            USER_DATA['time'] = getTime(parseInt(data['candles'][latest_data]['datetime']));
            USER_DATA['value'] = parseInt(data['candles'][latest_data]['close'])*quantity[ticker];
        }
        else{
            USER_DATA['value'] += parseInt(data['candles'][latest_data]['close'])*quantity[ticker];
        }
    };
}

function updateChart(){ //updates user_live_chart
    if(asset_name[0] != 'NO ASSETS' && CURRENT_OPTION == 'a'){
        getapi();
        const chart_labels = user_live_chart.data.labels;
        const chart_data = user_live_chart.data.datasets[0].data;
        var latest_time = chart_labels[chart_labels.length - 1];
        if (check_same_time(latest_time, USER_DATA['time']) == false){
            chart_labels.push(USER_DATA['time']);
            chart_data.push(USER_DATA['value']);

            if (USER_DATA['value'] >= iv){
                user_live_chart.data.datasets[0].borderColor= 'rgb(0, 255, 0)';
                user_live_chart.data.datasets[0].backgroundColor.shift();
                user_live_chart.data.datasets[0].backgroundColor.push('rgb(0, 255, 0)');}
            else{
                user_live_chart.data.datasets[0].borderColor= 'rgb(255, 0, 0)';
                user_live_chart.data.datasets[0].backgroundColor.shift();
                user_live_chart.data.datasets[0].backgroundColor.push('rgb(255, 0, 0)');}

            user_live_chart.update();

            if(chart_labels.length > 160){
                chart_data.shift();
                chart_labels.shift();
                user_live_chart.update();
            }
        }
    }
    else {return;}
}

setInterval(() => { //updates user_live_chart every 5 minutes
    updateChart();
}, 5*60000);
