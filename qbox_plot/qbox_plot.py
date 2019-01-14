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
def do_plots(title, xx,yy, type, output_html,y_axis_title='verbruik'):
    """

    :param title: Title of Plot
    :param x: dict with data for x-axis (time)
    :param y: dict with data for y_axix (usage)
    :return:
    """
    print('do_plots()')

    bar_totals = go.Bar(
        x=xx[2],
        y=yy[2],
        marker=dict(
            color='rgb(255,221,0)',
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

    line_consumption = go.Scatter(
        x=xx[0],
        y=yy[0],
        mode='lines'
    )
    line_redelivery = go.Scatter(
        x=xx[1],
        y=yy[1],
        mode='lines'
    )

    layout = go.Layout(
        title=title,
        xaxis=dict(tickangle=-45),
        plot_bgcolor='rgb(230,230,230)'
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
                tickvals=x
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

    #layout = go.Layout(title=title, plot_bgcolor='rgb(255, 230,230)')
    fig = go.Figure(data=data, layout=layout)

    plotly.offline.plot(fig,filename=output_html)
    # plotly.offline.plot({"data": data, "layout": layout}, auto_open=True)

def find_last_in_list(list, value):
    pos = max(loc for loc, val in enumerate(list) if val == value)
    return pos

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

def condense(x,y, interval):
    print('condense data with interval '+interval)
    condensed_x = []
    condensed_y = []

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
           # determine sensible presentation value for x-axis
           x_label = prev_timestamp

           if interval == 'day':
               x_label = datetime.datetime.strftime(prev_timestamp, "%d %b")

           if interval == 'hour':
               x_label = datetime.datetime.strftime(prev_timestamp, "%d %b %H %p")

           condensed_x.append(x_label)

           # add the condensed usage (gas or electricity) to the y-axis
           usage = value - prev_value
           condensed_y.append(usage)
           print(str(timestamp) + ' ' + str(usage))

           prev_timestamp = timestamp
           prev_value = value
           next = False

    return condensed_x, condensed_y


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
                        default=None,
                        help="txt file to parse")
    parser.add_argument("--filenames",
                        default=None,
                        help="txt files to parse")
    parser.add_argument("--consumption_files",
                        default=None,
                        help="high and low peak electricity consumption files (181, 182)")
    parser.add_argument("--redelivery_files",
                        default=None,
                        help="high and low peak electricity redelivery files (281, 282)")
    # general parameters
    parser.add_argument("--output_html",
                        default="qbx_plot.html",
                        help="output html file")


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
    parser.add_argument("--y_axis_title",
                        default="Verbruik",
                        help="Title on the Y axis")

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

    # for a single file
    if args.filename!=None:
        x,y = parse_txt_file(args.filename, starttime, endtime)

        # condense and stack the data based on the given interval (hour, day, week, month, year)
        x,y = condense(x,y,args.interval)

        do_plot(args.title,x,y, args.type, args.output_html, args.y_axis_title)

    # multiple files
    # assume: consumption1, consumption2, redelivery1,redelivery2
    xxx = []
    yyy = []

    if args.consumption_files!=None:
        xx = []
        yy = []
        filenames = args.consumption_files.split(',')
        for filename in filenames:
            x, y = parse_txt_file(filename, starttime, endtime)
            x, y = condense(x, y, args.interval)

            xx.append(x)
            yy.append(y)

        x_summed, y_summed = sum_datasets(xx,yy)

        xxx.append(x_summed)
        yyy.append(y_summed)

    if args.redelivery_files != None:
        xx = []
        yy = []
        filenames = args.redelivery_files.split(',')

        for filename in filenames:
            x, y = parse_txt_file(filename, starttime, endtime)
            x, y = condense(x, y, args.interval)

            xx.append(x)
            yy.append(y)
            # datasets.append(dataset)

        x_summed, y_summed = sum_datasets(xx, yy, negate=True)

        xxx.append(x_summed)
        yyy.append(y_summed)

    if args.consumption_files!=None:
        # create the cumulative list
        x_total, y_total = sum_datasets(xxx,yyy)
        xxx.append(x_total)
        yyy.append(y_total)
        do_plots(args.title, xxx, yyy, args.type, args.output_html, args.y_axis_title)



if __name__ == "__main__":
    main()