
l = [0] * 10000
print('--process---')
start = time.time()
bubble_merge_process(l, 0, len(l), 4)
end = time.time()
print(end - start)

l = [0] * 100000
print('--process---')
start = time.time()
bubble_merge_process(l, 0, len(l), 4)
end = time.time()
print(end - start)

l = [0] * 500000
print('--process---')
start = time.time()
bubble_merge_process(l, 0, len(l), 4)
end = time.time()
print(end - start)

l = [0] * 1000000
print('--process---')
start = time.time()
bubble_merge_process(l, 0, len(l), 4)
end = time.time()
print(end - start)

l = [0] * 10000
print('--thread---')
start = time.time()
bubble_merge_thread(l, 0, len(l), 4)
end = time.time()
print(end - start)

l = [0] * 100000
print('--thread---')
start = time.time()
bubble_merge_thread(l, 0, len(l), 4)
end = time.time()
print(end - start)

l = [0] * 500000
print('--thread---')
start = time.time()
bubble_merge_thread(l, 0, len(l), 4)
end = time.time()
print(end - start)

l = [0] * 1000000
print('--thread---')
start = time.time()
bubble_merge_thread(l, 0, len(l), 4)
end = time.time()
print(end - start)

l = [0] * 10000
print('--merge---')
start = time.time()
bubble_merge(l, 0, len(l), 4)
end = time.time()
print(end - start)

l = [0] * 100000
print('--merge---')
start = time.time()
bubble_merge(l, 0, len(l), 4)
end = time.time()
print(end - start)

l = [0] * 500000
print('--merge---')
start = time.time()
bubble_merge(l, 0, len(l), 4)
end = time.time()
print(end - start)

l = [0] * 1000000
print('--merge---')
start = time.time()
bubble_merge(l, 0, len(l), 4)
end = time.time()
print(end - start)
