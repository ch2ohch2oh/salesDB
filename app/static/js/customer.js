var myChart = echarts.init(document.getElementById('map'));

// Specify configurations and data graphs
myChart.showLoading();

$.get('https://s3-us-west-2.amazonaws.com/s.cdpn.io/95368/USA_geo.json', function (usaJson) {
    myChart.hideLoading();

    echarts.registerMap('USA', usaJson, {
        Alaska: {              // 把阿拉斯加移到美国主大陆左下方
            left: -131,
            top: 25,
            width: 15
        },
        Hawaii: {
            left: -110,        //夏威夷
            top: 28,
            width: 5
        },
        'Puerto Rico': {       //波多黎各
            left: -76,
            top: 26,
            width: 2
        }
    });
    map_option = {
        title: {
            text: 'Customer location estimates',
            left: 'left'
        },
        tooltip: {
            trigger: 'item',
            showDelay: 0,
            transitionDuration: 0.2,
            formatter: function (params) {
                var value = (params.value + '').split('.');
                value = value[0].replace(/(\d{1,3})(?=(?:\d{3})+(?!\d))/g, '$1,');
                return params.seriesName + '<br/>' + params.name + ' : ' + value;
            }
        },
        visualMap: {
            left: 'right',
            min: 0,
            max: 10000,
            color: ['orangered', 'yellow', 'lightskyblue'],
            text: ['High', 'Low'],
            calculable: true
        },
        toolbox: {
            show: true,
            //orient : 'vertical',
            left: 'right',
            top: 'top',
            feature: {
                mark: { show: true },
                dataView: { show: true, readOnly: false },  //前台可改变数据
                restore: { show: true },
                saveAsImage: { show: true }
            }
        },
        series: [
            {
                name: 'Customer Estimates',
                type: 'map',
                roam: true,
                map: 'USA',
                itemStyle: {
                    emphasis: { label: { show: true } }
                },

                textFixed: {
                    Alaska: [20, -20]
                },
                data: [] //传入数据
            }
        ]
    };

    myChart.setOption(map_option);
});

$.ajax({
    url: "/map",
    success: function (data) {
        map_option.series[0].data = data.data
        myChart.setOption(map_option)
    },
    error: function (xhr, type, errorThrown) {
    }
})