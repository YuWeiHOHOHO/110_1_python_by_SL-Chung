import eel
import speech_recognition
from pypinyin import pinyin
import pymysql

orderlist=[] #儲存已點餐點(購物車)

#==================================eel libraries=============================================
@eel.expose
def recommendation_system():
    db = pymysql.connect(host="localhost",user="root",password="password",database="meal_list")
    cursor = db.cursor()
    sql = """SELECT meal,amount FROM order_meal"""
    cursor.execute(sql)
    result =  cursor.fetchall()

    item = {"漢堡":0,"炸雞":0,"可樂":0,"玉米濃湯":0,"茶":0,"沙拉":0,"冰淇淋":0,"雞塊":0,"薯條":0}
    top1 = 0
    top2 = 0
    top3 = 0
    for i in range(len(result)):
        item[result[i][0]] = item[result[i][0]] + result[i][1]

    print(item)
    #===================取前3=======================================================
    item_amount_list = list(item.values())
    item_meal_list = list(item.keys())
    print(item_amount_list)
    for x in range(len(item_amount_list)):
        b = x+1
        for y in range(b,len(item_amount_list)):
            if item_amount_list[x] > item_amount_list[y] and item_amount_list[x] > top1:
                top1 = item_amount_list[x]
                
    item_amount_list.remove(top1)

    for x in range(len(item_amount_list)):
        b = x+1
        for y in range(b,len(item_amount_list)):
            if item_amount_list[x] > item_amount_list[y] and item_amount_list[x] > top2:
                top2 = item_amount_list[x]
                
    item_amount_list.remove(top2)            

    for x in range(len(item_amount_list)):
        b = x+1
        for y in range(b,len(item_amount_list)):
            if item_amount_list[x] > item_amount_list[y] and item_amount_list[x] > top3:
                top3 = item_amount_list[x]
    #========================================================================================
    ticket = False
    for key,value in item.items():
        if value == top1 and ticket == False:
            top1_meal = key
            ticket = True
        if value == top2 :
            top2_meal = key
        if value == top3 :
            top3_meal = key  
    db.commit()
    return f"當季推薦餐點 第一名：{top1_meal}，第二名：{top2_meal}，第三名：{top3_meal}"  

@eel.expose
def add_order(order): #新增餐點 order格式為"餐點：數量"(eg:漢堡：1)
    item=order.split("：",1)
    item[1]=int(item[1])
    
    #若orderlist內已有餐點就更新數量，沒有就新增餐點
    for i in range(len(orderlist)):
        if item[0]==orderlist[i][0]:
            orderlist[i][1]=orderlist[i][1]+item[1]
            print(orderlist)
            return f'您的訂單已加入購物車'
    
    orderlist.append(item)
    print(orderlist)
    return f'您的訂單已加入購物車'        
            
@eel.expose
def now_order(): #print出orderlist以及目前的總金額
    ordered_price = {"漢堡":80,"炸雞":100,"可樂":20,"玉米濃湯":30,"茶":20,"沙拉":35,"冰淇淋":15,"雞塊":30,"薯條":35}
    text="目前餐點："
    price=0
    for item in orderlist:
        text=text+item[0]+str(item[1])+'份  '
        price=price+ordered_price[item[0]]*item[1]
    text=text+'總共'+str(price)+'元'
    return text    

@eel.expose
def order_meal():#語音點餐
    number_list = [['yī'],[1],['liǎng'],[2],['sān'],['3'],['sì'],['4'],['wǔ'],['5']] #數量的拼音
    food_list = [['hàn'],['zhà'],['kě'],['yù'],['chá'],['shā'],['bīng'],['jǐ'],['shǔ']] #餐點拼音，只有第一個字的音查詢
    food_wholename = ["漢堡","炸雞","可樂","玉米濃湯","茶","沙拉","冰淇淋","雞塊","薯條"] #餐點全名
   
    #語音點餐
    r = speech_recognition.Recognizer()
    with speech_recognition.Microphone() as source:
        print("Wait 2 sec. and Order please!")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source,timeout=20)
    item = r.recognize_google(audio,language="zh-TW")
    count = list()
    count = pinyin(item)
    
    #進行語音判讀，這裡的程式有一個缺點，就是使用者一定要先說數量再說商品才讀的到，且只能點最多五份
    food="" #餐點
    num=0 #數量
    for i in range(len(count)) :
        if count[i] in number_list: #判斷是不是數字
            for amount,number_pinyin in enumerate(number_list):
                if count[i] == number_pinyin : #判斷數量再設定範圍內(5份)
                    
                    #判斷品項
                    for food_index,food_pinyin in enumerate(food_list) : #count[i+2]抓食品第一字
                            if count[i+2] == food_pinyin :
                                food=food_wholename[food_index]
                    
                    num=int(amount/2)+1 #判斷數量                   
                    
            return(food+"："+str(num)) #若有找到餐點及回報    
    return("點餐錯誤，請再說一次")


@eel.expose
def finished(): #完成點餐，將餐點存入資料庫，資料庫名稱為meal_list，表格名稱為order_meal
    db = pymysql.connect(host="localhost",user="root",password="password",database="meal_list")
    cursor = db.cursor()
    
    for item in orderlist:
        sql = "SELECT * FROM `meal_list`.`order_meal` WHERE meal = '"+ item[0] + "'"
        cursor.execute(sql)
        data = cursor.fetchone()
        if data == None: #若無餐點就新增
            print('查無餐點')
            sql = "Insert into `meal_list`.`order_meal`(`meal`,`amount`) values ('" + item[0] + "','"+str(item[1])+"')"
            cursor.execute(sql)
            db.commit()
        else: #若有餐點就修改數量
            print('已有餐點')
            num=int(data[2])+item[1]
            sql = "UPDATE `meal_list`.`order_meal` SET amount="+ str(num)+" WHERE meal='"+item[0]+"'"
            cursor.execute(sql)
            db.commit()
    #完成後重置購物車        
    orderlist.clear()

@eel.expose
def reset():
    orderlist.clear()    

#====================================================================================================

#執行程式
eel.init('webside')
eel.start('main.html', size=(800,800))
