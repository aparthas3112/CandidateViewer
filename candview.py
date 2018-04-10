#!/usr/bin/env python

"""
Code to view Heimdall candidates given a UTC
"""

import argparse
import os,sys
from utils import parse_cfg,get_all_candidates

# Add sigpyproc to sys.path:
SIGPYPROC = "/home/ebarr/Soft/sigpyproc"
if SIGPYPROC not in sys.path:
    sys.path.append(SIGPYPROC)

try:
    from sigpyproc.Readers import FilReader
except ImportError as e:
    sys.stderr.write("Could not import sigpyproc, exiting...\n")
    sys.exit(-1)

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
cands_path = config['cands_path']
data_path = config['data_path']

#Defining the column data sources for the candidate viewer

heimdall_source = ColumnDataSource(data=dict(x=[],y=[]))
sigproc_source = ColumnDataSource(data=dict(disp=[],dedisp=[],conv=[])) #This will change depending upon the input from sigproc


##################### Creating the interface for the candidate viewer #####################

#UTC input text box
utc_input = TextInput(value="Enter UTC here", title="UTC (YYYY-MM-DD-HH:SS:SS)")
SAMPLE_UTC = "2018-04-08-11:08:23"

# Error text box
errbox = Div(text="",width=800)
errtext = open(os.path.join(os.path.dirname(__file__), "errbox.html")).read()

#Candidate viewer plot
x_axis = Select(title="X-axis", options=sorted(params),value="snr")
y_axis = Select(title="Y-axis", options=sorted(params), value="dm")

candview = figure(plot_height=600, plot_width=800, title="Candidate Viewer", 
        tools=['tap','pan','wheel_zoom','reset'])
candview_plot = candview.circle(x='x',y='y', source=heimdall_source, size=6)

#Create range sliders for filtering the candidates in the candview plot - (can add more eventually)
snr_range = RangeSlider(title="SNR", start=0,end=10,value=(0,10),step=1)
dm_range = RangeSlider(title="DM", start=0,end=10,value=(0,10),step=1)

sigproc_disp = figure(plot_height=400,plot_width=400, 
        x_range=(0,10), y_range=(0,10), title="Dispersed dynamic spectrum")
sigproc_dd = figure(plot_height=400,plot_width=400, 
        x_range=(0,10), y_range=(0,10), title="De-dispersed dynamic spectrum")
sigproc_conv = figure(plot_height=400,plot_width=400, 
        x_range=(0,10), y_range=(0,10), title="Convolved dynamic spectrum")
dispersed_plot = sigproc_disp.image(image='disp', x=0, y=0, dw=10, dh=10, palette="Spectral11",source=sigproc_source) #This will also change depending on sigproc 2-d array
dedispersed_plot = sigproc_dd.image(image='dedisp', x=0, y=0, dw=10, dh=10, palette="Spectral11",source=sigproc_source) #This will also change depending on sigproc 2-d array
convolved_plot = sigproc_conv.image(image='conv', x=0, y=0, dw=10, dh=10, palette="Spectral11",source=sigproc_source) #This will also change depending on sigproc 2-d array

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
    all_candidates_path = os.path.join(cands_path,utc,"all_candidates.dat")
    if not os.path.exists(all_candidates_path):
        errbox.text = errtext
        sys.stderr.write("<%s> doesn't exist\n" %all_candidates_path)
        all_candidates = None
        heimdall_source.data = dict(x=[], y=[])
    else:
        errbox.text = ""
        all_candidates = get_all_candidates(all_candidates_path,
                header=params)
        x_axis.value = "snr" # Reset to default
        y_axis.value = "dm" #Reset to default
        update_candview()

def reset_dynamic_spectra():
    sys.stderr.write("Resetting\n")
    sigproc_source.data = dict(disp=[],dedisp=[],conv=[])


def plot_sigproc(cand):
    utc = utc_input.value
    beam_str = str(int(cand['beam'])).zfill(2)
    fil_path = os.path.join(data_path,utc,beam_str,utc+".fil")
    sys.stderr.write("%s\n" %fil_path)
    fil = FilReader(fil_path)
    disp = fil.readBlock(int(cand['sample']), 5000)
    dedisp = disp.dedisperse(cand['dm'])
    sigproc_source.data = dict(disp=[disp], dedisp=[dedisp], conv=[dedisp])


def tap_callback(attr, old, new):
    idx = new[u'1d']['indices']
    if idx and all_candidates is not None:
        assert len(idx) == 1
        idx = idx[0]
        cand = all_candidates.iloc[idx]
        plot_sigproc(cand)
        sys.stderr.write("%s\n" %cand)
    else:
        reset_dynamic_spectra()

    #sys.stderr.write("%s %i\n%s\n%s\n\n" %(attr,idx,old,new))

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

layout = layout([utc_input,errbox],
                [inputs,candview],
                [sigproc_disp,sigproc_dd,sigproc_conv],
                [copyright],sizing_mode='fixed')

candview_plot.data_source.on_change('selected', tap_callback)
        #lambda attr,old,new: sys.stderr.write("%s %s %s\n" %(attr,old,new)))
all_candidates = None
update_candview()
curdoc().add_root(layout)
