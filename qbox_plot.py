"""
    File name: qbx_plot.py
    Author: Nico Vermaas (nvermaas@xs4all.nl)
    Date created: 2019-01-13
    Description: Plot converted QboxNext datafiles.
"""

import os
import sys
import datetime

import plotly

import argparse
import plotly.plotly as py
import plotly.graph_objs as go
import plotly.figure_factory as FF


TIME_FORMAT = "%Y-%m-%d %H:%M"

def do_plot(title, x,y, type, output_html):
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
            textposition='auto',
            marker=dict(
                color='rgb(0,129,201)',

            ),

        )
        layout = go.Layout(
            title = title,
            xaxis=dict(tickangle=-45),
            barmode='group',
            plot_bgcolor='rgb(230,230,230)'
        )

    elif type == 'scatter':
        trace = go.Scatter(x=x, y=y, mode='lines')
        layout = go.Layout(title=title, plot_bgcolor='rgb(230,230,230')

    data = [trace]

    #layout = go.Layout(title=title, plot_bgcolor='rgb(255, 230,230)')
    fig = go.Figure(data=data, layout=layout)

    plotly.offline.plot(fig,filename=output_html)
    # plotly.offline.plot({"data": data, "layout": layout}, auto_open=True)


def do_plot_basic(title, x,y):
    """

    :param title: Title of Plot
    :param x: dict with data for x-axis (time)
    :param y: dict with data for y_axix (usage)
    :return:
    """
    print('do_plot()')
    trace = go.Scatter(x=x, y=y, mode='lines')
    data = [trace]

    layout = go.Layout(title=title, plot_bgcolor='rgb(255, 230,230)')

    plotly.offline.plot({
        "data": data,
        "layout": layout
    }, auto_open=True)


def combine(x,y, interval):
    print('combine data with interval '+interval)
    combined_x = []
    combined_y = []

    # initialize 
    #prev_timestamp = datetime.datetime.strptime(x[0], TIME_FORMAT)
    prev_timestamp = x[0]
    prev_value = y[0]
    next = False

    for i in range(1,len(x)):
        #timestamp = datetime.datetime.strptime(x[i], TIME_FORMAT)
        timestamp = x[i]
        value = y[i]

        # check if the 'next' condition is reached based on the interval
        if interval=='today':
           # check if the timestamp is still on the same day as the prev_timestamp
           if timestamp.day == prev_timestamp.day:
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
           # determine sensible presentation value for x-axis
           x_label = prev_timestamp

           if interval == 'day':
               x_label = datetime.datetime.strftime(prev_timestamp, "%d %b")

           combined_x.append(x_label)

           # add the combined usage (gas or electricity) to the y-axis
           usage = value - prev_value
           combined_y.append(usage)
           print(str(timestamp) + ' ' + str(usage))

           prev_timestamp = timestamp
           prev_value = value
           next = False

    return combined_x, combined_y

def parse_txt_file(filename, starttime, endtime):
    """
    read the qbox datafile
    :param filename:
    :return: x,y, dicts with values per timestamp
    """
    print("parsing file: "+filename)
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

# ------------------------------------------------------

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
    parser.add_argument("--filename",
                        default="2421.txt",
                        help="txt file to parse")
    # general parameters
    parser.add_argument("--output_html",
                        default="qbx_plot.html",
                        help="output html file")

    # Specification or Scheduler parameters (required)
    parser.add_argument("--starttime",
                        default=None,
                        help="Format like 2019-01-12 00:00")
    parser.add_argument("--endtime",
                        default=None,
                        help="Format like 2019-01-12 00:00")
    parser.add_argument("--interval",
                        default="day",
                        help="Shows bars per interval. Possible options: today, hour, day, week, month, year")
    # plot parameters
    parser.add_argument("--title",
                        default="Title",
                        help="Title of the Plot")
    parser.add_argument("--type",
                        default="bar",
                        help="Chart type. Possible options: bar, scatter")
    parser.add_argument("--examples", "-e",
                        default=False,
                        help="Show some examples",
                        action="store_true")
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
        print('--- qbx_plot.py - version 1.0 - 12 jan 2019 ---')
        return

    print('--- qbx_plot.py - version 1.0 - 12 jan 2019 ---')


    # get the data from a text file. The textfile must be in the format that QboxNext.DumpQbx delivers it.
    starttime = datetime.datetime.strptime(args.starttime, TIME_FORMAT)
    endtime = datetime.datetime.strptime(args.endtime, TIME_FORMAT)
    x,y = parse_txt_file(args.filename, starttime, endtime)

    # combine and stack the data based on the given interval (hour, day, week, month, year)
    x,y = combine(x,y,args.interval)

    do_plot(args.title,x,y, args.type, args.output_html)

if __name__ == "__main__":
    main()