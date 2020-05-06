#!/usr/bin/env python
from numba import jit
import time, queue
import threading, multiprocessing
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

#@jit(nopython=True)
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

def ans1():
    print('ans1')

def ans2():
    print('ans2')

def ans3():
    print('ans3')

def check(end, k):
    if k <= 0:
        raise "k cannot less equal 0"

    if k >= 10001:
        raise "k cannot Greater equal 10001"

    if end // k == 0:
        raise "k too large"

def thread_merge_thread(array, queue):
    while not queue.empty():
        item = queue.get()
        task = item.task

        print(item.priority)
        task.semaphoreL.acquire()
        task.semaphoreR.acquire()
        print('go')

        merge(array, task.start, task.middle, task.end)

        task.cur_semaphore.release()
    print('done')
@dataclass(order=False)
class Task:
    start: int
    middle: int
    end: int
    cur_semaphore: threading.Semaphore
    semaphoreL: threading.Semaphore
    semaphoreR: threading.Semaphore

@dataclass(order=True)
class PrioritizedItem:
    priority: int
    task: Any=field(compare=False)

def range_merge_schedule_process(array, splits, splits_start, splits_end_index, deep, queue):
    if splits_start < splits_end_index:
        q = (splits_start + splits_end_index) // 2

        semaphore1 = range_merge_schedule(array, splits, splits_start, q, deep + 1, queue)
        semaphore2 = range_merge_schedule(array, splits, q + 1, splits_end_index, deep + 1, queue)

        start = splits[splits_start][0]
        middle = splits[q][1]
        end = splits[splits_end_index][1]

        cur_semaphore = multiprocessing.Semaphore(0)

        task = Task(start, middle, end, cur_semaphore, semaphore1, semaphore2)

        item = PrioritizedItem(-deep, task)
        queue.put(item)
        return cur_semaphore
    else:
        # has resource
        return multiprocessing.Semaphore(1)

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
    j = 0
    bubble_sort(array, 0, len(array))
    for i in range(start, end):
        share_array[i] = array[j]
        j += 1

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
    managers = multiprocessing.Manager()
    pq_tmp = queue.PriorityQueue()
    q = multiprocessing.Queue()
    while not pq_tmp.empty():
        q.put(pq_tmp.get())

    range_merge_schedule_process(array, splits, 0, k - 1, 0, q)

    # merge
    processs = [0] * (k - 1)
    for i in range(0, k - 1):
        processs[i] = multiprocessing.Process(target=thread_merge_thread, args=(share_array, q))
        processs[i].start()

    # wait all merge done
    for i in range(0, k - 1):
       processs[i].join()

    # copy data
    for i in range(start, end):
        array[i] = share_array[i]

def bubble_merge_thread(array, start, end, k):
    splits = split_array(start, end, k)

    threads = []
    for i in splits:
        thread_tmp = threading.Thread(target=bubble_sort, args=(array, i[0], i[1]))
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

def ans4():
    print('ans4')

l = [2, 12389, 17823, 17232, 2387, 2, 123, 43, 4,3, 3,2 ,2 ]
bubble_sort(l, 0, len(l))
print(l)

l = [0] * 10000
start = time.time()
bubble_sort(l, 0, len(l))
end = time.time()
print(end - start)

for i in range(3,10):
    l = [2, 12389, 17823, 17232, 2387, 2, 123, 43, 4,3, 3,2 ,2 ]
    start = time.time()
    bubble_merge(l, 0, len(l), i)
    end = time.time()
    #print(end - start)
    print(l)

    l = [2, 12389, 17823, 17232, 2387, 2, 123, 43, 4,3, 3,2 ,2 ]
    bubble_merge_thread(l, 0, len(l), i)
    print(l)

    l = [2, 12389, 17823, 17232, 2387, 2, 123, 43, 4,3, 3,2 ,2 ]
    bubble_merge_process(l, 0, len(l), i)
    print(l)


def test():
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
# test()

ans1()
ans2()
ans3()
ans4()

