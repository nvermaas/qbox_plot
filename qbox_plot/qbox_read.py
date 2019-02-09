"""
    File name: qbox_read.py
    version: 1.0.0 (3 feb 2019)
    Author: Copyright (C) 2019 - Nico Vermaas (nvermaas@xs4all.nl)
    Date created: 2019-01-13
    Description: Read qbx files

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

import datetime, time
import struct

import argparse

rec_size = 26
none_value = 18446744073709551615

DATETIME_FORMAT = "%Y-%m-%d %H:%M"

def convertBytesToTimeStamp(b):
    """
    convert a 8 byte C# array to a python timestamp
    :param b:
    :return:
    """
    t1 = struct.unpack('<q', b)[0]
    secs = t1 / 10.0 ** 7
    delta = datetime.timedelta(seconds=secs)
    timestamp = datetime.datetime(1, 1, 1) + delta
    return timestamp


# this was the first rough function to read through a qbx.
# some of the functionlaity has been split off in better functions, but I left this in place for historical reasons.
def readQBX(filename):
    """
    StartOfFile: 19/01/2018 11:42:00
    EndOfFile:   25/01/2019 12:00:00
    ID:          d9f87792-67d3-4cec-94e1-959d17a97503
    Timestamp NL     :        raw,        kWh,      money, quality (kWh can be kWh, Wh or mWh depending on Precision setting)
    2018-01-19 11:42 :     276682,  276682000, 17154284000,     0
    2018-01-19 11:43 :     276682,  276682000, 17154284000,     0
    2018-01-19 11:44 :     276682,  276682000, 17154284000,     0
    """
    with open(filename, "rb") as binary_file:
        pointer = 0
        size = 8

        binary_file.seek(pointer)
        bytes=binary_file.read(size)
        pointer = pointer + size

        start_timestamp = convertBytesToTimeStamp(bytearray(bytes))
        print('start_timestamp = '+str(start_timestamp))
        current_timestamp = start_timestamp

        size = 8
        binary_file.seek(pointer)
        bytes=binary_file.read(size)
        pointer = pointer + size

        end_timestamp = convertBytesToTimeStamp(bytearray(bytes))
        print('end_timestamp = '+str(end_timestamp))

        # skip the id (16 bytes)
        size = 16
        pointer = pointer + size

        # start reading the data, every line is a minute
        """
            ulong raw = reader.ReadUInt64();
            ulong kWh = reader.ReadUInt64();
            ulong money = reader.ReadUInt64();
            ushort quality = reader.ReadUInt16();
        """
        #raw, kwh, money, quality = struct.unpack('<IH2B', data.read(8))

        size = 8 + 8 + 8 + 2

        while current_timestamp < end_timestamp:
            binary_file.seek(pointer)
            bytes=binary_file.read(size)
            pointer = pointer + size

            raw = 0
            kwh = 0
            raw,kwh,money, quality = struct.unpack('<QQQH', bytes) # expected : 1725222

            delta = datetime.timedelta(minutes=1)
            if kwh>0:
                if (int(raw) == none_value):
                    raw_str = '<none>'
                    factor = 0
                else:
                    raw_str = str(raw)
                    factor = int(kwh/raw)

                print(str(current_timestamp)+ ': ' + raw_str+', '+str(kwh)+ ' factor = '+str(factor))

            current_timestamp = current_timestamp + delta


def get_starttime(binary_file):
    """
    get the starttime from the binary QBX file.
    These are the first 8 bytes in C# timestamp format
    :param binary_file:
    :return: a timestamp
    """

    pointer = 0
    size = 8

    binary_file.seek(pointer)
    bytes = binary_file.read(size)

    timestamp = convertBytesToTimeStamp(bytearray(bytes))
    # print('start_timestamp = ' + str(timestamp))
    return timestamp


def get_endtime(binary_file):
    """
    get the endtime from the binary QBX file.
    These are the second 8 bytes in C# timestamp format
    :param binary_file:
    :return: a timestamp
    """

    pointer = 8
    size = 8

    binary_file.seek(pointer)
    bytes = binary_file.read(size)

    timestamp = convertBytesToTimeStamp(bytearray(bytes))
    # print('end_timestamp = ' + str(timestamp))
    return timestamp


def get_pointer(binary_file, starttime, timestamp):
    """
    Calculate the filepointer in the binary_file based on the starttime and required timestamp.
    There is one data record per minute, and the data records start after a header of 32 bytes.
    :param binary_file:
    :param starttime:
    :param timestamp:
    :return:
    """
    # print('get_pointer(' + str(starttime) + ',' + str(timestamp))

    # Convert to Unix timestamp
    d1_ts = time.mktime(starttime.timetuple())
    d2_ts = time.mktime(timestamp.timetuple())
    minutes = int(d2_ts-d1_ts) / 60

    # the data starts after a 32 bytes header
    offset = 32

    # each record in the QBX file is 26 bytes (8 + 8 + 8 + 2)
    rec_size = 26

    pointer = int((minutes * rec_size) + offset)
    return pointer


def get_record(binary_file, pointer):
    """
    a record is 26 bytes, convert the array of values
    :param binary_file:
    :param pointer:
    :return:
    """
    binary_file.seek(pointer)
    bytes = binary_file.read(rec_size)

    raw, kwh, money, quality = struct.unpack('<QQQH', bytes)  # expected : 1725222
    return raw, kwh


#------------------------------------------------------------------------------------

def write_record_to_file(filename, timestamp, raw, kwh):
    """
    write a value at a timestamp
    :param filename: qbx file to write values to
    :param timemstamp: location in the file to write values to
    :param raw,kwh : values to write (fake money and quality will be added also)
    :return:
    """

    # print('do_write_timestamp(' + filename + ',' + str(timestamp)+'))
    with open(filename, "r+b") as binary_file:
        # what is the timestamp at the starting position of the file pointer? (the beginning of the file)
        starttime = get_starttime(binary_file)

        # determine the file pointer based on the starttime and the required timestamp
        pointer = get_pointer(binary_file, starttime, timestamp)

        # create the record
        bytes = struct.pack('<QQQH', int(raw), int(kwh),0,0)

        # write the record
        binary_file.seek(pointer)
        binary_file.write(bytes)


def read_record_from_file(filename, timestamp):
    """
    return a value from a filename for a certain timestamp.
    testdata in 2421.txt: 2019-01-17 04:40 :    1788960, 1788955000, 110915210000,

    :param filename:
    :param timestamp:
    :return:
    """
    # print('do_show_timestamp(' + filename + ',' + str(timestamp)+'))
    with open(filename, "rb") as binary_file:
        # what is the timestamp at the starting position of the file pointer? (the beginning of the file)
        starttime = get_starttime(binary_file)

        # determine the file pointer based on the starttime and the required timestamp
        pointer = get_pointer(binary_file, starttime, timestamp)

        # read the record
        value = get_record(binary_file,pointer)
        print(timestamp)
        print(value)


def read_range(filename, t1, t2):
    """
    return the difference of the values at t2 - t1

    :param filename:
    :param t1,t2: timestamps
    :return:
    """
    # print('do_show_range(' + filename + ', ' + str(t1)+ ', ' + str(t2))

    with open(filename, "rb") as binary_file:
        starttime = get_starttime(binary_file)

        # determine the file pointer based on the starttime and the required timestamp
        pointer1 = get_pointer(binary_file, starttime, t1)
        pointer2 = get_pointer(binary_file, starttime, t2)

        # read the record
        value1 = get_record(binary_file, pointer1)
        value2 = get_record(binary_file, pointer2)

        delta = (value2 - value1)/1000
        print(str(value2/1000) + ' - '+ str(value1/1000) + ' = ' + str(delta))
        return delta


def repair_spikes(filename,t1,t2):
    """

    :param filename: qbx file to repair
    :param t1: timestamp to start searching from
    :param t2: timestamp to end the search
    :return:
    """

    print('repair_spikes(' + filename + ',' + str(t1)+' - '+str(t2)+')')
    with open(filename, "r+b") as binary_file:
        # what is the timestamp at the starting position of the file pointer? (the beginning of the file)
        starttime_in_file = get_starttime(binary_file)
        endtime_in_file = get_endtime(binary_file)

        timestamp = t1
        # don't try to go beyond EOF
        if t2 > endtime_in_file:
            t2 = endtime_in_file

        prev_raw = 1

        # position the file pointer to start reading the data
        pointer = get_pointer(binary_file, starttime_in_file, timestamp)

        while timestamp < t2:

            # read the data
            raw, kwh = get_record(binary_file, pointer)

            if (kwh>0):
                if (int(raw) == none_value):
                    raw_str = '<none>'
                    raw = prev_raw
                    # I want to repair the kwh column for raw = <none> also, otherwise the spikes persist
                    factor = int(kwh / raw)

                else:
                    raw_str = str(raw)
                    factor = int(kwh / raw)
                    prev_raw = raw

                print(str(timestamp)+ ': raw = '+raw_str+", kwh = "+str(kwh)+", factor = "+str(factor))

            # The factor between raw and kwh should be roughly 1000, usually it is 999 or 1000
            # spikes show up as huge numbers, but 1500 seems a good enough threshold
            if (factor>1500):
                print('*SPIKE* at '+str(timestamp)+'. Change kwh from '+str(kwh)+' to '+str(raw*1000))

                # create the new record
                kwh = raw * 1000
                bytes = struct.pack('<QQQH', int(raw), int(kwh), 0, 0)

                # write the record
                binary_file.seek(pointer)
                binary_file.write(bytes)

            # advance to the next record
            pointer = pointer + rec_size
            delta = datetime.timedelta(minutes=1)
            timestamp = timestamp + delta
            prev_raw = raw

def main():
    """
    The main module.
    """
    parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
    parser.add_argument("--operation","-o",
                        default="show_all",
                        help="show_all, read, write, range, repair")
    parser.add_argument("--filename","-f",
                        default=None,
                        help="qbx file to read")
    parser.add_argument("--timestamp","-t",
                        default=None,
                        help="read a value from a specific timestamp")
    parser.add_argument("--starttime","-t1",
                        default=None,
                        help="starttime of a range")
    parser.add_argument("--endtime","-t2",
                        default=None,
                        help="endtime of a range")
    parser.add_argument("--raw","-raw",
                        default=None,
                        help="value for the raw column")
    parser.add_argument("--kwh","-kwh",
                        default=None,
                        help="value for the kwh column")
    parser.add_argument("--examples","-e",
                        default=None,
                        help="Examples")

    print('--- qbox_read.py - version 1.2.1 - 9 feb 2019 ---')
    print('Copyright (C) 2019 - Nico Vermaas. This program comes with ABSOLUTELY NO WARRANTY;')

    args = parser.parse_args()

    if (args.examples):
        print("Show the whole file.")
        print('> qbox_read -o show_all -f 2421.qbx')
        print()
        print("Read the consumption value (meterstand) of a certain timestamp.")
        print('> qbox_read -o read -f 2421.qbx -t "2019-01-17 04:35"')
        print()
        print("Write a kwh,raw pair to a certain timestamp (be very careful with writing to your original files).")
        print('> qbox_read -o write -f 2421.qbx -t "2019-01-17 04:35" -kwh=123456 -raw=123456000')
        print()
        print("Show the difference in consumption value in a certain timerange.")
        print('> qbox_read -o range -f ..\\testdata\\15-49-002-081_00002421_Client0.qbx -t1 "2019-01-01 00:00" -t2 "2019-02-01 00:00"')
        print()
        return

    if (args.operation=='show_all'):
        readQBX(args.filename)
        return

    if (args.operation=='read'):
        timestamp = datetime.datetime.strptime(args.timestamp, DATETIME_FORMAT)
        read_record_from_file(args.filename, timestamp)
        return

    if (args.operation=='write'):
        timestamp = datetime.datetime.strptime(args.timestamp, DATETIME_FORMAT)
        write_record_to_file(args.filename, timestamp, args.kwh, args.raw)
        return

    if (args.operation=='range'):
        t1 = datetime.datetime.strptime(args.starttime, DATETIME_FORMAT)
        t2 = datetime.datetime.strptime(args.endtime, DATETIME_FORMAT)
        read_range(args.filename, t1, t2)
        return

    if (args.operation=='repair'):
        filename = '15-49-002-081_00002421_Client0.qbx'
        #write_record(filename,datetime.datetime.strptime('2019-02-08 10:36', DATETIME_FORMAT),2035550,2035550000)
        #write_record(filename,datetime.datetime.strptime('2019-02-08 10:37', DATETIME_FORMAT),2035570,2035570000)
        #write_record(filename,datetime.datetime.strptime('2019-02-08 10:38', DATETIME_FORMAT),2035580,2035580000)
        #write_record(filename,datetime.datetime.strptime('2019-02-08 10:39', DATETIME_FORMAT),2035590,2035590000)
        #write_record(filename,datetime.datetime.strptime('2019-02-08 10:40', DATETIME_FORMAT),2035600,2035600000)
        # 8:30 2041342 op de gasmeter
        t1 = datetime.datetime.strptime('2019-02-08 09:55', DATETIME_FORMAT)
        t2 = datetime.datetime.strptime('2019-02-09 12:00', DATETIME_FORMAT)
        repair_spikes(filename,t1,t2)
        return


if __name__ == "__main__":
        main()
