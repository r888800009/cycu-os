# cycu-os Hw2
- 資訊三甲 10612150 林詠翔

## 使用開發環境:
- 開發平台: CPU: Intel i5-6300HQ (4) @ 3.200GHz, Memory: 12G
- 使用的程式語言: Python 
- 使用開發環境: Linux 64bit (archlinux), vim, Python 3.8.3


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

輸入檔名
``` plaintext
> in/input1.txt
>
```

之後可以看到同目錄多了一個 `output1.txt` 為輸出檔

能夠處理 FCFS, NSJF, PSJF, RR, PP ，或者五個都使用的方法

## 流程
排程時只在抵達或結束的時候檢查 Process 順序
## 基本流程
1. 請求使用者輸入檔名
2. 載入檔案，讀取**選取的方法**、**Time slice**、**process**
3. 執行指定的排程方法，完成排程法之後產生並回傳 **finish time** 與**印出甘特圖**
4. 計算 turnaround time, waiting time
5. 顯示這兩個時間

### 公式
- Turnaround Time = Finish time - Arrival time
- Waiting Time = Turnaround time - CPU Burst

### FCFS
1. 將輸入的 Process Table 以 `arrival time`, `id` 排序，並且將排序後的結果
存入一個佇列當中，佇列保存各個 Process table
2. 將佇列依序 pop ，處理各個 Process，並且畫出甘特圖與計算
**目前的時間**與**結束時間**，並且以結束時間作為下一個 Process 的起點

### RR
1. 如 FCFS 一樣，先把 Process Table 排序，之後次序都會按照排序結果
2. 初始化 Process Table 的剩餘時間、是否抵達布林值
3. 檢查是否還有 Process 尚未完成，如果有執行
    1. 讓目前這個時間可以抵達的 Process 都放入佇列 
    2. 如果佇列為空就找到**還沒抵達的Process**中可以最早抵達的 Process 的時間
    3. 從佇列取出 Process 花費比 time slice 多的話，就扣除 time slice，反之則是 Process
花費的時間
    4. 讓 Process 完成後，這段時間可以抵達的 Process 先抵達
    5. 如果還有剩餘時間就放回 queue 中，否則標記完成並且計算結束時間
4. 畫出甘特圖

### NSJF
該方法有兩個佇列，分別為 arrival_queue 與 priority_queue，
當中有這兩個 queue 根據不同鍵值進行排序，前者而言鍵值為
``` plaintext
(item['arrival time'], item['cpu_burst'], item['id'])
```
也就是說，會以抵達時間、CPU 花費時間、ID 依序排序，因為 arrival_queue 
的內容尚未抵達，理應透過抵達時間作為參考

而後者則是
``` plaintext
(item['cpu_burst'], item['arrival time'], item['id'])
```
CPU 花費時間、抵達時間、ID 依序排序，在這 queue 當中的所有 Queue 已經抵達，
因此必須透過 CPU 花費時間排序而非抵達時間。

當中這些佇列都會取最小鍵值。

1. 當這兩個 queue 其中一個不為空時
2. 先將這段時間可以抵達 Process 全部放入 priority_queue 中
3. 如果 priority_queue 為空則取一個 Process 抵達並放入該佇列
4. 取 Priority queue 最先者，並且把該 Process 的時間用完，並且計算下一段時間
5. 讓先前這段時間能抵達的 Process 全抵達放入 priority_queue 中

### PSJF && PP
這兩個方法非常類似，並且 Process 格外保存的剩餘 CPU 時間與最後使用 CPU 時間，在一開始
都先初始化該值，也如同 NSJF 有 arrival_queue 與 priority_queue，前者會以
抵達時間、PSJF 以剩餘時間或 PP 優先級、ID 由小到大排序。

而 PSJF 的搶奪是根據任意時段中，當前 Process 剩餘時間與抵達的 Process 的 CPU 時間
作為判斷，而 PP 則是根據 Process table 的 Priorty 進行判斷能否搶奪

佇列使用的鍵值類似這樣
``` plaintext
(item[priority_key], item['last_use_cpu_time'], item['arrival time'], item['id'])
```
當中 `priority_key` 按照使用 PSJF 或 PP 做不同的變化

1. 如果還有 Process 可以抵達或優先佇列有 Process
2. 取一個 Process 並且判斷 CPU 過程中是否會被搶奪
3. 將無法搶奪者全部放入優先佇列直到遇到搶奪者或結束
4. 如果可以搶奪則讓時間停在搶奪者 Process 的抵達時間，
並且計算原本 Process 的剩餘時間，並且放入優先佇列中
5. 紀錄結束時間
6. 如果有搶奪者 Process ，下一輪以該 Process 判斷，否則執行之前以排進優先佇列的 Process

## data structure
### 時間保存
為了方便保存與處理時間資訊，透過三個 dict 保存時間內容。
``` python 
finish_time_dict = {}
wait_time_dict = {}
turnaround_time_dict = {}
```

裡面可以保存多個 process 的finish, waitting turnaround time 等等，其基本架構為:
``` python
{ id_num: {methon: time} }
```

以 process 13 透過 FCFS 處理後的時間來說，表示方法會變成
``` python
{ 13: {'FCFS': 10} }
```

並且透過不同 process 與方式跑好之後，內容可能會變成
``` python 
{ 
  13: {'FCFS': 10, 'RR': 40}, 
  15: {'FCFS': 40, 'RR': 50}
}
```

同時會保存一個 list 保存使用過的排程方法，並且透過該 list 的內容把，
之前保存的時間顯示出來。

### Process Table
程式在讀檔之後，會把讀取的資訊存入 python 的 dict 中，並且把每個 Process 的
ID、CPU Burst、Arrival Time、Priority 切分出來，之後把這些資料存入一個 list，
以變之後可以透過檔案所描述的方法處理。
``` python
process_list = []

process = {
    'id' : id_to_char(id),              # process 的 id 以 char 表示
    'id_num' : int(id),                 # process 的 id 
    'cpu_burst' : int(cpu_burst),       # CPU 花費的時間
    'arrival time' : int(arrival_time), # 到達時間
    'Priority' : int(proirity)          # 優先級
}
```

#### 格外的屬性
- `process['is_arrival']`: 在 RR 方法中採用，代表是否已經抵達，為布林值
- `process['RCB']`: 代表剩下所需的時間，在 RR, PSJF, PP 中都有使用到，
初始值為 `process['cpu_burst']`
- `process['last_use_cpu_time']`: 初始值為 `0` ，該屬性代表最後一次使用 CPU 的時間，
用於決定 Process 的優先順序

## 未完成的功能
無

