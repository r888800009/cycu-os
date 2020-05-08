#!/usr/bin/env python
from numba import jit
import time, queue
import threading, multiprocessing
import multiprocessing.managers
from dataclasses import dataclass, field
from typing import Any

@jit(nopython=True)
def bubble_sort(array, start, end):
    # end - 1 ~ start
    for i in range(end - 1, start, - 1):
        # start ~ end - 1
        for j in range(start, i):
            if array[j] > array[j + 1]:
                array[j], array[j + 1] = array[j + 1], array[j]

@jit(nopython=True)
def merge(array, start, middle, end):
    L = array[start:middle]
    R = array[middle:end]
    i = j = 0
    for k in range(start, end):
        if i < len(L) and j < len(R):
            if L[i] <= R[j]:
                array[k] = L[i]
                i += 1
            else:
                array[k] = R[j]
                j += 1
        elif i == len(L):
            array[k] = R[j]
            j += 1
        else:
            array[k] = L[i]
            i += 1


def check(end, k):
    if k <= 0:
        raise "k cannot less equal 0"

    if k >= 10001:
        raise "k cannot Greater equal 10001"

    if end // k == 0:
        raise "k too large"

def thread_merge_thread(array, q):
    try:
        while not q.empty():
            item = q.get(block=False)
            task = item.task

            task.semaphoreL.acquire()
            task.semaphoreR.acquire()

            merge_process(array, task.start, task.middle, task.end)

            task.cur_semaphore.release()
    except queue.Empty:
        return

def merge_process(share_array, start, middle, end):
    array = share_array[start:end]
    merge(array, 0, middle - start, end - start)
    share_array[start:end] = array[:]

def process_merge_process(array, q):
    try:
        while not q.empty():
            item = q.get(block=False)
            task = item.task

            task.semaphoreL.acquire()
            task.semaphoreR.acquire()

            merge_process(array, task.start, task.middle, task.end)

            task.cur_semaphore.release()
    except queue.Empty:
        return

@dataclass(order=False)
class Task:
    start: int
    middle: int
    end: int
    cur_semaphore: threading.Semaphore
    semaphoreL: threading.Semaphore
    semaphoreR: threading.Semaphore

@dataclass(order=False)
class TaskProcess:
    start: int
    middle: int
    end: int
    cur_semaphore: multiprocessing.managers.SyncManager
    semaphoreL: multiprocessing.managers.SyncManager
    semaphoreR: multiprocessing.managers.SyncManager

@dataclass(order=True)
class PrioritizedItem:
    priority: int
    task: Any=field(compare=False)

def range_merge_schedule_process(array, splits, splits_start, splits_end_index, deep, queue, manager):
    if splits_start < splits_end_index:
        q = (splits_start + splits_end_index) // 2

        semaphore1 = range_merge_schedule_process(array, splits, splits_start, q, deep + 1, queue, manager)
        semaphore2 = range_merge_schedule_process(array, splits, q + 1, splits_end_index, deep + 1, queue, manager)

        start = splits[splits_start][0]
        middle = splits[q][1]
        end = splits[splits_end_index][1]

        cur_semaphore = manager.Semaphore(0)

        task = TaskProcess(start, middle, end, cur_semaphore, semaphore1, semaphore2)

        item = PrioritizedItem(-deep, task)
        queue.put(item)
        return cur_semaphore
    else:
        # has resource
        return manager.Semaphore(1)

def range_merge_schedule(array, splits, splits_start, splits_end_index, deep, queue):
    if splits_start < splits_end_index:
        q = (splits_start + splits_end_index) // 2

        semaphore1 = range_merge_schedule(array, splits, splits_start, q, deep + 1, queue)
        semaphore2 = range_merge_schedule(array, splits, q + 1, splits_end_index, deep + 1, queue)

        start = splits[splits_start][0]
        middle = splits[q][1]
        end = splits[splits_end_index][1]

        cur_semaphore = threading.Semaphore(0)

        task = Task(start, middle, end, cur_semaphore, semaphore1, semaphore2)

        item = PrioritizedItem(-deep, task)
        queue.put(item)
        return cur_semaphore
    else:
        # has resource
        return threading.Semaphore(1)

def bubble_sort_process(share_array, start, end):
    array = share_array[start:end]
    bubble_sort(array, 0, len(array))
    share_array[start:end] = array[:]

def bubble_merge_process(array, start, end, k):
    splits = split_array(start, end, k)

    share_array = multiprocessing.Array('i', array)
    processs = []
    for i in splits:
        process_tmp = multiprocessing.Process(target=bubble_sort_process, args=(share_array, i[0], i[1]))
        process_tmp.start()
        processs.append(process_tmp)

    # wait all bubble_sort done
    for i in range(0, k):
        processs[i].join()

    # scheduling merging execution order
    manager = multiprocessing.Manager()
    q = manager.Queue()
    pq = queue.PriorityQueue()
    range_merge_schedule_process(array, splits, 0, k - 1, 0, pq, manager)

    while not pq.empty():
        q.put(pq.get())

    # merge
    processs = [0] * (k - 1)
    for i in range(0, k - 1):
        processs[i] = multiprocessing.Process(target=process_merge_process, args=(share_array, q))
        processs[i].start()

    # wait all merge done
    for i in range(0, k - 1):
       processs[i].join()

    # copy data
    array[:] = share_array[:]

def bubble_merge_thread(array, start, end, k):
    splits = split_array(start, end, k)

    threads = []
    for i in splits:
        thread_tmp = threading.Thread(target=bubble_sort_process, args=(array, i[0], i[1]))
        thread_tmp.start()
        threads.append(thread_tmp)

    # wait all bubble_sort done
    for i in range(0, k):
        threads[i].join()

    # scheduling merging execution order
    pq = queue.PriorityQueue()
    range_merge_schedule(array, splits, 0, k - 1, 0, pq)

    # merge
    threads = [0] * (k - 1)
    for i in range(0, k - 1):
        threads[i] = threading.Thread(target=thread_merge_thread, args=(array, pq))
        threads[i].start()

    # wait all merge done
    for i in range(0, k - 1):
        threads[i].join()


def split_array(start, end, k):
    check(end, k)
    splits = []
    split_size = end / k
    for i in range(0, k - 1):
        substart = start + int(i * split_size)
        subend = start + int((i + 1) * split_size)
        splits.append([substart, subend])

    substart = start + int((k - 1) * split_size)
    splits.append([substart, end])
    assert(len(splits) == k)
    return splits

def range_merge(array, splits, splits_start, splits_end_index, deep):
    if splits_start < splits_end_index:
        q = (splits_start + splits_end_index) // 2
        range_merge(array, splits, splits_start, q, deep + 1)
        range_merge(array, splits, q + 1, splits_end_index, deep + 1)

        start = splits[splits_start][0]
        middle = splits[q][1]
        end = splits[splits_end_index][1]

        merge(array, start, middle, end)

def bubble_merge(array, start, end, k):
    splits = split_array(start, end, k)

    for i in splits:
        bubble_sort(array, i[0], i[1])

    range_merge(array, splits, 0, k - 1, 0)

def test():
    ans = [i for i in range(1, 100)]
    ans2 = [i for i in range(1, 101)]
    q1 = ans.copy()
    q1.reverse()
    q2 = ans2.copy()
    q2.reverse()

    for i in range(3,10):

        l = q1.copy()
        bubble_merge(l, 0, len(l), i)
        assert(l == ans)

        l = q2.copy()
        bubble_merge(l, 0, len(l), i)
        assert(l == ans2)

        l = q1.copy()
        bubble_merge_thread(l, 0, len(l), i)
        assert(l == ans)

        l = q2.copy()
        bubble_merge_thread(l, 0, len(l), i)
        assert(l == ans2)

        l = q1.copy()
        bubble_merge_process(l, 0, len(l), i)
        assert(l == ans)

        l = q2.copy()
        bubble_merge_process(l, 0, len(l), i)
        assert(l == ans2)

    """
    l = [0] * 10000

    try:
        bubble_merge(l, 0, len(l), 10000)
    except:
        assert(False)

    try:
        bubble_merge(l, 0, len(l), 10001)
        assert(False)
    except:
        print(1)

    try:
        bubble_merge(l, 0, len(l), 0)
        assert(False)
    except:
        print(1)
    """

# test()

# JIT first
bubble_sort([0], 0, 0)
merge([0], 0, 0, 0)

def ans1(array):
    print('ans1')

    start = time.time()
    bubble_sort(array, 0, len(array))
    end = time.time()

    return  end - start

def ans2(array):
    print('ans2')
    k = int(input('k: '))
    start = time.time()
    bubble_merge_process(array, 0, len(array), k)
    end = time.time()
    return  end - start

def ans3(array):
    print('ans3')
    k = int(input('k: '))
    start = time.time()
    bubble_merge_thread(array, 0, len(array), k)
    end = time.time()
    return  end - start

def ans4(array):
    print('ans4')
    k = int(input('k: '))
    start = time.time()
    bubble_merge(array, 0, len(array), k)
    end = time.time()
    return  end - start

while True:
    try:
        filename = input("filename: ")
        timecost = 0
        with open(filename, "r") as f:
            command = int(f.readline())
            data = f.readline().split()

            array = [int(i) for i in data]

            if command == 1:
                timecost = ans1(array)
            elif command == 2:
                timecost = ans2(array)
            elif command == 3:
                timecost = ans3(array)
            elif command == 4:
                timecost = ans4(array)
            else:
                raise NameError

            f.close()

        with open(filename + '.output', "w") as f:
            for i in array:
                f.write('{} '.format(i))

            print('time: {}'.format(timecost))
            f.write('\ntime: {}\n'.format(timecost))
            print('output file: {}'.format(filename + '.output'))
            f.close()

    except ValueError:
        print('Data must be Number')
    except FileNotFoundError:
        print('file not found')
    except NameError:
        print('command not found')
    except EOFError:
        break
    except KeyboardInterrupt:
        break

