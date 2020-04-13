var categories= echarts.init(document.getElementById("ct1"))
ca_option = {
    title: {
        text: '某站点用户访问来源',
        subtext: '纯属虚构',
        left: 'center'
    },
    tooltip: {
        trigger: 'item',
        formatter: '{a} <br/>{b} : {c} ({d}%)'
    },
    legend: {
        orient: 'vertical',
        left: 'left',
        data: ['Confections', 'Shell fish', 'Cereals', 'Dairy', 'Beverages',  'Seafood',  'Meat', 'Poultry', 'Grain', 'Snails', 'Produce']
    },
    series: [
        {
            name: '访问来源',
            type: 'pie',
            radius: '55%',
            center: ['50%', '60%'],
            data: [
                {value: 335, name: 'Confections'},
                {value: 310, name: 'Shell fish'},
                {value: 234, name: 'Cereals'},
                {value: 135, name: 'Dairy'},
                {value: 154, name: 'Beverages'},
                {value: 335, name: 'Seafood'},
                {value: 310, name: 'Meat'},
                {value: 234, name: 'Poultry'},
                {value: 135, name: 'Grain'},
                {value: 154, name: 'Snails'},
                {value: 154, name: 'Produce'},
            ],
            emphasis: {
                itemStyle: {
                    shadowBlur: 10,
                    shadowOffsetX: 0,
                    shadowColor: 'rgba(0, 0, 0, 0.5)'
                }
            }
        }
    ]
}; categories.setOption(ca_option);