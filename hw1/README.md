# cycu-os
- 資訊三甲 10612150 林詠翔

## 使用開發環境:

- 開發平台: CPU: Intel i5-6300HQ (4) @ 3.200GHz, Memory: 12G
- 使用的程式語言: Python 
- 使用開發環境: Linux 64bit (archlinux), vim, Python 3.8.2 + Numba

為了加快 Python 速度，使用 Numba 的JIT 處理 氣泡排序與Merge sort的部份，
並且四題都有完成。

一開始請求使用者輸入檔名，之後程式會去讀取檔案裡面的題號，之後把資料讀進程式並且呼叫對映題號函數，
根據題目要求決定要不要輸入格外參數，之後輸出一個 output 檔。



## 說明你的程式設計(功能，使用的data structure)
檢視說明文件
``` bash
chromium README.html
```

下載原始碼解壓縮並且執行

``` bash
unzip 10612150.zip
cd 10612150
python ./main.py
```

### 使用方法
先輸入檔名，模式為2, 3, 4的話程式會要求輸入切割的次數，之後會顯示輸出檔。
``` plaintext
filename: input.txt
ans1
time: 0.28061532974243164
output file: input.txt.output
filename: input2.txt
ans2
k: 4
time: 0.09701848030090332
output file: input2.txt.output
filename:
```

程式顯示 `input.txt.output` 與 `input2.txt.output` 都是排列好的輸出檔。
第一行為排序好的資料，第二行為時間。

### 氣泡排序法 流程
1. 外迴圈變數選擇當前排序目標位置
2. 內迴圈嘗試把最大值推到目標位置

### 合併
1. 傳入兩個要合併陣列在主陣列的索引範圍
2. 複製兩個子陣列
3. 以迴圈多次比較內容，每次取最小者優先放入陣列

### One Process 
將資料切成 k 份，並且透過單 Process 進行排序

1. 將資料切成 k 個區間，透過 `list` 保存區間範圍 
2. 區間個別透過 Bubble Sort 排序
3. 透過遞迴的方式實做合併排序法，不過傳入參數是區間，
僅僅做合併的行為不再分解。

### Process 與 Thread 合併排序法順序排程
1. 切割多個區間範圍，並以 `list` 保存
2. 將此 `list` 作為合併排序法的傳入陣列
3. 原先合併排序的 `Merge()` 改成放入 Priority Queue 遞迴並使深度大者優先(遞迴節點深度，而非 `DFS` 演算法)
這裡把這些叫做 `Task` 的節點。
4. 在排程工作中，設定號誌來解決合併順序(生產者消費者問題)，
因此如果有 Thread 或 Process 提前完成工作，並且排序下一個大區塊時，
不會因為下面尚未完成使資料錯誤。
5. 由 Process 或 Thread 各自取得佇列，直到佇列為空

### k Thread 流程
資料切成 k 份透過 k 個 Thread 進行排序，複製資料之後在傳入排序演算法以免 Numba 出錯。

1. 與 One Process 的差別在於，氣泡排序法在區間切割好之後，丟給 k 個執行緒執行。
並且最後做 join 的行為，等待所有氣泡排序法執行緒完成。
2. 呼叫排程合併排序法排程的函數
3. 建立 k - 1 個 Thread 執行，這些 Thread 會在 Queue 取出 `Task` ， Python 有提供線程安全的 Queue ，
因此在使用 Queue 時， Python 會處理互斥性。
4. Thread 取出 `Task` 之後，這個資料結構裡面存放三個號誌，分別是自身、兩個等待合併，
的資料。 並且 Thread 會等待底下兩個資料合併完成之後，號誌釋放才會進行合併的行為，
並且釋放自身的號誌。

### k Process 流程
資料切成 k 份，透過 k 個 Process 進行排序，與 k Thread 的寫法類似，
差別在於:

- 號誌透過 Python 的 Manager 處理，達成共享記憶體的功能。
- 排程合併順序之後，會把優先佇列的內容存到 `manager.Queue` ，
達到共享多個 Process 的效果。
- 在合併之前，原始資料被複製到 `multiprocessing.Array` ，
達成共享記憶體的效果。


由於 Numba 無法處理 Python 共享記憶體的物件，因此在氣泡排序與合併排序時，
會先複製一份資料在傳入函數，最後在複製回共享記憶體。

## 使用的data structure
Process 與 Thread 在進行 Marge 前，先切割多個區間，並且以區間進行 Merge Sort 的排程，
會展開一個 Marge sort 的樹狀結構，並且排程由下自上完成。

這個方法會產生一個以號誌產生出來的樹狀結構，並且節點全部存放於 Priority Queue 中，
當中節點以 `Task` 組成， `TaskProcess` 則是適用於 Process 的節點。

``` python
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
```

之後 Process 透過 Manager 共享記憶體，為透過 Server process 去共享資料的方法。

## 時間統計

測量方法

透過以下寫法測量各種排序方法的速度，以下是 K Process 排序的範例
``` python 
start = time.time()
bubble_merge_process(l, 0, len(l), 4)
end = time.time()
print(end - start)
```

以下圖表皆以秒為單位
![比較速度](fig1.png)


| 資料筆數  | bubble sort  | process      | thread       | merge        |
|-----------|--------------|--------------|--------------|--------------|
| 10,000    | 0.1261167526 | 0.0893228054 | 0.5930533409 | 0.1272084713 |
| 100,000   | 11.30908847  | 1.127340794  | 3.272245169  | 3.757363558  |
| 500,000   | 283.9312696  | 21.58810401  | 74.93181825  | 75.82278562  |
| 1,000,000 | 1157.237283  | 86.55200291  | 292.4291878  | 296.1974378  |

切成 4 份，可以看一個Process執行速度約是氣泡排序法未切割的四倍，
n ^ 2 算出比例之後還要乘上分割的數量為 (n / k) ^ 2 * k ，可以導出 n ^ 2 / k，
因此是快 4 倍而不是 16 。

Thread 因為 Python 有 GIL 所以執行上與單一 Process 差不多，
並且比 Process 慢四倍，因為 Python 的 Process 幾乎使用所有核心，
Thread 只有單核心。


這裡採用 `taskset` 去限制 Process 的 CPU 數量，並且單獨比較 Thread 與
Process。
```  bash
taskset --cpu-list 0 ./main.py 
```

![比較process thread 速度](fig2.png)

| 資料筆數  | thread        | process      |
|-----------|---------------|--------------|
| 10,000    | 0.07281732559 | 0.1521923542 |
| 100,000   | 3.204283237   | 3.380565882  |
| 500,000   | 71.91410947   | 74.10192752  |
| 1,000,000 | 284.5606923   | 286.828119   |

可以看到 Thread 與 Process 幾乎重合， K  Thread 略小於 Process，
但數據上還是可以看到幾秒的差異，其中導致延遲應該與資料共享相關，
以及 Process 的 Context Switch 等等。
