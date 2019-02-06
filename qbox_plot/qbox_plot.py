"""
    File name: qbx_plot.py
    version: 1.0.0 (16 jan 2019)
    Author: Copyright (C) 2019 - Nico Vermaas (nvermaas@xs4all.nl)
    Date created: 2019-01-13
    Description: Plot converted QboxNext datafiles.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import os
import sys
import datetime

import plotly
import requests

import argparse
import plotly.graph_objs as go
#import numpy as np


TIME_FORMAT = "%Y-%m-%d %H:%M"

#--- common functions ---
def weeknumber_to_date(starttime, week):
    """
    Convert weeknumber to a human readable date
    :param week: week number, 1..53
    :return: date as string like '7 jan'
    """

    search_pattern = str(starttime.year)+'-W'+str(week)
    timestamp = datetime.datetime.strptime(search_pattern + '-0', "%Y-W%W-%w").date()
    date = datetime.datetime.strftime(timestamp, "%d %b")
    return date

def find_last_in_list(list, value):
    pos = max(loc for loc, val in enumerate(list) if val == value)
    return pos


def scp_filename(host, source, target):
    """ scp a file from a remote location to a local dir
        location: directory on the node where the source file is, and where the target file will be copied.
        from_name: file to copy
        to_name : the new file.
    """
    print('scp '+host+':/' + source+ ' to ' + target)
    cmd = 'scp ' + host + ':' + source + ' ' + target
    os.system(cmd)


def execute_remote_command(host, cmd):
    """ Run command on an ARTS node. Assumes ssh keys have been set up
        cmd: command to run
    """
    ssh_cmd = "ssh {} \"{}\"".format(host, cmd)
    print("Executing '{}'".format(ssh_cmd))
    return os.system(ssh_cmd)

# --- plot functions  ---

def do_electricity_plots(title, xx,yy, legends, type, output_html,y_axis_title='verbruik'):
    """
    :param title: Title of Plot
    :param x: dict with data for x-axis (time)
    :param y: dict with data for y_axix (usage)
    :return:
    """
    print('do_electricity_plots()')

    line_consumption = go.Scatter(
        x=xx[0],
        y=yy[0],
        mode='lines',
        name=legends[0]
    )
    line_redelivery = go.Scatter(
        x=xx[1],
        y=yy[1],
        mode='lines',
        name = legends[1]
    )
    bar_totals = go.Bar(
        x=xx[2],
        y=yy[2],
        marker=dict(
            color='rgb(255,221,0)',
        ),
        name=legends[2]
    )

    layout = go.Layout(
        title=title,
        xaxis=dict(tickangle=-45),
        plot_bgcolor='rgb(230,230,230)',
        yaxis = dict(
            title=y_axis_title,
            titlefont=dict(
            family='Courier New, monospace',
            size=18,
            color='#7f7f7f'),
        ),
        barmode = 'group',

    )

    data = [bar_totals,line_consumption,line_redelivery]

    fig = go.Figure(data=data, layout=layout)
    plotly.offline.plot(fig,filename=output_html)


def do_plot(title, x,y, type, output_html,y_axis_title='verbruik'):
    """

    :param title: Title of Plot
    :param x: dict with data for x-axis (time)
    :param y: dict with data for y_axix (usage)
    :return:
    """
    print('do_plot()')

    if type == 'bar':
        trace = go.Bar(
            x=x,
            y=y,
            marker=dict(
                color='rgb(0,129,201)',
            ),
        )
        layout = go.Layout(
            title = title,
            xaxis=dict(
                tickangle=-45,
                #tickvals=x
            ),
            yaxis=dict(
                title=y_axis_title,
                titlefont=dict(
                    family='Courier New, monospace',
                    size=18,
                    color='#7f7f7f'),
            ),

            barmode='group',
            plot_bgcolor='rgb(230,230,230)'
        )

    elif type == 'scatter':
        trace = go.Scatter(
            x=x,
            y=y,
            mode='lines')
        layout = go.Layout(
            title=title,
            xaxis=dict(tickangle=-45),
            plot_bgcolor='rgb(230,230,230)'
        )

    data = [trace]

    fig = go.Figure(data=data, layout=layout)
    plotly.offline.plot(fig,filename=output_html)


# --- data handling functions for io_mode = text ---

def sum_datasets(xx, yy, negate=False):
    """
    Sum all the x and y values of the 2 datasets in the dictionary d
    :param dd:
    :param negate: make the resulting dataset negative
    :return:
    """
    print('sum_datasets()')
    x_summed = []
    y_summed = []

    # concatenate the lists
    x_list = xx[0] + xx[1]
    y_list = yy[0] + yy[1]

    # iterate through the combined list and sum doubles
    try:
        for i in range(1,len(x_list)):
            x_value = x_list[i-1]
            y_value1 = y_list[i-1]

            # look for duplicates. If found, sum the y_values and remove the duplicate.
            pos = find_last_in_list(x_list, x_value)
            if pos>i-1:
                y_value2 = y_list[pos]
                y_value_summed = int(y_value1) + int(y_value2)

                # remove duplicate from both lists
                x_list.pop(pos)
                y_list.pop(pos)
            else:
                y_value_summed = int(y_value1)

            x_summed.append(x_value)
            if negate:
                y_summed.append(-y_value_summed)
            else:
                y_summed.append(y_value_summed)
    except:
        pass

    return x_summed,y_summed


def handle_next(interval, value, prev_value, timestamp, prev_timestamp, condensed_x, condensed_y):
    # determine sensible presentation value for x-axis
    x_label = prev_timestamp

    if interval == 'day':
        x_label = datetime.datetime.strftime(prev_timestamp, "%d %b")

    if interval == 'hour':
        x_label = datetime.datetime.strftime(prev_timestamp, "%d %b %H %p")

    if interval == 'month':
        x_label = datetime.datetime.strftime(prev_timestamp, "%b")

    condensed_x.append(x_label)

    # add the condensed usage (gas or electricity) to the y-axis
    usage = value - prev_value
    condensed_y.append(usage)
    print(str(timestamp) + ' ' + str(usage))


def condense(x,y, interval):
    print('condense data with interval '+interval)
    condensed_x = []
    condensed_y = []

    # initialize 
    prev_timestamp = x[0]
    prev_value = y[0]
    next = False

    for i in range(1,len(x)):
        #timestamp = datetime.datetime.strptime(x[i], TIME_FORMAT)
        timestamp = x[i]
        value = y[i]

        if interval == 'minute':
            if timestamp.minute != prev_timestamp.minute:
                next = True

        if interval == 'hour':
            if timestamp.hour != prev_timestamp.hour:
                next = True

        if interval == 'day':
            if timestamp.date() != prev_timestamp.date():
                next = True

        if interval == 'month':
            if timestamp.month != prev_timestamp.month:
                next = True

        # default
        if interval is None:
            if (i % 10)==0:
                next = True

        # next limit found
        if (next):
            handle_next(interval, value, prev_value, timestamp, prev_timestamp, condensed_x, condensed_y)

            # prepare the variables for the next round
            prev_timestamp = timestamp
            prev_value = value
            next = False

    # finally add the last value
    handle_next(interval, value, prev_value, timestamp, prev_timestamp, condensed_x, condensed_y)

    return condensed_x, condensed_y


# --- IO functions  ---
def get_x_value(i, starttime, interval):
    months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']

    if interval.upper() == 'MONTH':
        x_value = months[i - 1]
    elif interval.upper() == 'WEEK':
        x_value = weeknumber_to_date(starttime, i)
    else:
        x_value = i


    return x_value

def format_data_from_qbackend(args, starttime, my_data, dataset='gas'):

    net_low_total = my_data.get('data')[0].get('total')
    net_low_data  = my_data.get('data')[0].get('data')

    consumption_total = my_data.get('data')[1].get('total')
    consumption_data  = my_data.get('data')[1].get('data')

    net_high_total = my_data.get('data')[2].get('total')
    net_high_data  = my_data.get('data')[2].get('data')

    gas_total = my_data.get('data')[3].get('total')
    gas_data  = my_data.get('data')[3].get('data')

    generation_total  = my_data.get('data')[4].get('total')
    generation_data = my_data.get('data')[4].get('data')

#    np_consumption = np.array(consumption_data)
#    np_generation = np.array(generation_data)
#    np_net_high = np.array(net_high_data)
#    np_net_low = np.array(net_low_data)

#    np_netto = np_net_high + np_net_low
#    np_generation = (np_consumption - np_netto)
#    np_generation = np_generation * -1
#    np_consumption = np_consumption - np_generation

#    consumption_data = np_consumption.tolist()
#    generation_data = np_generation.tolist()

    # interate through the data to find the usage per timestamp

    # there is still a bug in the qserver resolution,
    # for gas it still calculates it own resolution instead of using the provided one.
    # a work around is to provide the 'dataset' value in the paramters to indicate which
    # dataset should be used for the interval.
    if args.dataset=='gas':
        length = len(gas_data)
    else:
        length = len(consumption_data)

    interval = args.interval
    x = []      # timestamps
    y = []      # values per timestamp

    for i in range(1, length+1):

        # x-axis
        x.append(get_x_value(i, starttime, interval))

        # y-axis
        if (dataset.upper()=='GAS'):
            y.append(gas_data[i-1])
        elif (dataset.upper()=='CONSUMPTION'):
            y.append(consumption_data[i-1])
        elif (dataset.upper()=='NETTO'):
            y.append(net_low_data[i-1]+net_high_data[i-1])
        elif (dataset.upper()=='GENERATION' or dataset.upper()=='REDELIVERY'):
            y.append(generation_data[i-1])

    return x,y


def get_data_from_qbackend(args, starttime, endtime):
    # http://192.168.178.62/api/getseries?sn=15-49-002-081&from=2018-12-01&to=2018-12-02

    # the backend service does not accept times, so reformat the times
    startdate = starttime.date()
    enddate = endtime.date()
    if startdate == enddate:
        enddate = enddate + datetime.timedelta(days=1)

    url = args.qbackend + '/?sn='+args.qbox_sn
    url = url + '&from='+str(startdate)+'&to='+str(enddate)

    # resolution
    # OneMinute = 1,
    # FiveMinutes = 5,
    # Hour = 60,
    # Day = 1440,
    # Week = 10080,
    # Month = 43800 // gemiddelde van 365 dagen

    url = url + '&resolution='+args.interval

    print("get_data_from_qbackend("+url+")")
    print("timerange   : "+str(startdate)+" - "+str(enddate))
    response = requests.get(url)

    # Check for HTTP codes other than 200
    if response.status_code != 200:
        raise Exception("Error accessing API: " + response.status_code);

    # Decode the JSON response into a dictionary and use the data
    data = response.json()
    return data


def parse_txt_file(filename, starttime, endtime):
    """
    read the qbox datafile
    :param filename:
    :return: x,y, dicts with values per timestamp
    """
    print("parse_txt_file: "+filename)
    print("timerange   : "+str(starttime)+" - "+str(endtime))
    # initialisation
    x = []
    y = []

    with open(filename) as my_file:

        # read and skip the first few lines of information
        start_of_file = my_file.readline()
        end_of_file = my_file.readline()
        id = my_file.readline()
        line = my_file.readline()

        # read the data
        i = 0
        while line:
            try:
                line = my_file.readline().rstrip()
                i = i +1
                s = line.split(" : ")

                # skip empty data
                if s[1]!='empty slot':
                    timestamp = datetime.datetime.strptime(s[0], TIME_FORMAT)
                    # check if the record is between the given starttime and endtime
                    if (timestamp > starttime and timestamp < endtime):
                        data = int(s[1].split(',')[1])/1000
                        x.append(timestamp)
                        y.append(data)

            except:
                # eof reached, just continue
                pass
    return x,y


# --- presentation functions ---
def do_single_plot_presentation(args, starttime, endtime):

    if args.remote_host != None:
        # copy the files from a remote location.
        source = os.path.join(args.remote_dir, args.filename)
        target = os.path.join(args.local_dir, args.filename)
        scp_filename(args.remote_host, source, target)

    # remote_host and qbackend should be mutually exclusive, because there is no need to copy the ascii files
    # when the backend API is used. But if you want, you can still do both and copy the ascii files also.
    if args.io_mode=='qbackend':
        data = get_data_from_qbackend(args, starttime, endtime)
        x, y = format_data_from_qbackend(args, starttime, data, args.dataset)
    else:
        # get the data from a text file. The textfile must be in the format that QboxNext.DumpQbx delivers it.
        x, y = parse_txt_file(os.path.join(args.local_dir, args.filename), starttime, endtime)

        # condense and stack the data based on the given interval (hour, day, week, month, year)
        x, y = condense(x, y, args.interval)

    # use plotly to make a html page with a plot
    do_plot(args.title, x, y, args.type, args.output_html, args.y_axis_title)


def do_electricity_presentation_qbackend(args, starttime, endtime):
    xx = []
    yy = []

    data = get_data_from_qbackend(args, starttime, endtime)

    # consumption
    x, y = format_data_from_qbackend(args, starttime, data, 'consumption')
    xx.append(x)
    yy.append(y)

    # generation
    x, y = format_data_from_qbackend(args, starttime,data, 'generation')
    xx.append(x)
    yy.append(y)

    # netto
    x, y = format_data_from_qbackend(args,starttime, data, 'netto')
    xx.append(x)
    yy.append(y)

    # x_summed, y_summed = sum_datasets(xx, yy)

    # create the cumulative list
    # x_total, y_total = sum_datasets(xxx, yyy)


    legends = args.legends.split(",")

    # use plotly to make a html page with a plot
    do_electricity_plots(args.title, xx, yy, legends, args.type, args.output_html, args.y_axis_title)


def do_electricity_presentation_text(args, starttime, endtime):
    # multiple files
    # assume: consumption1, consumption2, redelivery1,redelivery2
    xxx = []
    yyy = []

    if args.consumption_files != None:
        xx = []
        yy = []
        filenames = args.consumption_files.split(',')
        for filename in filenames:

            if args.remote_host != None:
                # copy the files from a remote location.
                source = os.path.join(args.remote_dir, filename)
                target = os.path.join(args.local_dir, filename)
                scp_filename(args.remote_host, source, target)

            x, y = parse_txt_file(os.path.join(args.local_dir, filename), starttime, endtime)
            x, y = condense(x, y, args.interval)

            xx.append(x)
            yy.append(y)

        x_summed, y_summed = sum_datasets(xx, yy)

        xxx.append(x_summed)
        yyy.append(y_summed)

    if args.redelivery_files != None:
        xx = []
        yy = []
        filenames = args.redelivery_files.split(',')

        for filename in filenames:

            if args.remote_host != None:
                # copy the files from a remote location.
                source = os.path.join(args.remote_dir, filename)
                target = os.path.join(args.local_dir, filename)
                scp_filename(args.remote_host, source, target)

            x, y = parse_txt_file(os.path.join(args.local_dir, filename), starttime, endtime)
            x, y = condense(x, y, args.interval)

            xx.append(x)
            yy.append(y)
            # datasets.append(dataset)

        x_summed, y_summed = sum_datasets(xx, yy, negate=True)

        xxx.append(x_summed)
        yyy.append(y_summed)

    # create the cumulative list
    x_total, y_total = sum_datasets(xxx, yyy)
    xxx.append(x_total)
    yyy.append(y_total)
    legends = args.legends.split(",")

    # use plotly to make a html page with a plot
    do_electricity_plots(args.title, xxx, yyy, legends, args.type, args.output_html, args.y_axis_title)


def do_electricity_presentation(args, starttime, endtime):
    if args.io_mode == 'qbackend':
        do_electricity_presentation_qbackend(args, starttime, endtime)
    else:
        do_electricity_presentation_text(args, starttime, endtime)


def get_arguments(parser):
    """
    Gets the arguments with which this application is called and returns the parsed arguments.
    If a parfile is give as argument, the arguments will be overrided
    The args.parfile need to be an absolute path!
    :param parser: the argument parser.
    :return: Returns the arguments.
    """
    args = parser.parse_args()
    if args.parfile:
        args_file = args.parfile
        if os.path.exists(args_file):
            parse_args_params = ['@' + args_file]
            # First add argument file
            # Now add command-line arguments to allow override of settings from file.
            for arg in sys.argv[1:]:  # Ignore first argument, since it is the path to the python script itself
                parse_args_params.append(arg)
            args = parser.parse_args(parse_args_params)
        else:
            raise (Exception("Can not find parameter file " + args_file))
    return args


def main():
    """
    The main module.
    """
    parser = argparse.ArgumentParser(fromfile_prefix_chars='@')

    # general parameters
    parser.add_argument("--qbox_sn",
                        default="15-49-002-081",
                        help="The qbox serial number is on the sticker on you qbox. It is needed to access the data in the qbackend")
    # IO parameters
    parser.add_argument("--io_mode",
                        default=None,
                        help="Communication mode. Possible options: local_text, remote_text, qbackend")

    parser.add_argument("--filename",
                        default=None,
                        help="txt file to parse (when txt file parsing is used)")
    parser.add_argument("--dataset",
                        default=None,
                        help="dataset to parse (when qbackend is used). Possible options: gas, consumption, generation")
    parser.add_argument("--consumption_files",
                        default=None,
                        help="high and low peak electricity consumption files (181, 182)")
    parser.add_argument("--redelivery_files",
                        default=None,
                        help="high and low peak electricity redelivery files (281, 282)")
    parser.add_argument("--qbackend",
                        default=None,
                        help="The url to the API that delivers the data in json format. For example: http://192.168.178.62/api/getseries")
    parser.add_argument("--remote_host",
                        default=None,
                        help="remote ssh/scp host where the files are stored (if None, then they are assumed to be local)")
    parser.add_argument("--remote_dir",
                        default=None,
                        help="remote directory where the files are stored")
    parser.add_argument("--remote_pre_command",
                        default=None,
                        help="execute this command on the remote host before downloading the data files")
    parser.add_argument("--remote_post_command",
                        default=None,
                        help="execute this command on the remote host after generating the html results.")
    parser.add_argument("--local_dir",
                        default='',
                        help="local directory where the data files are stored or read")

    # visualisation parameters
    parser.add_argument("--legends",
                        default="verbruik,teruglevering,totaal",
                        help="Legends for consumption, redelivery and totals.")
    parser.add_argument("--output_html",
                        default="qbx_plot.html",
                        help="output html file")
    parser.add_argument("--presentation",
                        default=None,
                        help="Possible options: single, electricity")

    parser.add_argument("--mode",
                        default=None,
                        help="Default modes. Possible options: today, this_week, this_month, this_year")

    parser.add_argument("--starttime",
                        default=None,
                        help="Format like 2019-01-12 00:00")
    parser.add_argument("--endtime",
                        default=None,
                        help="Format like 2019-01-12 00:00")
    parser.add_argument("--interval",
                        default="day",
                        help="Shows bars per interval. Possible options: minute, hour, day, month")
    # plot parameters
    parser.add_argument("--title",
                        default="Title",
                        help="Title of the Plot")
    parser.add_argument("--y_axis_title",
                        default="Verbruik",
                        help="Title on the Y axis")
    parser.add_argument("--type",
                        default="bar",
                        help="Chart type. Possible options: bar, scatter")

    # All parameters in a file
    parser.add_argument('--parfile',
                        nargs='?',
                        type=str,
                        help='Parameter file containing all the parameters')
    parser.add_argument("--version",
                        default=False,
                        help="Show current version of this program.",
                        action="store_true")

    args = get_arguments(parser)

    # --------------------------------------------------------------------------------------------------------
    if (args.version):
        print('--- qbx_plot.py - version 1.1.0 - 19 jan 2019 ---')
        print('Copyright (C) 2019 - Nico Vermaas. This program comes with ABSOLUTELY NO WARRANTY;')
        return

    print('--- qbx_plot.py - version 1.1.0 - 19 jan 2019 ---')
    print('Copyright (C) 2019 - Nico Vermaas. This program comes with ABSOLUTELY NO WARRANTY;')
    if args.starttime != None:
        starttime = datetime.datetime.strptime(args.starttime, TIME_FORMAT)

    # if no endtime is specified, then the endtime is now
    if args.endtime != None:
        endtime = datetime.datetime.strptime(args.endtime, TIME_FORMAT)
    else:
        endtime = datetime.datetime.now()

    # some default modes
    # today
    if args.mode=='today':
        endtime = datetime.datetime.now()
        starttime = endtime.replace(hour=0, minute=0)

    # this_month
    if args.mode=='this_month':
        endtime = datetime.datetime.now()
        starttime = endtime.replace(day=1, hour=0, minute=0)

    # this_year
    if args.mode=='this_year':
        endtime = datetime.datetime.now()
        starttime = endtime.replace(month=1,day=1, hour=0, minute=0)

    if args.remote_pre_command != None:
        execute_remote_command(args.remote_host, args.remote_pre_command)

    # determine the type of presentation
    presentation = args.presentation

    # for backward compatibility with version 1.0,
    # the presentation mode was interpreted from the definition of the datafiles
    if presentation == None:
        if args.consumption_files==None:
            presentation="single"
        else:
            presentation="electricity"


    # for a single dataset
    if presentation=="single":
       do_single_plot_presentation(args, starttime, endtime)

    # for a combined dataset
    if presentation=="electricity":
       do_electricity_presentation(args, starttime, endtime)


    if args.remote_post_command != None:
        execute_remote_command(args.remote_host, args.remote_post_command)


if __name__ == "__main__":
        #try:
        main()
        #except Exception as error:
        #    print(str(error))

