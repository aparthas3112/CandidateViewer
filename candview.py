#!/usr/bin/env python

"""
Code to view Heimdall candidates given a UTC
"""

import argparse


#BOKEH imports
from bokeh.plotting import figure, output_file, show, Figure
from bokeh.layouts import widgetbox
from bokeh.models.widgets import CheckboxButtonGroup, Slider, Select, TextInput, Panel, Tabs, PreText, Button, TextInput, RangeSlider, DataTable, TableColumn, CheckboxGroup, Toggle, Dropdown
from bokeh.layouts import layout,column,row
from bokeh.models import CustomJS, ColumnDataSource, HoverTool, Div, LabelSet, BoxAnnotation, LogColorMapper
from bokeh.io import curdoc
from bokeh.models import CustomJS, TextInput, Paragraph


#Argument parser
parser = argparse.ArgumentParser(description="Candidate viewer for Heimdall")
parser.add_argument("-cfile", dest="config", help="Configuration file for the candidate viewer", required=True)
args=parser.parse_args()

#Parsing the configuration file
configfile = open(str(args.config),"r")
for line in configfile.readlines():
    attr = line.split("=")[0].rstrip()
    if attr == "params":
        params=[]
        for param in line.split("=")[1].rstrip().lstrip(' ').split(' '):
            params.append(param)
    if attr == "data_path":
        data_path = line.split("=")[1].rstrip().lstrip(' ')


#Defining the column data sources for the candidate viewer

heimdall_source = ColumnDataSource(data=dict(x=[],y=[]))
sigproc_source = ColumnDataSource(data=dict(image1=[],image2=[],image3=[])) #This will change depending upon the input from sigproc


##################### Creating the interface for the candidate viewer #####################

#UTC input text box
utc_input = TextInput(value="Enter UTC here", title="UTC (YYYY/MM/DD HH:SS:SS)")

#Candidate viewer plot
x_axis = Select(title="X-axis", options=sorted(params),value="snr")
y_axis = Select(title="Y-axis", options=sorted(params), value="dm")

candview = figure(plot_height=600, plot_width=800, title="Candidate Viewer")
candview_plot = candview.circle(x='x',y='y', source=heimdall_source, size=4)

#Create range sliders for filtering the candidates in the candview plot - (can add more eventually)
snr_range = RangeSlider(title="SNR", start=0,end=10,value=(0,10),step=1)
dm_range = RangeSlider(title="DM", start=0,end=10,value=(0,10),step=1)

sigproc1 = figure(plot_height=400,plot_width=400, title="Dispersed plot")
sigproc2 = figure(plot_height=400,plot_width=400, title="De-dispersed plot")
sigproc3 = figure(plot_height=400,plot_width=400, title="Convolved plot")
dispersed_plot = sigproc1.image(image='image1', x=0, y=0, dw=10, dh=10, palette="Spectral11",source=sigproc_source) #This will also change depending on sigproc 2-d array
dedispersed_plot = sigproc2.image(image='image2', x=0, y=0, dw=10, dh=10, palette="Spectral11",source=sigproc_source) #This will also change depending on sigproc 2-d array
convolved_plot = sigproc3.image(image='image3', x=0, y=0, dw=10, dh=10, palette="Spectral11",source=sigproc_source) #This will also change depending on sigproc 2-d array

#Copyrights information
copyright = PreText(text=" (C) 2018 Aditya Parthasarathy and Wael Farah", width=700)


################### Callback routines ##################
"""
def filterdata():
    data = df[
            (df.snr >= snr_range.value[0]) &
            (df.snr <= snr_range.value[1]) &
            (df.dm >= dm_range.value[0]) &
            (df.dm <= dm_range.value[1])
            ]
    return data
"""
def update_candview():
    #filtered_data = filterdata()
    heimdall_source.data = dict(x=[], y=[])
    candview.xaxis.axis_label = x_axis.value
    candview.yaxis.axis_label = y_axis.value


############### Defining widgets and layout for the interface ############
controls = [x_axis,y_axis]
for control in controls:
    control.on_change('value', lambda attr, old, new: update_candview())
param_inputs = widgetbox(*controls, sizing_mode='fixed')

range_sliders = [snr_range,dm_range]
for slider in range_sliders:
    slider.on_change('value', lambda attr,old,new: update_candview())
slider_inputs = widgetbox(*range_sliders, sizing_mode='fixed')

inputs = column([param_inputs,slider_inputs])

layout = layout([utc_input],
                [inputs,candview],
                [sigproc1,sigproc2,sigproc3],
                [copyright],sizing_mode='fixed')

update_candview()
curdoc().add_root(layout)

