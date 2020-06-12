#!/usr/bin/env python
import re
import sys
import copy
import heapq

def get_method_timeslce(line):
    strarray = line.split()
    method_num = int(strarray[0])
    if not (1 <= method_num  or method_num <= 6):
        raise Exception("method Range error")
    time_slice = int(strarray[1])
    if time_slice <= 0:
        raise Exception("Time slice Range error")
    return method_num, time_slice

def id_to_char(process_id):
    id_num = int(process_id)
    if id_num < 0:
        raise Exception("id range error")
    if 0 <= id_num and id_num <= 9:
        return chr(ord('0') + id_num)
    return chr(ord('A') + id_num - 10)

def Test1():
    test_gantt = []
    gantt_chart_gen(test_gantt, 0, 3, 'a')
    gantt_chart_gen(test_gantt, 3, 4, 'b')
    gantt_chart_gen(test_gantt, 4, 6, 'c')
    print_gantt(test_gantt, 'test', sys.stdout)

def method_fcfs(process_list, finish_time_dict, method_order_out, f):
    #print('has probleam')
    gantt = []
    queue = [v for v in sorted(process_list, key=lambda item: (item['arrival time'], item['id']))]
    time = 1
    while queue:
        process = queue.pop(0)
        gantt_chart_gen(gantt, time, time + process['cpu_burst'], process['id'])
        time += process['cpu_burst']
        finish_time_dict.setdefault(process['id_num'], {})['FCFS'] =  time

    print_gantt(gantt, 'FCFS', f)
    method_order_out.append('FCFS')

def arrival(process_list, last_arrival, queue, time):
    for arrival_proc in process_list:
        if arrival_proc['is_arrival'] == False and arrival_proc['arrival time'] <= time:
            arrival_proc['is_arrival'] = True
            queue.append(arrival_proc)

def find_min_arrival_time(process_list, last_arrival):
    # find a not arrivaled process min time
    time = last_arrival +  1000
    for arrival_proc in process_list:
        if arrival_proc['is_arrival'] == False:
            time = min(time, arrival_proc['arrival time'])
    return time

def method_rr(process_list, time_slice, finish_time_dict, method_order_out, f):
    # init Remaining cpu_burst and arrival
    process_list = [v for v in sorted(process_list, key=lambda item: (item['arrival time'], item['id']))]

    last_arrival = 0
    for proc in process_list:
        proc['RCB'] = proc['cpu_burst']
        proc['is_arrival'] = False
        last_arrival = max(last_arrival, proc['arrival time'])

    # round robin
    gantt = []
    queue = []

    time = -1
    while process_list:
        # arrival a Processe
        arrival(process_list, last_arrival, queue, time)
        if not queue: # empty queue
            time = find_min_arrival_time(process_list, last_arrival)
        else: # not empty
            process = queue.pop(0)
            cost_time = min(process['RCB'], time_slice)
            process['RCB'] -= cost_time
            gantt_chart_gen(gantt, time, time + cost_time, process['id'])
            time += cost_time

            # arrival a Processe
            arrival(process_list, last_arrival, queue, time)

            if process['RCB'] != 0:
                queue.append(process)
            else:
                finish_time_dict.setdefault(process['id_num'], {})['RR'] = time
                process_list.remove(process)

    print_gantt(gantt, 'RR', f)
    method_order_out.append('RR')

def get_process_key(item, priority_key):
    return (item[priority_key], item['last_use_cpu_time'], item['arrival time'], item['id'])

def get_process_key_by_cpu_burst(item):
    return (item['cpu_burst'], item['arrival time'], item['id'])

def arrival_to_priority_queue(arrival_queue, priority_queue, time):
        while arrival_queue and arrival_queue[0]['arrival time'] <= time:
            proc = arrival_queue.pop(0)
            key_val = get_process_key_by_cpu_burst(proc)
            heapq.heappush(priority_queue, (key_val, proc))

def method_nsjf(process_list, finish_time_dict, method_order_out, f):
    gantt = []
    arrival_queue = [v for v in sorted(process_list, key=lambda item: (item['arrival time'], item['cpu_burst'], item['id']))]
    priority_queue = []

    time = -1
    while priority_queue or arrival_queue:
        arrival_to_priority_queue(arrival_queue, priority_queue, time)
        if not priority_queue:
            proc = arrival_queue.pop(0)
            key_val = get_process_key_by_cpu_burst(proc)
            heapq.heappush(priority_queue, (key_val, proc))
            time = proc['arrival time']

        proc = heapq.heappop(priority_queue)[1]

        # run cpu time
        cost_time = proc['cpu_burst']
        gantt_chart_gen(gantt, time, time + cost_time, proc['id'])
        time += cost_time
        finish_time_dict.setdefault(proc['id_num'], {})["NPSJF"] = time

        # arrival all before the process finish
        arrival_to_priority_queue(arrival_queue, priority_queue, time)


    print_gantt(gantt, "Non-PSJF", f)
    method_order_out.append("NPSJF")



def time_preemptive(process, arrival_queue, priority_queue, time):
    # arrival preemptive
    while arrival_queue and arrival_queue[0]['arrival time'] < time + process['RCB']:
        proc = arrival_queue.pop(0)
        key_val = get_process_key(proc, 'RCB')
        heapq.heappush(priority_queue, (key_val, proc))

        item = process
        key_val = (item['RCB'] - (proc['arrival time'] - time), -item['last_use_cpu_time'], item['arrival time'], item['id'])
        if priority_queue[0] < (key_val, process):
            proc = heapq.heappop(priority_queue)[1]
            return  proc['arrival time'] - time, proc

    if priority_queue:
        proc = heapq.heappop(priority_queue)[1]
        return process['RCB'], proc

def pp_preemptive(process, arrival_queue, priority_queue, time):
    # arrival preemptive
    while arrival_queue and arrival_queue[0]['arrival time'] < time + process['RCB']:
        proc = arrival_queue.pop(0)
        key_val = get_process_key(proc, 'Priority')
        heapq.heappush(priority_queue, (key_val, proc))

        if priority_queue[0] < (get_process_key(process, 'Priority'), process):
            proc = heapq.heappop(priority_queue)[1]
            return  proc['arrival time'] - time, proc

    if priority_queue:
        proc = heapq.heappop(priority_queue)[1]
        return process['RCB'], proc


def init_process_list(process_list):
    for proc in process_list:
        proc['RCB'] = proc['cpu_burst']
        proc['last_use_cpu_time'] = 0

def method_preemptive(process_list, finish_time_dict, method_order_out, preemptive_method, priority_key, title, f):
    # init Remaining cpu_burst and arrival
    init_process_list(process_list)

    gantt = []
    arrival_queue = [v for v in sorted(process_list, key=lambda item: (item['arrival time'], item[priority_key], item['id']))]
    priority_queue = []
    process = None

    time = -1
    while arrival_queue or priority_queue or process:
        if process == None:
            process = arrival_queue.pop(0)
            time = process['arrival time']
            key_val = get_process_key(process, priority_key)
            heapq.heappush(priority_queue, (key_val, process))
            continue
        cost_time, next_process = process['RCB'], None
        if arrival_queue or priority_queue:
            # PSJF next process arrival
            cost_time, next_process = preemptive_method(process, arrival_queue, priority_queue, time)
        # use cpu
        process['RCB'] -= cost_time
        process['last_use_cpu_time'] = time
        gantt_chart_gen(gantt, time, time + cost_time, process['id'])
        time += cost_time

        if process['RCB'] == 0:
            finish_time_dict.setdefault(process['id_num'], {})[title] = time
        else:
            key_val = get_process_key(process, priority_key)
            heapq.heappush(priority_queue, (key_val, process))

        process = next_process

    print_gantt(gantt, title, f)
    method_order_out.append(title)

def method_psjf(process_list, finish_time_dict, method_order_out, f):
    method_preemptive(process_list, finish_time_dict, method_order_out, time_preemptive, 'RCB', 'PSJF', f)

def method_pp(process_list, finish_time_dict, method_order_out, f):
    method_preemptive(process_list, finish_time_dict, method_order_out, pp_preemptive, 'Priority', 'Priority', f)

def do_method(method_num, time_slice, process_list, finish_time_dict, method_order_out, f):
    process_list = copy.deepcopy(process_list)
    if method_num == 1: # 1. FCFS (First Come First Serve)
        method_fcfs(process_list, finish_time_dict, method_order_out, f)
    elif method_num == 2: # 2. RR (Round Robin)
        method_rr(process_list, time_slice, finish_time_dict, method_order_out, f)
    elif method_num == 3: # 3. PSJF (Preemptive Shortest Job First)
        method_psjf(process_list, finish_time_dict, method_order_out, f)
    elif method_num == 4: # 4. NSJF (Non-preemptive Shortest Job First)
        method_nsjf(process_list, finish_time_dict, method_order_out, f)
    elif method_num == 5: # 5. PP (Preemptive Priority)
        method_pp(process_list, finish_time_dict, method_order_out, f)
    elif method_num == 6: # 6. ALL
        for num in range(1, 6):
            do_method(num, time_slice, process_list, finish_time_dict, method_order_out, f)
    else:
        print(method_num)
        print('error method num')

def count_time(process_list, finish_time_dict, turnaround_time_dict, wait_time_dict, method_order):
    for process in [{ 'id': proc['id_num'], 'cpu_burst': proc['cpu_burst'], 'arrival_time': proc['arrival time']} for proc in process_list]:
        id_num = process['id']
        cpu_burst = process['cpu_burst']
        arrival = process['arrival_time']
        turnaround_time_dict.setdefault(id_num, {})
        wait_time_dict.setdefault(id_num, {})
        for method in method_order:
           turnaround_time_dict[id_num][method] = finish_time_dict[id_num][method] - arrival
           wait_time_dict[id_num][method] = turnaround_time_dict[id_num][method] - cpu_burst

def print_dict(time_dict, method_order, f):

    f.write('{:<8}'.format('id'))
    for method in method_order:
        f.write('{:<8}'.format(method))
    f.write('\n')

    splitline(f)

    for id_num, v in sorted(time_dict.items(), key=lambda item: item[0]):
        f.write('{:<8}'.format(id_num))
        for method in method_order:
            f.write('{:<8}'.format(time_dict[id_num][method]))
        f.write('\n')
    splitline(f)

def splitline(f):
    f.write('===========================================================\n')

def gantt_chart_gen(gantt_out_list, startTime, endTime, id_char):
    if len(gantt_out_list) > startTime:
        print(''.join(gantt_out_list))
        print(startTime)
        raise Exception('gantt_out_list error')

    for i in range(startTime, endTime):
        gantt_out_list.append(id_char)

def print_gantt(gantt_out_list, title, f):
    f.write('=={:>8}==\n'.format(title))
    f.write('-{}\n'.format(''.join(gantt_out_list)))

def load_and_run(name):
    method_num = time_slice = 0
    with open(name, "r") as f:
        counter = 1
        process_list = []
        for line in f:

            if counter == 1:
                # line1: method, time slice
                method_num, time_slice = get_method_timeslce(line)
            elif counter == 2:
                # drop
                pass
            else:
                # data
                array = line.split()
                process = {
                    'id' : id_to_char(array[0]),
                    'id_num' : int(array[0]),
                    'cpu_burst' : int(array[1]),
                    'arrival time' : int(array[2]),
                    'Priority' : int(array[3])
                }

                # print(process)
                process_list.append(process)
            counter += 1

    # data struct example
    # { id_num: {methon: time} }
    # example:
    # { 13: {'FCFS': 10} }
    finish_time_dict = {}
    wait_time_dict = {}
    turnaround_time_dict = {}
    method_order = []

    outname = name.replace('input', 'output')
    if outname == name:
        outname = name + '.output'
    with open(outname, 'w') as f:
        do_method(method_num, time_slice, process_list, finish_time_dict, method_order, f)
        count_time(process_list, finish_time_dict, turnaround_time_dict, wait_time_dict, method_order)

        f.write('Waiting Time\n')
        print_dict(wait_time_dict, method_order, f)

        f.write('Turnaround Time\n')
        print_dict(turnaround_time_dict, method_order, f)

while True:
    filename = input('> ')
    load_and_run(filename)
