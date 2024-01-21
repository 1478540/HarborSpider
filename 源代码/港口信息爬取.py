import requests
import pymysql
from bs4 import BeautifulSoup



if __name__=="__main__":
    count = 1#用与记录爬取的国家数
    Hostname="127.0.0.1"
    Username="Port_administrator"
    Password="Port_administrator"
    db="Port_information"
    try:
        DBConnection=pymysql.connect(host=Hostname, user=Username, password=Password, db=db)
        print("Connected to MySQL database successfully!")
    except pymysql.Error as e:
        print(f"Error connecting to MySQL database: {e}")


    url="http://gangkou.00cha.net/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.57"
    }
    #为什么这个地方只能用位置传参?
    response=requests.get(url,headers)
    response.encoding="gb2312"
    soup=BeautifulSoup(response.text,'lxml')

    A_list=soup.find_all('a')
    country_list=[]
    for i in A_list:
        if 'gj_' in i["href"]:
            country_list.append(i["href"])

    #country_list存储着每一个国家的查询后缀

    for i in country_list:
        new_url=url+i
        response=requests.get(new_url,headers)
        response.encoding = "gb2312"
        soup = BeautifulSoup(response.text, 'lxml')

        A_list=soup.find_all('a')
        port_list=[]
        for j in A_list:
            if 'gk_' in j["href"]:
                port_list.append(j["href"])
        #port_list存储着一个国家内每一个港口的查询后缀

        for k in port_list:
            new_url=url+k
            response=requests.get(new_url,headers)
            if response.status_code==404:
                continue
            response.encoding="gb2312"
            soup=BeautifulSoup(response.text,'lxml')

            tr_list=[]
            for tr in soup.find_all('tr'):
                td_list=[]
                for td in tr.find_all('td'):
                    text = td.text.replace("\u3000",'').replace('\xa0', ' ')
                    td_list.append(text)
                tr_list.append(td_list)
            #tr_list[]这个二维数组就存储一个港口的所有信息了

            introduce=[]
            introduce.append([tr_list[0][1]])
            for goal_div in soup.find_all('div', class_='bei lh'):
                if '港口介绍' in goal_div.text:
                    introduce.append([goal_div.text.replace('\xa0', ' ').replace('\n','').replace('\r','\r')])
                    break

            if len(introduce) < 2:
                introduce.append([""])
            #intrduce列表里有两个元素，第一个元素是港口的代码，第二个元素是该港口的介绍


           #print(tr_list[0][1],tr_list[0][3],tr_list[1][1],tr_list[1][3],tr_list[2][1],tr_list[2][3],tr_list[3][1],tr_list[3][3],tr_list[4][1],tr_list[4][3])


            #将捕获的数据插入到MySQL
            cursor = DBConnection.cursor()
            sql1 = "INSERT INTO Basic_information(Port_Code,City,Port_Chinese,Port_English,Country,Region,Route_Chinese,Route_English,Anchorage,Type) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            val1 = (tr_list[0][1],tr_list[0][3],tr_list[1][1],tr_list[1][3],tr_list[2][1],tr_list[2][3],tr_list[3][1],tr_list[3][3],tr_list[4][1],tr_list[4][3])
            sql2="INSERT INTO Port_Introduce(Port_Code,introduce) VALUES (%s, %s)"
            val2=(introduce[0],introduce[1])
            try:
                cursor.execute(sql1, val1)
                cursor.execute(sql2,val2)
            except pymysql.err.IntegrityError as err:
                print(err)

        #每插入完一个国家的所有港口数据，便进行一次事物提交
        DBConnection.commit()
        print("插入完第"+str(count)+"个国家的所有港口数据")
        count=count+1

    DBConnection.close()



