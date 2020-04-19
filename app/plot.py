from app import app
from bokeh.embed import components
from bokeh.models import ColumnDataSource, HoverTool, NumeralTickFormatter, Legend
from bokeh.plotting import figure, show
from bokeh.palettes import brewer

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

def line(data, x, y, y_type='number'):
    x_range = data.loc[:, x]
    data_source = ColumnDataSource(data)
    # print(x_range)
    formats = '$ 0.00 a' if y_type == 'dollar' else '0.00 a'
    if x == 'date':
        data_hover = HoverTool(tooltips=[('Date', '@date{%F}'), (y.replace("_", " ").title(), '@'+y+'{'+formats+'}')], 
            formatters={'@date': 'datetime'})
        data_fig = figure(x_axis_type='datetime', sizing_mode='scale_width', height=300, tools=[data_hover], 
            toolbar_location=None)
    else:
        data_hover = HoverTool(tooltips=[(x.replace("_", " ").title(), '@'+x), (y.replace("_", " ").title(), '@'+y+'{'+formats+'}')])
        data_fig = figure(x_range = x_range, sizing_mode='scale_width', height=300, tools=[data_hover], 
            toolbar_location=None)
    # styling visual
    data_fig.line(x=x, y=y, source=data_source, line_width=2)
    data_fig.xaxis.axis_label = x.replace("_", " ").title()
    data_fig.xaxis.axis_label_text_font_size = "12pt"
    data_fig.xaxis.axis_label_standoff = 10
    data_fig.yaxis.axis_label = y.replace("_", " ").title()
    data_fig.yaxis.axis_label_text_font_size = "12pt"
    data_fig.yaxis.axis_label_standoff = 10
    data_fig.xaxis.major_label_text_font_size = '10pt'
    data_fig.yaxis.major_label_text_font_size = '11pt'
    data_fig.yaxis[0].formatter = NumeralTickFormatter(format=formats)
    return components(data_fig)

def vbar(data, x, y, y_type='number'):
    x_range = data.loc[:, x]
    data_source = ColumnDataSource(data)
    # print(x_range)
    formats = '$ 0.00 a' if y_type == 'dollar' else '0.00 a'
    data_hover = HoverTool(tooltips=[(x.replace("_", " ").title(), '@'+x), (y.replace("_", " ").title(), '@'+y+'{'+formats+'}')])
    data_fig = figure(x_range = x_range, sizing_mode='scale_width', height=300, tools=[data_hover], 
        toolbar_location=None)
    # plot
    data_fig.vbar(x=x, top=y, source=data_source, width=0.9, hover_color='red', hover_fill_alpha=0.8)
    # styling visual
    data_fig.xaxis.axis_label = x.replace("_", " ").title()
    data_fig.xaxis.axis_label_text_font_size = "12pt"
    data_fig.xaxis.axis_label_standoff = 10
    data_fig.yaxis.axis_label = y.replace("_", " ").title()
    data_fig.yaxis.axis_label_text_font_size = "12pt"
    data_fig.yaxis.axis_label_standoff = 10
    data_fig.xaxis.major_label_text_font_size = '10pt'
    data_fig.yaxis.major_label_text_font_size = '11pt'
    data_fig.yaxis[0].formatter = NumeralTickFormatter(format=formats)
    return components(data_fig)

def hbar(data, x, y, x_type='number'):
    y_range = data.loc[:, y]
    x_data = data.loc[:, x]
    x_range = (x_data.min() - (x_data.max()-x_data.min())/10, x_data.max())
    data_source = ColumnDataSource(data)
    formats = '$ 0.00 a' if x_type == 'dollar' else '0.00 a'
    data_hover = HoverTool(tooltips=[(y.replace("_", " ").title(), '@'+y), (x.replace("_", " ").title(), '@'+x+'{'+formats+'}')])
    data_fig = figure(y_range=y_range, x_range=x_range, sizing_mode='scale_width', height=300, tools=[data_hover], 
        toolbar_location=None)
    # plot
    data_fig.hbar(y=y, right=x, source=data_source, height=0.8, hover_color='red', hover_fill_alpha=0.8)
    # styling visual
    data_fig.xaxis.axis_label = x.replace("_", " ").title()
    data_fig.xaxis.axis_label_text_font_size = "12pt"
    data_fig.xaxis.axis_label_standoff = 10
    data_fig.yaxis.axis_label = y.replace("_", " ").title()
    data_fig.yaxis.axis_label_text_font_size = "12pt"
    data_fig.yaxis.axis_label_standoff = 10
    data_fig.xaxis.major_label_text_font_size = '10pt'
    data_fig.yaxis.major_label_text_font_size = '11pt'
    data_fig.xaxis[0].formatter = NumeralTickFormatter(format=formats)
    return components(data_fig)

def multiline(data, x, y, y_type='number', *args):
    x_range = data.loc[:, x]
    data_source = ColumnDataSource(data)
    formats = '$ 0.00 a' if y_type == 'dollar' else '0.00 a'
    # plot
    color = brewer['Paired'][len(args)]
    i = 0
    legend_item = []
    if x == 'date':
        data_fig = figure(x_axis_type='datetime', sizing_mode='scale_width', height=300, toolbar_location=None)
        for i in range(len(args)):
            plot = data_fig.line(x=x, y=args[i].replace(" ", "_"), line_color=color[i], line_width=5, source=data_source)
            # args is name containing space, thus need to replace space to underscore to match dataframe column
            data_fig.add_tools(HoverTool(renderers=[plot], tooltips=[('Date', '@date{%F}'), (args[i].title(), '@'+args[i].replace(" ", "_")+'{'+formats+'}')],
                formatters={'@date': 'datetime'}, mode='mouse'))
            legend_item.append((args[i], [plot]))
            i += 1
    else:
        data_fig = figure(x_range = x_range, sizing_mode='scale_width', height=300, toolbar_location=None)
        for i in range(len(args)):
            plot = data_fig.line(x=x, y=args[i].replace(" ", "_"), line_color=color[i], line_width=5, source=data_source)
            data_fig.add_tools(HoverTool(renderers=[plot], tooltips=[(x.replace("_", " ").title(), '@'+x), (args[i].title(), '@'+args[i].replace(" ", "_")+'{'+formats+'}')],
                mode='mouse'))
            legend_item.append((args[i], [plot]))
            i += 1
    # styling visual
    legend = Legend(items=legend_item, location='center', click_policy='hide')
    data_fig.add_layout(legend, 'right')
    data_fig.xaxis.axis_label = x.replace("_", " ").title()
    data_fig.xaxis.axis_label_text_font_size = "12pt"
    data_fig.xaxis.axis_label_standoff = 10
    data_fig.yaxis.axis_label = y.replace("_", " ").title()
    data_fig.yaxis.axis_label_text_font_size = "12pt"
    data_fig.yaxis.axis_label_standoff = 10
    data_fig.xaxis.major_label_text_font_size = '10pt'
    data_fig.yaxis.major_label_text_font_size = '11pt'
    data_fig.yaxis[0].formatter = NumeralTickFormatter(format=formats)
    return components(data_fig)

def vbar_stack(data, x, y, y_type='number', color=["#da3337", "#4986ec"], alpha=0.8, *args):
    x_range = data.loc[:, x]
    data_source = ColumnDataSource(data)
    formats = '$ 0.00 a' if y_type == 'dollar' else '0.00 a'
    data_fig = figure(x_range = x_range, sizing_mode='scale_width', height=300, tools='hover', 
        tooltips='$name: @$name{0.00 a}', toolbar_location=None)
    # plot
    plot = data_fig.vbar_stack(args, x=x, source=data_source, width=0.9, alpha=alpha, color=color)
    # styling visual
    legend_item =[]
    for i in range(len(args)):
        legend_item.append((args[i], [plot[i]]))
    legend = Legend(items=legend_item, location='center')
    data_fig.add_layout(legend, 'right')
    data_fig.xaxis.axis_label = x.replace("_", " ").title()
    data_fig.xaxis.axis_label_text_font_size = "12pt"
    data_fig.xaxis.axis_label_standoff = 10
    data_fig.yaxis.axis_label = y.replace("_", " ").title()
    data_fig.yaxis.axis_label_text_font_size = "12pt"
    data_fig.yaxis.axis_label_standoff = 10
    data_fig.xaxis.major_label_text_font_size = '10pt'
    data_fig.yaxis.major_label_text_font_size = '11pt'
    data_fig.yaxis[0].formatter = NumeralTickFormatter(format=formats)
    return components(data_fig)