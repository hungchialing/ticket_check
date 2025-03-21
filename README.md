# ticket_check
python 爬售票

簡單寫了一個可以針對網址去做搜尋網站架構有沒有出現關鍵字的爬蟲

有使用random來做重新整理的時間間隔

config.ini檔可以做以下的更改

[範例]

url = 網址

check_interval = 5 我要的秒數

keyword = 立即訂購

use_selenium = true

min_interval_factor = 0.7 秒數前後最小值

max_interval_factor = 1.5 秒數前後最大值

