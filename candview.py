#!/usr/bin/env python

"""
Code to view Heimdall candidates given a UTC
"""

import argparse
import os,sys
from utils import parse_cfg,parse_all_candidates


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
config = parse_cfg(str(args.config))
params = config['params']
data_path = config['data_path']

#Defining the column data sources for the candidate viewer

heimdall_source = ColumnDataSource(data=dict(x=[],y=[]))
sigproc_source = ColumnDataSource(data=dict(image1=[],image2=[],image3=[])) #This will change depending upon the input from sigproc


##################### Creating the interface for the candidate viewer #####################

#UTC input text box
utc_input = TextInput(value="Enter UTC here", title="UTC (YYYY/MM/DD HH:SS:SS)")
SAMPLE_UTC = "2018-04-08-11:08:23"

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
def filterdata():
    data = df[
            (df.snr >= snr_range.value[0]) &
            (df.snr <= snr_range.value[1]) &
            (df.dm >= dm_range.value[0]) &
            (df.dm <= dm_range.value[1])
            ]
    return data

def update_candview():
    #filtered_data = filterdata()
    if all_candidates is not None:
        heimdall_source.data = dict(x=all_candidates[x_axis.value],
                y=all_candidates[y_axis.value])
    candview.xaxis.axis_label = x_axis.value
    candview.yaxis.axis_label = y_axis.value

def update_candfile():
    global all_candidates
    utc = utc_input.value
    all_candidates_path = os.path.join(data_path,utc,"all_candidates.dat")
    if not os.path.exists(all_candidates_path):
        sys.stderr.write("<%s> doesn't exist\n" %all_candidates_path)
        all_candidates = None
        heimdall_source.data = dict(x=[], y=[])
    else:
        all_candidates = parse_all_candidates(all_candidates_path,
                header=params)
        x_axis.value = "snr" # Reset to default
        y_axis.value = "dm" #Reset to default
        update_candview()


############### Defining widgets and layout for the interface ############
controls = [x_axis,y_axis]
for control in controls:
    control.on_change('value', lambda attr, old, new: update_candview())
utc_input.on_change('value', lambda attr, old, new: update_candfile())
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

all_candidates = None
update_candview()
curdoc().add_root(layout)

