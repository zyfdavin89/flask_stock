# coding=utf-8

from flask import make_response
import pymssql
import json
import time
from flask import Flask, render_template
import pandas as pd
import datetime

app = Flask(__name__)


class MSSQL:
    def __init__(self, host, user, pwd, db):
        self.host = host
        self.user = user
        self.pwd = pwd
        self.db = db

    def __getconnect(self):
        """
        得到连接信息
        返回: conn.cursor()
        """
        if not self.db:
            raise (NameError, "没有设置数据库信息")
        self.conn = pymssql.connect(host=self.host, user=self.user, password=self.pwd, database=self.db, charset="utf8")
        cur = self.conn.cursor()
        if not cur:
            raise (NameError, "连接数据库失败")
        else:
            return cur

    def execquery(self, sql):
        """
        执行查询语句
        返回的是一个包含tuple的list，list的元素是记录行，tuple的元素是每行记录的字段

        调用示例：
                ms = MSSQL(host="localhost",user="sa",pwd="123456",db="PythonWeiboStatistics")
                resList = ms.ExecQuery("SELECT id,NickName FROM WeiBoUser")
                for (id,NickName) in resList:
                    print str(id),NickName
        """
        cur = self.__getconnect()
        cur.execute(sql)
        reslist = cur.fetchall()

        # 查询完毕后必须关闭连接
        self.conn.close()
        return reslist


def get_access_control(_json):
    """允许跨域访问"""

    rst = make_response(_json)

    rst.headers['Access-Control-Allow-Origin'] = "*"
    rst.headers['content-type'] = "text/javascript; charset=utf-8"

    return rst


@app.route('/<name>')
def index(name):
    return render_template('index.html', name=name)


@app.route('/stock/<code>')
def stock(code):
    sql_tuple = MSSQL(host="127.0.0.1", user="sa", pwd="windows-999", db="stocks").execquery(
        "select a.date, adjust_price_f from (select * from v_trade_date) a left outer join(select * from stock_data where code = '"+code+"')  b on a.[date] = b.[date] where a.date >= (select top 1 date from stock_data where code = '"+code+"') order by a.date")

    list_stock = []

    stop_price = 0

    for s in sql_tuple:
        if s[1] is not None:
            stop_price = s[1]
        list_date = [
            time.mktime(s[0].timetuple()) * 1000, stop_price]
        list_stock.append(list_date)

    _json = json.dumps(list_stock)

    return get_access_control(_json)


@app.route('/zig/<code>')
def zig(code):
    sql_tuple = MSSQL(host="USER-GH61M1ULCU", user="sa", pwd="windows-999", db="stocks").execquery(
        "SELECT [date],[price] FROM stock_zig WHERE [stock] = '" + code + "' order by date")

    list_stock = []

    for s in sql_tuple:
        list_date = [
            time.mktime(s[0].timetuple()) * 1000, s[1]]
        list_stock.append(list_date)

    _json = json.dumps(list_stock)

    return get_access_control(_json)


@app.route('/buy/<code>')
def buy(code):
    df = pd.read_csv('operate.csv')
    df = df[df['stockcode'] == code]
    df = df[df['operatetype'] == 'buy']

    dic = df.to_dict(orient='index')

    list_stock = []

    for a in dic:
        list_date = [time.mktime(datetime.datetime.strptime(dic[a]['date'], '%Y-%m-%d').timetuple()) * 1000,
                     dic[a]['referenceprice']]
        list_stock.append(list_date)

    _json = json.dumps(list_stock)

    return get_access_control(_json)


@app.route('/sell/<code>')
def sell(code):
    df = pd.read_csv('operate.csv')
    df = df[df['stockcode'] == code]
    df = df[df['operatetype'] == 'sell']

    dic = df.to_dict(orient='index')

    list_stock = []

    for a in dic:
        list_date = [time.mktime(datetime.datetime.strptime(dic[a]['date'], '%Y-%m-%d').timetuple()) * 1000,
                     dic[a]['referenceprice']]
        list_stock.append(list_date)

    _json = json.dumps(list_stock)

    return get_access_control(_json)

if __name__ == '__main__':
    app.run(host='0.0.0.0')

# @todo 增加净值曲线
