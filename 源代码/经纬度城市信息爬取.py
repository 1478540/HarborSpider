

from bs4 import BeautifulSoup
import re
import requests
import pymysql

def Requests_Querry(url,headers,str_code):
    response = requests.get(url, headers)
    response.encoding = str_code
    return response

def Analysis_Data(response):
    soup=BeautifulSoup(response.text,'lxml')
    div = soup.find('div', {'class': 'blogpost-body blogpost-body-html'})
    if div:
        table = div.find('table')
        if table:
            tr_list = []
            rows = table.find_all('tr')
            for row in rows:
                columns = row.find_all('td')
                td_list = []
                for column in columns:
                    td_list.append(column.text)
                tr_list.append(td_list)
    return tr_list

def dms_to_dd(dms_str):
    dms_str = dms_str.strip()
    sign = -1 if dms_str.startswith(('南', '西')) else 1
    dms_str = dms_str[2:].replace(':', '')

    parts = dms_str.split('°')
    try:
        degrees = float(parts[0])
    except:
        degrees=0
    try:
        minutes = float(parts[1].split("'")[0])
    except:
        minutes=0
    dd = sign * (degrees + minutes / 60)
    return dd

def Conversion_Coordinate(Coordinate_list):
    New_Coordinate_list = []
    for i in Coordinate_list:
        if i:
            latitude_float = dms_to_dd(i[3])
            longitude_float = dms_to_dd(i[4])
            New_Coordinate_list.append([i[0], latitude_float, longitude_float])
    return New_Coordinate_list

def DBConnection(Hostname,Username,Password,db):
    try:
        DBConnection = pymysql.connect(host=Hostname, user=Username, password=Password, db=db)
        print("Connected to MySQL database successfully!")
    except pymysql.Error as e:
        print(f"Error connecting to MySQL database: {e}")
    return DBConnection

#返回一个数据库游标
def Create_Cursor(DBConnection):
    return DBConnection.cursor()


def Insert_Execute(Cursor,list):
    try:
        sql="INSERT INTO City_Coordinates VALUES (%s, %s, %s)"
        val=(list[0],list[1],list[2])
        Cursor.execute(sql,val)
    except pymysql.err.IntegrityError as e:
        print(e)


if __name__ =="__main__":
    url = "https://www.cnblogs.com/haibin-zhang/p/4955880.html"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.63"
    }
    response=Requests_Querry(url,headers,"UTF-8")
    Coordinate_list=Analysis_Data(response)
    print(Coordinate_list)

    New_Coordinate_list=Conversion_Coordinate(Coordinate_list)
    print(New_Coordinate_list)

    Hostname = "127.0.0.1"
    Username = "Port_administrator"
    Password = "Port_administrator"
    db = "Port_information"
    DB=DBConnection(Hostname,Username,Password,db)
    cursor=Create_Cursor(DB)
    for i in New_Coordinate_list:
        Insert_Execute(cursor,i)
        DB.commit()
    DB.close()





