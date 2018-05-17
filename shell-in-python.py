# coding: utf-8
# python 3.6.4

import subprocess
import time
from datetime import datetime
import pytz
import os
import sys

# pip install tzlocal
from tzlocal import get_localzone 
# necessary to get local timestamp


# input shell file name as an argument while running this python file
SHELL_FILE = sys.argv[1]
TOP_LEVEL_DIR = "./log/"


# create directory if exists
def lazy_create_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
            
# takes the shell file location, runs it and returns a buffered reader of the output
def terminal(shell_file_path):
    command = "bash -C " + shell_file_path
    run = subprocess.Popen(command.split(), shell = False, stdout = subprocess.PIPE)
    return run.stdout

# get the system time
def get_time():
    return datetime.now()

# get minute from system time
def get_minute(now):
    return now.minute

# get hour from system time
def get_hour(now):
    return now.hour

# get day from system time
def get_day(now):
    return now.day

# print time in the required format with timezone
def time_printer(now):
    return now.astimezone(get_localzone()).isoformat()

# remove microseconds from the timestamp
def remove_microseconds(timestamp):
    split_time = timestamp.split("-")
    return "-".join(split_time[:-2] + [split_time[-2][:-3]] + [split_time[-1]])

# parse the hour folder name from timestamp (timezone) and hour of the day
def get_hour_folder(hour,timestamp):
    timezone = timestamp.split("+")[-1].split("-")[-1]
    return str(hour) + "-" + timezone + "/"

# parse the day folder name from timestamp
def get_day_folder(timestamp):
    return timestamp.split("T")[0] + "/"

# create the log file from timestamp and unique id
def filename_from_timestamp(time_stamp, unique_id, folder="hour/"):
    lazy_create_dir(TOP_LEVEL_DIR + folder)
    return TOP_LEVEL_DIR + folder + "my_log_" + str(unique_id) + "_" + remove_microseconds(str(time_stamp)) + ".log"

# change file after one minute
def change_file(f, file_name):
    f.close()
    f = open(file_name,"wb")
    print(file_name)
    return f


# returns a buffered reader to the output instead of printing in the terminal
buffer = terminal(SHELL_FILE)

unique_id = 1
store_flag = False
store = ""

# parse time to get day, hour and minute
now = get_time()
prev_minute = get_minute(now)
prev_hour = get_hour(now)
prev_day = get_day(now)

# parse day and hour folder names
day_folder = get_day_folder(time_printer(now))
hour_folder = get_hour_folder(prev_hour,time_printer(now))

# file name with directory info attached
file_name = filename_from_timestamp(time_printer(now), unique_id, day_folder + hour_folder)
print(file_name)
f = open(file_name,"wb")

while True:
    
    # change day folder
    if get_day(now) != get_day:
        prev_day = get_day(now)
        day_folder = get_day_folder(time_printer(now))
        
    # change hour foler
    if get_hour(now) != prev_hour:
        prev_hour = get_hour(now)
        hour_folder = get_hour_folder(prev_hour,time_printer(now))
        
    # change file after each minute
    if get_minute(now) != prev_minute:
        unique_id += 1
        file_name = filename_from_timestamp(time_printer(now), unique_id, day_folder + hour_folder)
        f = change_file(f, file_name)
        prev_minute = get_minute(now)
        
        # (edge case)
        if store_flag == True:
            f.write(store)
            store_flag = False
    
    line = buffer.readline()
    minute_from_shell = str(line.strip(), 'utf-8').split(":")[-2]
    
    # to take care of the last second being written in the previous file (edge case)
    if int(minute_from_shell) == prev_minute:
        f.write(line)
    else:
        #print("Edge case at work")
        store_flag = True
        store = line
    
    # update time
    now = get_time()

