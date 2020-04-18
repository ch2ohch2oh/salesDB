
function get_revenue_by_category2() {
    $.ajax({
        url:"/ct1",
        success: function(data) {
       ca_option.series.data=data.data
            categories.setOption(ca_option)
		},
		error: function(xhr, type, errorThrown) {

		}
    })
}

get_revenue_by_category2()

