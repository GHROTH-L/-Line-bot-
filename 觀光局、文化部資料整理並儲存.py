#!/usr/bin/env python
# coding: utf-8

# # 清理所有Output活動資料

# *This file just only click "Cell" -> "Run All"

# In[105]:


#flask line bot 
from flask import Flask
app = Flask(__name__)
from flask import Flask, request, abort
from linebot import  LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextSendMessage, TextMessage, MessageTemplateAction, ButtonsTemplate,LocationMessage, LocationSendMessage,LocationAction,TemplateSendMessage,URITemplateAction, QuickReply, QuickReplyButton



#資料結構模組
import numpy as np
import scipy as sp
from pandas import Series, DataFrame
import pandas as pd

# 引入time模組
import time 
import datetime

#Crawler模組
import requests
from lxml import etree
from io import BytesIO
import requests
import json

#讀取google sheet 模組
#讀取excel
import openpyxl
#Python網頁爬蟲寫入資料到Google Sheet
import pygsheets

#引入模型
import joblib

#引入距離公式
from haversine import haversine, Unit


# # 演唱會

# In[106]:


'''
讀取json檔案
'''
URL = ("https://cloud.culture.tw/frontsite/trans/SearchShowAction.do?method=doFindTypeJ&category=17")
res = requests.get(URL)
k = res.json()


# In[107]:


contest = []
#不是每張都有照片，所以先指定一張網路照片
jpg = 'https://img.tixbar.com/concert/concert-list.jpg'
'''
使用迴圈，整理jason檔，並且將空的結束時間，讀取跟開始時間一樣
地點空值，也賦予他none
'''
for outer_key in k:
    for show_info_list_key in outer_key["showInfo"]:
        if show_info_list_key["endTime"] == "":
            show_info_list_key["endTime"] = show_info_list_key["time"]
        if show_info_list_key["price"] == "":
            show_info_list_key["price"] = 0
        if show_info_list_key["location"] == "":
            show_info_list_key["location"] = None            
        contest.append([outer_key["title"] ,outer_key["category"], show_info_list_key["time"], show_info_list_key["endTime"],show_info_list_key["location"],show_info_list_key["latitude"],show_info_list_key["longitude"],show_info_list_key["price"],jpg]) 


# In[ ]:


'''
因為最後output還是要展現出開始與結束時間，並轉呈dataframe 以利最後將為轉換（字串顯示)的時間放在最後兩欄位
'''
stime1 = []
etime1 = []
for i in range(len(contest[:])):
    stime1.append(contest[i][2])
    etime1.append(contest[i][3])
stime1 = pd.DataFrame(stime1)
etime1 = pd.DataFrame(etime1)


# In[109]:


'''
因為時間的格是要做轉變，所以先提取出來變成list，然後轉成時間戳記，以利後來與填寫表單者的時間做對比
後續轉成dataframe 再與主要的contest 做結合
'''
#將時間轉換成時間戳記
for i in range(len(contest[:])):
    contest[i][2] =int(time.mktime(time.strptime(contest[i][2], "%Y/%m/%d %H:%M:%S"))) 
    contest[i][3] =int(time.mktime(time.strptime(contest[i][3], "%Y/%m/%d %H:%M:%S"))) 

# timeString=contest[0][3]
# struct_time = time.strptime(timeString, "%Y/%m/%d %H:%M:%S")
# contest[0][3] = int(time.mktime(struct_time)) # 轉成時間戳


# In[111]:


contest2 = pd.DataFrame(contest)
#給予欄位名稱
contest2.columns = ['title', 'class', 'stime', 'etime', 'address', 'lat', 'long', 'fare','img']

#插入沒有改變的時間轉成datafrmae
contest2.insert(9,'stime1',stime1)
contest2.insert(10,'etime1',etime1)


# # 藝術節

# In[112]:


URL = ("https://cloud.culture.tw/frontsite/trans/SearchShowAction.do?method=doFindFestivalTypeJ")
res1 = requests.get(URL)
k2 = res1.json()


# In[113]:


act=[]
#名稱、類別(有兩個) 開始時間 結束時間 地址 緯度 經度 花費 照片
for i in range(len(k2[:])):
    if k2[i]['class1'] =='':
        k2[i]['class1'] = k2[i]['class2']
    if k2[i]['charge'] =='':
        k2[i]['charge'] = None
    act.append([k2[i]['actName'],k2[i]['class1'],k2[i]['startTime'],k2[i]['endTime'],k2[i]['address'],k2[i]['longitude'],
                  k2[i]['latitude'],k2[i]['charge'],k2[i]['imageUrl']])


# In[114]:


#將未改變的時間先抓出來並轉呈dataframe
stime1 = []
etime1 = []
for i in range(len(act[:])):
    stime1.append(act[i][2])
    etime1.append(act[i][3])

for i in range(len(stime1[:])):
    struct_time = time.strptime(stime1[i], "%b %d, %Y %H:%M:%S %p") # 轉成時間元組
    stime1[i] = time.strftime("%Y/%m/%d %H:%M:%S", struct_time)
    struct_time = time.strptime(etime1[i], "%b %d, %Y %H:%M:%S %p") # 轉成時間元組
    etime1[i] = time.strftime("%Y/%m/%d %H:%M:%S", struct_time)

stime1 = pd.DataFrame(stime1)
etime1 = pd.DataFrame(etime1)


# In[115]:


#將時間轉換成時間戳記
for i in range(len(act[:])):
    act[i][2] =int(time.mktime(time.strptime(act[i][2], "%b %d, %Y %H:%M:%S %p"))) 
    act[i][3] =int(time.mktime(time.strptime(act[i][3], "%b %d, %Y %H:%M:%S %p"))) 

# timeString=contest[0][3]
# struct_time = time.strptime(timeString, "%Y/%m/%d %H:%M:%S")
# contest[0][3] = int(time.mktime(struct_time)) # 轉成時間戳


# In[116]:


act2 = pd.DataFrame(act)
#act


# In[117]:


act2.columns = ['title', 'class', 'stime', 'etime', 'address', 'lat', 'long', 'fare','img']


# In[118]:


#插入為轉換的時間
act2.insert(9,'stime1',stime1)
act2.insert(10,'etime1',etime1)


# In[119]:


#合併演唱會與藝文活動
Art = pd.concat([contest2, act2], axis=0)


# In[122]:


#mapping 類別，讓她們符合我們的分類
class_mapping = {'01':1, '02':1, '03':1, '04':5, '05':1,
               '06':1, '07':7, '08':1, '11':1, '13':13, '14':14, '15':15, '16':16, '17':1, '19':19}
Art['class'] = Art['class'].map(class_mapping)
#Art


# # 觀光局活動

# In[123]:


'''
觀光局的景點只有xml檔，所以跟文化部的資料擷取方式會不同
這裡取出的都是存成list
'''
f = BytesIO((requests.get("https://gis.taiwan.net.tw/XMLReleaseALL_public/activity_C_f.xml").content))


tree = etree.parse(f)
Name = [t.text for t in tree.xpath("/XML_Head/Infos/Info/Name")]
Category = [t.text for t in tree.xpath("/XML_Head/Infos/Info/Class1")]
Start = [t.text for t in tree.xpath("/XML_Head/Infos/Info/Start")]
End = [t.text for t in tree.xpath("/XML_Head/Infos/Info/End")]
Add = [t.text for t in tree.xpath("/XML_Head/Infos/Info/Add")]
Px = [t.text for t in tree.xpath("/XML_Head/Infos/Info/Px")]
Py = [t.text for t in tree.xpath("/XML_Head/Infos/Info/Py")]
Charge = [t.text for t in tree.xpath("/XML_Head/Infos/Info/Charge")]
Picture1 = [t.text for t in tree.xpath("/XML_Head/Infos/Info/Picture1")]
Start1 = [t.text for t in tree.xpath("/XML_Head/Infos/Info/Start")]
End1 = [t.text for t in tree.xpath("/XML_Head/Infos/Info/End")]
#for a, b, c, d , e, f, g, h, i, j, k  in zip(Name, Category, Start, End, Add, Px, Py,Charge,Picture1, Start1, End1):
#    print(a,b,c,d,e,f,g,h,i, j ,k)


# In[124]:


#轉出的東西是list，這裡把它變成 dic

attri_data1 = {'title': Name,
               'class': Category,
               'stime':Start,
               'etime':End,
               'address':Add,
               'lat': Py,
               'long': Px,
               'fare': Charge,
               'img':Picture1,
               'stime1': Start1,
               'etime1': End1
              }


# In[125]:


#改變時間成為時間戳記

for i in range(len(attri_data1["stime"])):
    #ori_stime = attri_data1['stime'][i]
    
    sbegin = time.strptime(attri_data1['stime'][i], "%Y/%m/%d %H:%M:%S")
    ebegin = time.strptime(attri_data1['etime'][i], "%Y/%m/%d %H:%M:%S")
    
    
    sYear = attri_data1['stime'][i].split(' ')
    eYear = attri_data1['etime'][i].split(' ')
    ########注意時間郵戳是從1970 1/1 8點開始，在此時間之前都會有bug
    if(sYear[0] == '1970/01/01'):
        sbegin = time.strptime('1970/01/01 08:00:00', '%Y/%m/%d %H:%M:%S') 
    if(eYear[0] == '1970/01/01'):
        ebegin = time.strptime('1970/01/01 08:00:00', '%Y/%m/%d %H:%M:%S')
    #######
   
    attri_data1['stime'][i] = int(time.mktime(sbegin)) 
    attri_data1['etime'][i] = int(time.mktime(ebegin))
    
    #attri_data1['stime1'][i] = ori_stime
    #attri_data1['etime1'][i] = ori_stime
       
attri_data_frame1 = DataFrame(attri_data1)


# In[126]:


#改變類別
class_mapping = {'01':1, '1':1,
                 '02':1, '2':1,
                 '03':99,'3':99,  
                 '04':99,'4':99,
                 '05':1, '5':1,
                 '06':5, '6':5,
                 '07':99,'7':99,
                 '08':None,'8': None, 
                 '09':None,'9':None}
attri_data_frame1['class'] = attri_data_frame1['class'].map(class_mapping)
attri_data_frame1.dropna(subset=["class"])
#attri_data_frame1


# # 觀光局景點

# In[127]:


#景點
v = requests.get("https://gis.taiwan.net.tw/XMLReleaseALL_public/scenic_spot_C_f.xml")
xml_bytes_v = v.content
f_v = BytesIO(xml_bytes_v)
tree = etree.parse(f_v)
Name = [t.text for t in tree.xpath("/XML_Head/Infos/Info/Name")]
Category = [t.text for t in tree.xpath("/XML_Head/Infos/Info/Class1")]
Opentime = [t.text for t in tree.xpath("/XML_Head/Infos/Info/Opentime")]
Px = [t.text for t in tree.xpath("/XML_Head/Infos/Info/Px")]
Py = [t.text for t in tree.xpath("/XML_Head/Infos/Info/Py")]
address = [t.text for t in tree.xpath("/XML_Head/Infos/Info/Add")]
Ticketfare = [t.text for t in tree.xpath("/XML_Head/Infos/Info/Ticketinfo")]
#print(type(xml_bytes_v))
#for g, h, i, j, k, l ,m in zip(Name, Category, Opentime, Px, Py, address, Ticketfare):
#    print(g,h,i,j,k, l, m)


# In[128]:


jpg = "https://i0.wp.com/www.funtime.com.tw/blog/wp-content/uploads/2020/01/Skype_Picture_2020_07_16T09_07_32_182Z.jpeg?zoom=1.25&resize=700%2C933"
attri_data2 = {'title': Name,
               'class': Category,
               'stime':Opentime,
               'address':address,
               'lat': Py,
               'long': Px,
               'fare': Ticketfare
              }
attri_data_frame2 = DataFrame(attri_data2)
attri_data_frame2.insert(3, "etime", None)
attri_data_frame2.insert(8, "img", jpg)
attri_data_frame2.insert(9, "stime1", Opentime)
attri_data_frame2.insert(10, "etime1", None)

attri_data_frame2['class'] = attri_data_frame2['class'].astype('string')#注意資料來源為'object',須轉型
#attri_data_frame2


# In[129]:


class_mapping = {'01':1, '1':1,
                 '02':2, '2':2, 
                 '03':2, '3':2, 
                 '04':2, '4':2, 
                 '05':1, '5':1,
                 '06':5, '6':5,
                 '07':2, '7':2,
                 '08':2, '8':2,
                 '09':2, '9':2,
                 '10':5, '11':2, '12':5,
                 '13':None, '14':1, '15':2, '16':2, '17':2, '18':None}
attri_data_frame2['class'] = attri_data_frame2['class'].map(class_mapping)
attri_data_frame2.dropna(subset=["class"])
#attri_data_frame2


# # 合併觀光局的活動和景點

# In[130]:


#前三筆合併
final_art = pd.concat([Art, attri_data_frame1], axis=0)
#這邊要轉成數字float不然後面不能比時間
final_art['stime']= final_art['stime'].astype('float')
final_art['etime']= final_art['etime'].astype('float')
final_art.index = range(len(final_art))
#將類別、經緯度是na的資料drop調
final_art =final_art.dropna(subset=["class","lat","long"])


# In[131]:


# 計算各個行(欄位)裡有多少個“NaN”
#final_art.isna().sum()


# In[133]:


#將還是有缺值得其他部分 fill 0
final_art.fillna(0, inplace = True)
#照片、時間、以及票價，如果要在line上呈現需要轉乘string
final_art['img']= final_art['img'].astype('string')
final_art['stime1']= final_art['stime1'].astype('string')
final_art['etime1']= final_art['etime1'].astype('string')
final_art['fare']= final_art['fare'].astype('string')
final_art.index = range(len(final_art))


# In[134]:


#final_art.info()  


# In[135]:


#儲存成前三csv(因為景點的資料有問題，每筆格式都不太一樣，難以整理，所以最後只讓它顯示出來，不加入表單存取時間的篩選)
#存成csv的壞處是沒有辦法及時更新
final_art.to_csv( '三.csv', index=False )


# In[136]:


#整理景點的資料，經緯度以及其他比照上面
attri_data_frame2['lat']= attri_data_frame2['lat'].astype('float')
attri_data_frame2['long']= attri_data_frame2['long'].astype('float')
attri_data_frame2.fillna(0, inplace = True)
attri_data_frame2['img']= attri_data_frame2['img'].astype('string')
attri_data_frame2['stime1']= attri_data_frame2['stime1'].astype('string')
attri_data_frame2['etime1']= attri_data_frame2['etime1'].astype('string')
attri_data_frame2['fare']= attri_data_frame2['fare'].astype('string')
attri_data_frame2.to_csv( '一.csv'  , index=False )

#儲存成一csv


# In[137]:


#attri_data_frame2.info()


# In[ ]:


'''
注意：
再次提醒存成csv是以後就讀取csv，不用每次都要重新抓資料並且再度跑後台程式
壞處是，需要人工手動更新並且放到上面去
'''

