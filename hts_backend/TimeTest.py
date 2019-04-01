
from __future__ import absolute_import
import datetime
import time
import json
import ast

import pandas as pd
import requests

from datetime import timezone, timedelta, datetime, date

import cryptocompare
from django.utils import timezone

def getCoinList():
    req = requests.get('https://www.cryptocompare.com/api/data/coinlist/').json()
    info = req['Data']
    coinList = pd.DataFrame(info)
    coinList = coinList.transpose()
    coinList.to_csv('coinList.csv')
    return coinList



"""
print(type(time.localtime()))
print(type(time.strftime("%H %M %S", time.localtime()).split(' ')))
a = 10
a = float(a)

b = 10
b = int(10)

print(int(b))

a = b
print(a)

print(cryptocompare.get_historical_price_day('BTC', curr='USC'))


"""

currentPrice = cryptocompare.get_price('EOS', 'USD')
currentPrice = currentPrice['EOS']['USD']
print(currentPrice)

timestamp = time.time()
dt_utc = datetime.fromtimestamp(timestamp, timezone.utc)
print(dt_utc)

timestamp = time.time()
dt_utc = datetime.fromtimestamp(timestamp, timezone.utc)
kmt = dt_utc + timedelta(hours=9)
print(type(kmt))
print(kmt)
print(kmt)
timestamp = time.time()
dt = datetime.fromtimestamp(timestamp)
dt_utc = datetime.fromtimestamp(timestamp, timezone.utc)
kmt = dt_utc + timedelta(hours=9)

timestamp = time.time()
dt_utc = datetime.fromtimestamp(timestamp, timezone.utc)
kmt = dt_utc + timedelta(hours=9)
# 여기서부터 day를 추출해서 하면 오류의 여지가 줄어든다
yesterday = kmt - timedelta(days=1)
#yesterday.hour = 0
print(yesterday)

kmtstr = str(kmt)
kmtstr = kmtstr.split(' ')
print(kmtstr)
dates1 = kmtstr[0]
dates1 = dates1.split('-')
print(dates1[1])

kmtYest = kmt - timedelta(days=2)
kmtstr = str(kmtYest)
kmtstr = kmtstr.split(' ')
print(kmtstr)
dates1 = kmtstr[0]
dates1 = dates1.split('-')
print(dates1[1])


print(dt_utc + timedelta(hours=9))
print(type(dt_utc)) #datetime type
#print("datetime.fromtimestamp(timestamp, utc_timezone) => %s " % dt_utc)
#tz = timezone(timedelta(9))
#dt_9 = datetime.fromtimestamp(timestamp, tz)
#print("datetime.fromtimestamp(timestamp, 9_timezone) => %s \n" % dt_9)


print((time.strftime("%Y%m%d", time.localtime())))
#print((time.strftime("%Y%m%d", time.localtime() + timedelta(days=1))))
print((time.strftime("%H %M %S", time.localtime())))
timeElemtnets = time.ctime() #.split(" ")
#day = timeElemtnets[0]
#month = timeElemtnets[1]
#date = timeElemtnets[2]

Clock = time.strftime("%H %M %S", time.localtime()).split(' ')#timeElemtnets[3].split(':')

#print(type(timeElemtnets[4]))

#print(timeElemtnets)
print(Clock)
Hour = Clock[0]
Min = Clock[1]
Sec = Clock[2]
#print(day) #Sat Sun
#print(type(day))
BasicFID = "10;11;12;13;16;17;18;"
# 현재가,전일대비,등락률,누적거래, 시가, 고가, 저가

HoggaMado = "41;42;43;44;45;46;47;48;49;"
QuantMado = "61;62;63;64;65;66;67;68;69;"

HoggaMaSu = "52;52;53;54;55;56;57;58;59;"
QuantMaSu = "71;72;73;74;75;76;77;78;79;"
TotalFid = BasicFID + HoggaMado + QuantMado + HoggaMaSu + QuantMaSu

A = TotalFid.split(';')
print(A)
print(type(A))

A = {}
text_data = json.dumps(A)
print(text_data)
print(type(text_data))

print(type(ast.literal_eval(text_data)))
print(ast.literal_eval(text_data))

"""
tags = Tag.objects.filter(field_name='string_or_field')
posts = Post.objects.filter(tags__in=tags)
#list to qset
"""

A = "+1234"
B = int(A)
C = "-1234"
D = int(B)
print(B)
print(D)

Hour = Clock[0]
Min = Clock[1]

print(Hour)
print(Min)

print(int(Hour) > 15)
print(int(Hour) < 9)

print(not ((int(Hour) > 15 and int(Min) > 30) or (int(Hour) < 9))) #장중이 아니면
print(((not(int(Hour) > 15 and int(Min) > 30)) and (not int(Hour) < 9)))

#print((not(int(Hour) > 15 and int(Min) > 30)))
#print((not (int(Hour) < 9)))

#print(type(cryptocompare.get_historical_price_day('BTC', curr='USC')))
#print(cryptocompare.get_historical_price_day('BTC', curr='USC'))
#print("")
#print("")
#print(cryptocompare.get_historical_price_hour('BTC', curr='USC'))
#dictD = cryptocompare.get_historical_price_day(sobj.Share_Code, curr='USC')

T = {"128": "-8787", "129": "91.37", "299": "-0.34", "138": "+8787", "139": "109.45", "13": "555841", "215": " ",
     "21": "122933", "23": "-12350", "24": "7074", "68": "15187", "201": "-0.40", "291": " 0", "292": "0",
     "293": "3", "294": " 0", "295": "0.00", "41": "-12350", "42": " 12400", "43": "+12450", "44": "+12500",
     "45": "+12550", "46": "+12600", "47": "+12650", "48": "+12700", "49": "+12750", "50": "+12800",
     "51": "-12300", "52": "-12250", "53": "-12200", "54": "-12150", "55": "-12100", "56": "-12050",
     "57": "-12000", "58": "-11950", "59": "-11900", "60": "-11850", "61": "788", "62": "10592",
     "63": "8136", "64": "10088", "65": "9893", "66": "13317", "67": "13493", "scd": "002800", "69": "5898",
     "70": "14412", "71": "951", "72": "4405", "73": "10506", "74": "12167", "75": "14788", "76": "8315",
     "77": "16217", "78": "8688", "79": "13787", "80": "3193", "81": "0", "82": "0", "83": "0", "84": "0",
     "85": "0", "86": "0", "87": "0", "88": "0", "89": "+1000", "90": "0", "91": "0", "92": "0", "93": "0", "94": "0",
     "95": "0", "96": "0", "97": "0", "98": "0", "99": "0", "100": "0", "238": "5", "121": "101804", "122": "+1000",
     "200": "-50", "125": "93017", "126": "0"}

T2 = {"299": "-10.53", "10": "-192500", "11": "-500", "12": "-0.26", "13": "222135", "14": "22831", "15": "+1",
     "16": "+194000", "17": "+194500", "18": "-192000", "20": "145041", "21": "145042", "23": "+2550000",
     "24": "16361", "25": "5", "26": "-27875", "27": "-192500", "28": "-192000", "29": "-5378219500",
     "30": "-80.95", "31": "0.17", "32": "638", "290": "2", "291": " 0", "292": "0", "293": "3", "294": " 0",
     "295": "0.00", "41": "+2564000", "42": "+2565000", "43": "+2566000", "44": "+2567000", "45": "+2568000",
     "46": "+2569000", "47": "+2570000", "48": "+2571000", "49": "+2572000", "50": "+2573000", "51": "+2563000",
         "52": "+2562000", "53": "+2561000", "54": "+2560000", "311": "132372", "56": "+2558000", "57": "+2557000",
         "58": "+2556000", "59": "+2555000", "60": "+2554000", "61": "1312", "62": "4519", "63": "1239", "64": "2943",
         "65": "1273", "66": "2155", "67": "5780", "68": "914", "69": "497", "70": "744", "71": "383", "72": "578",
         "73": "789", "74": "495", "55": "+2559000", "76": "142", "77": "198", "78": "619", "79": "274", "80": "106",
         "81": "0", "82": "0", "83": "+1", "84": "0", "85": "0", "86": "0", "87": "0", "88": "0", "89": "0", "90": "0",
         "91": "0", "92": "0", "93": "0", "94": "0", "95": "0", "96": "0", "97": "0", "98": "0", "99": "0", "100": "0",
         "121": "21376", "122": "+1", "125": "3968", "126": "0", "128": "-17408", "129": "18.56", "138": "+17408",
         "139": "538.71", "691": "0", "75": "384", "scd": "005930", "200": "+51000", "201": "+2.04", "215": " ",
         "228": "51.48", "238": "2"}


T3 = {"128": "-17534", "129": "16.73", "299": "-10.53", "138": "+17534", "139": "597.84", "13": "231320", "215": " ",
      "21": "151014", "23": "+2550000", "24": "16361", "201": "+2.04", "291": " 0", "292": "0", "293": "3", "294": " 0",
      "295": "0.00", "41": "+2562000", "42": "+2563000", "43": "+2564000", "44": "+2565000", "45": "+2566000",
      "46": "+2567000", "47": "+2568000", "48": "+2569000", "49": "+2570000", "50": "+2571000", "51": "+2561000",
      "52": "+2560000", "53": "+2559000", "54": "+2558000", "55": "+2557000", "56": "+2556000", "57": "+2555000",
      "58": "+2554000", "59": "+2553000", "60": "+2552000", "61": "427", "62": "1264", "63": "1160", "64": "4649",
      "65": "1190", "66": "2585", "67": "1287", "68": "2263", "69": "5239", "70": "992", "71": "676", "72": "1365",
      "73": "401", "74": "40", "75": "78", "76": "522", "77": "165", "78": "110", "79": "81", "80": "84", "81": "+6",
      "82": "-6", "83": "0", "84": "0", "85": "0", "86": "0", "87": "0", "88": "0", "89": "0", "90": "0", "91": "0",
      "92": "0", "93": "0", "94": "0", "95": "0", "96": "0", "97": "0", "98": "0", "99": "0", "100": "0", "238": "2",
      "121": "21056", "122": "0", "200": "+51000", "125": "3522", "126": "0", "scd": "005930"}

#print(T["10"])
#yesterdayPrice = cryptocompare.get_historical_price('BTC', 'USD', timestamp=datetime.datetime(2018, 4, 22))
#print(yesterdayPrice)
#currentPrice = cryptocompare.get_price('BTC', 'USD')  # ('BTC')
#print(currentPrice)

#dictD = cryptocompare.get_historical_price_day('BTC', curr='USC')
#print(type(dictD))

#print(day)

A = getCoinList()
#print(A)
CoinNameList = A['CoinName']
#TotalCoinSupplyList = A["TotalCoinSupply"]
#print(type(A))
print(CoinNameList['BTC'])
#print(A)

#print(CoinNameList)
#print(TotalCoinSupplyList) #task 초입에서 선언하고 활용

coins = cryptocompare.get_coin_list(format=True)

ll = []
for x in coins:
    c = x + " : " + str(CoinNameList[x])
    #ll.append(c)
    print(c)

"""
print(int(False))
A = "2018" + "04" + "21"
print((int(A) > 20180422))

coininfo = getCoinList()
# print(A)
TotalCoinSupplyList = coininfo["TotalCoinSupply"]
print((TotalCoinSupplyList))

A = "                           20181131"
print(int(A))
"""