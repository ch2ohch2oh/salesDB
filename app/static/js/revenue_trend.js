var ren_trend = echarts.init(document.getElementById("rt1"))
	data = [["2018-06-05",10],["2018-06-06",129],["2018-06-07",135],["2018-06-08",86],["2018-06-09",73],["2018-06-10",85],["2018-06-11",73],["2018-06-12",68],["2018-06-13",92],["2018-06-14",130],["2018-06-15",245],["2018-06-16",139],["2018-06-17",115],["2018-06-18",111],["2018-06-19",309],["2018-06-20",206],["2018-06-21",137],["2018-06-22",128],["2018-06-23",85],["2018-06-24",94],["2018-06-25",71],["2018-06-26",106],["2018-06-27",84],["2018-06-28",93],["2018-06-29",85],["2018-06-30",73],["2018-07-01",83],["2018-07-02",125],["2018-07-03",107],["2018-07-04",82],["2018-07-05",44],["2018-07-06",72],["2018-07-07",106],["2018-07-08",107],["2018-07-09",66],["2018-07-10",91],["2018-07-11",92],["2018-07-12",113],["2018-07-13",107],["2018-07-14",131],["2018-07-15",111],["2018-07-16",64],["2018-07-17",69],["2018-07-18",88]];
    <!--  change data with js   -->
        var dateList = data.map(function (item) {
        return item[0];
        });
        var valueList = data.map(function (item) {
       return item[1];
       });

   ren_trend_option = {
    // Make gradient line here
    visualMap: [{
        show: false,
        type: 'continuous',
        seriesIndex: 0,
        min: 0,
        max: 400
    },{
        show: false,
        type: 'continuous',
        seriesIndex: 1,
        dimension: 0,
        min: 0,
        max: dateList.length - 1
    }],

    title: [{
        left: 2,
        text: 'revenue trend'
    }],
    tooltip: {
        trigger: 'axis'
    },
    xAxis: [{
        data: dateList
    }],
    yAxis: [{
        splitLine: {show: false}
    }],
    grid: [{
        bottom: '60%'
    }, {
        top: '60%'
    }],
    series: [{
        type: 'line',
        showSymbol: false,
        data: valueList
    }, ]
};  ren_trend.setOption(ren_trend_option);