from flask import Flask, request, render_template
from pyecharts import options as opts
from pyecharts.charts import Bar,Tab
from pyecharts.charts import Geo
from pyecharts.globals import ChartType

import pymysql
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)


app = Flask(__name__)

#返回一个数据库连接
# Hostname = "127.0.0.1"
# Username = "Port_administrator"
# Password = "Port_administrator"
# db = "Port_information"
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

#进行查询并返回结果results(是个元组)
def Select_Execute(Cursor,Port_Code):
    Cursor.execute("select * from Basic_information natural join Port_Introduce where Port_Code='"+Port_Code+"';")
    results = Cursor.fetchall()

    text_tail=results[0][10]
    ans_text=""
    while len(text_tail)>50:
        ans_text = ans_text+text_tail[:50] + "\n"
        text_tail=text_tail[50:]

    ans_text=ans_text+text_tail
    new_results=results[0][0:10]+(ans_text,)
    NEW_results=()
    NEW_results=NEW_results+(new_results,)
    return NEW_results

#将查询结果修饰并转为字符串
def Select_Text(results):
    results_text=""
    Attr_list=["港口代码：","城市：","港口中文：","港口英文：","国家：","地区：","航线中文：","航线英文","锚地：","类型：","介绍："]
    i=0
    while i<=10:
        results_text=results_text+Attr_list[i]+str(results[0][i])+"\n"
        i = i + 1
    return results_text

#数据统计，传入一个已经连接的数据库，和要分组表里的属性名(Type、Route_Chinese、Country、region)
def Data_grouped(DBConnection,attr_str):
    df = pd.read_sql('SELECT * FROM Basic_information', DBConnection)
    data_grouped = df.groupby(attr_str)['Port_Code'].count()
    return data_grouped

#制作柱状图，传入一个data_grouped和一个属性名(Type、Route_Chinese、Country、region)
def bar_chart(data_grouped,attr_str):
    if attr_str=="Country":
        chart=(
            Bar(init_opts=opts.InitOpts(height="8000px"))
            .add_xaxis(data_grouped.index.tolist())
            .add_yaxis("Port_Number", data_grouped.values.tolist(),bar_width="70%")
            .set_global_opts(title_opts=opts.TitleOpts(title=attr_str + "- Bar Chart"))
            .reversal_axis()
        )
    else:
        chart = (
            Bar()
            .add_xaxis(data_grouped.index.tolist())
            .add_yaxis("Port_Number", data_grouped.values.tolist())
            .set_global_opts(title_opts=opts.TitleOpts(title=attr_str+"- Bar Chart"))
        )
    return chart

def Coordinate_list(Cursor):
    Cursor.execute("select * from Coordinate_view")
    results = Cursor.fetchall()
    return results

def World_Map(results_tuple):
    geo = Geo(init_opts=opts.InitOpts(width="800px", height="600px"))
    geo.add_schema(maptype="world")

    data=[]
    for i in results_tuple:
        string="港口代码："+str(i[4])+"<br>所在城市："+str(i[1])+"<br>纬度："+str(i[2])+"<br>经度："+str(i[3])
        data.append((i[0],string))
        geo.add_coordinate(i[0], i[3], i[2])

    geo.add(
        "",
        data,
        type_=ChartType.EFFECT_SCATTER,
        symbol_size=8,
    )
    geo.set_series_opts(
        label_opts=opts.LabelOpts(is_show=False),
        itemstyle_opts=opts.ItemStyleOpts(color="orange"),
    )
    geo.set_global_opts(
        title_opts=opts.TitleOpts(title="Geo-港口分布图"),
    )
    return geo

#制作表单，传入一个DBConnection
def Tab_chart(DBConnection,Cursor):
    tab=Tab()

    Country_grouped =Data_grouped(DBConnection,"Country")
    Region_grouped = Data_grouped(DBConnection, "Region")
    Route_Chinese_grouped = Data_grouped(DBConnection, "Route_Chinese")
    Type_grouped = Data_grouped(DBConnection, "Type")

    Country_Chart=bar_chart(Country_grouped,"Country")
    Region_Chart=bar_chart(Region_grouped,"Region")
    Route_Chinese_Chart=bar_chart(Route_Chinese_grouped,"Route_Chinese")
    Type_Chart=bar_chart(Type_grouped,"Type")
    World_Map_Chart=World_Map(Coordinate_list(Cursor))

    tab.add(World_Map_Chart, "Coordinates")
    tab.add(Region_Chart, "Region")
    tab.add(Route_Chinese_Chart, "Route_Chinese")
    tab.add(Country_Chart,"Country")
    tab.add(Type_Chart,"Type")

    return tab


DB=DBConnection("127.0.0.1","Port_administrator","Port_administrator","Port_information")
cursor=Create_Cursor(DB)

#下面是一个路由的定义，路由代表 视图函数和URL模式的映射关系。对不同的URL模式（get、post）路由就会调用不同的视图
@app.route("/", methods=["GET", "POST"])
#index()是一个视图函数
def index():
    keyword=""
    text=""
    if request.method == "POST":
        try:
            keyword = request.form.get("keyword")
            results=Select_Execute(cursor,str(keyword))
            text=Select_Text(results)
            chart = Tab_chart(DB,cursor)
        except:
            chart=Tab_chart(DB,cursor)
    else:
        chart=Tab_chart(DB,cursor)
    #render_template是模板渲染，第一个参数是模板的名称，接下来可以接收任意关键字参数
    #模板渲染的本质就是将 模板里面的占位符替换成相应的HTML代码
    # chart.render_embed()自动生成表格的HTML代码
    return render_template("index.html", chart=chart.render_embed(),keyword=keyword,text=text)

if __name__ == "__main__":
    app.run()

