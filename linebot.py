#!/usr/bin/env python
# coding: utf-8

# In[1]:


#flask line bot 
from flask import Flask
app = Flask(__name__)
from flask import Flask, request, abort
from linebot import  LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import ImageSendMessage, MessageEvent, TextSendMessage, TextMessage, MessageTemplateAction, ButtonsTemplate,LocationMessage, LocationSendMessage,LocationAction,TemplateSendMessage,URITemplateAction, QuickReply, QuickReplyButton



#資料結構模組
import numpy as np
import scipy as sp
from pandas import Series, DataFrame
import pandas as pd
from sklearn.utils import shuffle

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


# In[2]:


line_bot_api = LineBotApi('b6y8VTNiQP64KhlPbnDcThDxE8nlANSv24zIByWJHuIEFadkA9Xuf1YfzN8D6UNkoEGHIDdHJU7CUQV1WLWwd5+yshKv5LidrGEC643UDhrwMNawmLulQMHogNfcsgHOLMoNYXU3LifOkEEkzzdVmAdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('0afc32a47a632b5e89f9a6d8d6ea8cb3')#使用者channel secret


# In[3]:


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
'''
如果傳送的是@傳送位置，則讓他展開quick ryply 並且讓它定位自己的位置
如果是其他的，就跳出template 並且讓他選擇填寫表單或者傳送位置
'''
def handle_message(event):
    mtext = event.message.text
    if mtext == '@傳送地點':
        message =  TextSendMessage(
                text='請按位置，展開之後再點選定位',
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=LocationAction(label="位置")
                        ),
                    ]))
        '''
        event 輸出是這樣
        event.message.latitude
        event.message.longitude
        (這裡是指收到使用者傳送位置的訊息解析是如此)
        '''
        line_bot_api.reply_message(event.reply_token, message)
    else:
        message=TemplateSendMessage(
                    alt_text='Buttons template',
                    template=ButtonsTemplate(
                        title='注意!!!!!!',
                        text='請先填寫表單，之後再按傳送地點',
                        actions=[
                            URITemplateAction(
                                label='填寫表單',
                                uri='https://forms.gle/7g67kpWdL2i9PBLv6'
                            ),
                            MessageTemplateAction(
                                label='傳送地點',
                                text ='@傳送地點'
                            )
                        ]
                    )
                )

        line_bot_api.reply_message(event.reply_token,message)    




@handler.add(MessageEvent, message=LocationMessage)
def handle_location_message(event):
    #讀取憑證碼的json檔
    gc = pygsheets.authorize(service_account_file='kidowefinal.json')

    # 輸入要更改的Googles Sheets網址（也可直接用 Google Sheets 的 ID ）
    survey_url = 'https://docs.google.com/spreadsheets/d/16qef0PrpEfGJoRiCi8Amus0LY5VNIWyfr80hE8Qg6vg/edit#gid=619117859'

    # 開啟該Google sheets
    sh = gc.open_by_url(survey_url)
    ws = sh.worksheet_by_title('DataCollect')
    #轉乘dataframe
    df = ws.get_as_df(start='A', index_colum=0, empty_value='', include_tailing_empty=False) # index 從 1 開始算
    
    #更動sheet的時間(這裡只有抓最新一筆的資料做整理)
    if '下午' in df.iloc[-1,0]:
        df.iloc[-1,0] = df.iloc[-1,0].replace('下午','PM')
        df.iloc[-1,0] =int(time.mktime(time.strptime(df.iloc[-1,0], "%Y/%m/%d %p %H:%M:%S")))
    elif '上午' in df.iloc[-1,0]:
        df.iloc[-1,0] = df.iloc[-1,0].replace('上午','AM')
        df.iloc[-1,0] =int(time.mktime(time.strptime(df.iloc[-1,0], "%Y/%m/%d %p %H:%M:%S")))
    else:
        df.iloc[-1,0] =int(time.mktime(time.strptime(df.iloc[-1,0], "%Y/%m/%d %p %H:%M:%S")))
    
    '''
    sheet 順序 性別 #年齡 #居住地 #教育 工作 月收入 是否結婚
    模型順序 age education job marriage income residence gender
    注意：這裡時間戳記把它弄於最後了
    '''
    df = df.reindex(columns=['您的年齡區間是?','您的教育學齡? (台灣教育學制為標準)',
                         '您的工作類別是?','您的婚姻狀況是?','您的月收入區間是?',
                         '您個人目前所居住縣市?','您的性別是?','時間戳記'])
    '''
    東西要丟入模型並且得到output
    '''
    #抓出最新一筆的 -1是不想抓到時間戳記
    a = []
    for i in range(df.shape[1]-1):
        a.append(int(df.iloc[-1,i][0]))
    q = DataFrame(a)
    q=q.T
    q.columns =  ['age','education','job','marriage','income','residence','gender']
    
    purpose = model(q)
    '''
    output 部分
    '''    
    #讀取三個的csv
    final_art =pd.read_csv('三.csv')  

    
    #篩選時間(這邊就只有可篩選時間的被drop)
    d3 = df.iloc[-1,7]
    final_art = final_art[(final_art['stime'] <= d3) & (final_art['etime'] >= d3)]
    #將篩選時間之後的final 與景點再度合併
    attri_data_frame2 =pd.read_csv('一.csv')
    final_art = pd.concat([final_art, attri_data_frame2], axis=0)
    final_art =final_art.dropna(subset=["class","lat","long"])
    
    #特定條件下的output
    final_art = final_art.loc[(final_art['class'] == purpose ) | (final_art['class'] == 99)]
    final_art.fillna(0, inplace = True)
    '''
    下面這兩個雖然在data中已經處理乾淨，但是難保有問題，所以讓他們再跑一次
    這邊是把經緯度轉型
    '''
    final_art['lat']= final_art['lat'].astype('float')
    final_art['long']= final_art['long'].astype('float')
    '''
    這裡把票價、estime1 stime1  img轉成文字
    '''
    final_art['img']= final_art['img'].astype('string')
    final_art['stime1']= final_art['stime1'].astype('string')
    final_art['etime1']= final_art['etime1'].astype('string')
    final_art['fare']= final_art['fare'].astype('string')
    final_art.index = range(len(final_art))
    '''
    這裡是連結google的距離
    建立一個for迴圈 篩選可以 就繼續執行下面
    '''
    #隨機suffle
    final_art = shuffle(final_art)
    for i in range(len(final_art[:])):
        d = haversine((event.message.latitude, event.message.longitude),(final_art.iloc[i,5], final_art.iloc[i,6]))
        if d <= 10:
            t = final_art.iloc[i][7]
            stime = final_art.iloc[i][9]
            etime = final_art.iloc[i][10]
            img = final_art.iloc[i][8]
            message = [LocationSendMessage(
                                title= final_art.iloc[i][0],
                                address = final_art.iloc[i][4],
                                latitude = final_art.iloc[i][5],
                                longitude = final_art.iloc[i][6]),
                       TextSendMessage(#傳送文字
                            text = "票價:"+t),
                       TextSendMessage(#傳送文字
                             text = "開始時間:"+stime),
                       TextSendMessage(#傳送文字
                            text = "結束時間:"+etime),
                       ImageSendMessage(
                            original_content_url = img,
                            preview_image_url = img)
                      ]

            line_bot_api.reply_message(
                            event.reply_token,message)


# In[4]:


#這邊要想模型
def model(n):    
    '''
    打開匯入模型
    然後print出數字
    '''
    forest = joblib.load("RForest0221.plk")
    output_label = forest.predict(n)
    
    return output_label[0]


# In[ ]:


if __name__ == '__main__':
    app.run()


# In[ ]:





# In[ ]:




