from app import app
from bokeh.embed import components
from bokeh.models import ColumnDataSource, HoverTool, NumeralTickFormatter
from bokeh.plotting import figure, show

def formatter(val, type='number'):
    if 10**3 < val < 10**6:
        val = str(round(val / 10**3, 3)) + ' Thousand'
    elif 10**6 < val < 10**9:
        val = str(round(val / 10**6, 3)) + ' Million'
    elif 10**9 < val < 10**12:
        val = str(round(val / 10**9, 3)) + ' Billion'
    elif val >= 10**12:
        val = str(round(val / 10**12, 3)) + ' Trillion'
    return '$ ' + val if type == 'dollar' else val

def vbar(data, x, y, y_type):
    x_range = data.loc[:, x]
    data_source = ColumnDataSource(data)
    # print(x_range)
    formats = '{$ 0.00 a}' if y_type == 'dollar' else '{0.00 a}'
    data_hover = HoverTool(tooltips=[(x.capitalize(), '@'+x), (y.capitalize(), '@'+y+formats)])
    data_fig = figure(x_range = x_range, sizing_mode='scale_width', height=300, tools=[data_hover], 
        toolbar_location=None)
    # styling visual
    data_fig.vbar(x=x, top=y, source=data_source, width=0.9, hover_color='red', hover_fill_alpha=0.8)
    data_fig.xaxis.axis_label = x.capitalize()
    data_fig.xaxis.axis_label_text_font_size = "12pt"
    data_fig.xaxis.axis_label_standoff = 10
    data_fig.yaxis.axis_label = y.capitalize()
    data_fig.yaxis.axis_label_text_font_size = "12pt"
    data_fig.yaxis.axis_label_standoff = 10
    data_fig.xaxis.major_label_text_font_size = '10pt'
    data_fig.yaxis.major_label_text_font_size = '11pt'
    data_fig.yaxis[0].formatter = NumeralTickFormatter(format=formats)
    data_js, data_div = components(data_fig)
    print(data_div)
    print(data_js)
    return data_js, data_div