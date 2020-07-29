import tushare as ts
import pandas as pd
from datetime import datetime
import datetime as dt
from stock.models import Stock, Share, DailyBasic


def load_shares_from_api():
    """
    从tushare api获取数据
    """
    current_date = datetime.now().strftime('%Y%m%d')
    # 在日志中记录
    print(current_date)
    # pro = ts.pro_api('06f6cd3668a4a60ffa45b3241832010a7a7a577db5ab0f354f4fe785')
    # dividend = pro.dividend(ann_date=current_date,
    #                         fields=['ts_code', 'end_date', 'ann_date', 'div_proc', 'stk_div', 'stk_bo_rate',
    #                                 'stk_co_rate', 'cash_div', 'cash_div_tax', 'record_date', 'ex_date', 'pay_date',
    #                                 'div_listdate', 'imp_ann_date', 'base_date', 'base_share'])
    pro = ts.pro_api('06f6cd3668a4a60ffa45b3241832010a7a7a577db5ab0f354f4fe785')

    # 设空dividend合并
    dividend = pd.DataFrame(columns=('ts_code', 'end_date', 'ann_date', 'div_proc',
                              'stk_div', 'stk_bo_rate', 'stk_co_rate', 'cash_div',
                              'cash_div_tax', 'record_date', 'ex_date', 'pay_date',
                              'div_listdate', 'imp_ann_date', 'base_date', 'base_share'))
    # 前溯一周
    for delta in range(8):
        up_date = (datetime.now()-dt.timedelta(days=delta)).strftime('%Y%m%d')
        # 以预案公告日前溯
        div_ann = pro.dividend(ann_date=up_date,
                                fields=['ts_code', 'end_date', 'ann_date', 'div_proc', 'stk_div', 'stk_bo_rate',
                                        'stk_co_rate', 'cash_div', 'cash_div_tax', 'record_date', 'ex_date', 'pay_date',
                                        'div_listdate', 'imp_ann_date', 'base_date', 'base_share'])
        # 以实施公告日前溯
        div_imp = pro.dividend(imp_ann_date=up_date,
                               fields=['ts_code', 'end_date', 'ann_date', 'div_proc', 'stk_div', 'stk_bo_rate',
                                       'stk_co_rate', 'cash_div', 'cash_div_tax', 'record_date', 'ex_date', 'pay_date',
                                       'div_listdate', 'imp_ann_date', 'base_date', 'base_share'])
        dividend = pd.concat([dividend, div_ann, div_imp], axis=0)

    dividend = dividend.where((dividend.notna()), None)
    for share in dividend.iterrows():
        try:
            stock = Stock.objects.get(pk=share[1]['ts_code'])
        except:
            print('stock error', share[1]['ts_code'])
        else:
            for i in (1, 2, 9, 10, 11, 12, 13, 14):
                share[1][i] = datetime.strptime(share[1][i], '%Y%m%d') if share[1][i] else None
            Share.objects.get_or_create(
                ts_code=stock,
                end_date=share[1][1], ann_date=share[1][2], div_proc=share[1][3], stk_div=share[1][4],
                stk_bo_rate=share[1][5], stk_co_rate=share[1][6], cash_div=share[1][7], cash_div_tax=share[1][8],
                record_date=share[1][9], ex_date=share[1][10], pay_date=share[1][11], div_listdate=share[1][12],
                imp_ann_date=share[1][13], base_date=share[1][14], base_share=share[1][15]
            )


def load_daily_basics_from_api():
    """
    从Tushare获取daily basic数据
    :return:
    """
    current_date = datetime.now().strftime('%Y%m%d')
    # 在日志中记录
    print(current_date + 'daily record')
    pro = ts.pro_api('06f6cd3668a4a60ffa45b3241832010a7a7a577db5ab0f354f4fe785')
    daily_basic = pro.daily_basic(ts_code='', trade_date=current_date,
                                  fields=['ts_code', 'trade_date', 'close', 'turnover_rate',
                                          'turnover_rate_f', 'volume_ratio', 'pe', 'pe_ttm', 'pb', 'ps',
                                          'ps_ttm', 'dv_ratio', 'dv_ttm', 'total_share', 'float_share',
                                          'free_share', 'total_mv', 'circ_mv'])
    daily_basic = daily_basic.where(daily_basic.notna(), None)
    for daily in daily_basic.iterrows():
        try:
            stock = Stock.objects.get(pk=daily[1]['ts_code'])
        except:
            print('stock error', daily[1]['ts_code'])
        else:
            daily[1][1] = datetime.strptime(daily[1][1], '%Y%m%d')  # trade_date
            DailyBasic.objects.get_or_create(ts_code=stock,
                                             trade_date=daily[1][1], close=daily[1][2], turnover_rate=daily[1][3],
                                             turnover_rate_f=daily[1][4], volume_ratio=daily[1][5], pe=daily[1][6],
                                             pe_ttm=daily[1][7], pb=daily[1][8], ps=daily[1][9],
                                             ps_ttm=daily[1][10],
                                             dv_ratio=daily[1][11], dv_ttm=daily[1][12], total_share=daily[1][13],
                                             float_share=daily[1][14], free_share=daily[1][15],
                                             total_mv=daily[1][16],
                                             circ_mv=daily[1][17])

import MySQLdb # todo pip install mysqlclient，注意连接端口等匹配
def create_or_replace_dailyView():
    # connect() 方法用于创建数据库的连接，里面可以指定参数：用户名，密码，主机等信息。
    # 这只是连接到了数据库，要想操作数据库需要创建游标。
    conn = MySQLdb.connect(
        host='localhost',
        port=3307,
        user='root',
        passwd='123456',
        db='stock_web',
    )
    # 时间为某天零点前8小时
    trade_date = (datetime.now() - dt.timedelta(days=1)).strftime('%Y-%m-%d') + ' 16:00:00'
    # 通过获取到的数据库连接conn下的cursor()方法来创建游标。
    cur = conn.cursor()

    # 通过游标cur 操作execute()方法可以写入纯sql语句。通过execute()方法中写如sql语句来对数据进行操作
    sql = "CREATE OR REPLACE VIEW stock_DailyBasicView AS" \
          " SELECT row_number() OVER () as id, sd.ts_code_id, sd.trade_date," \
          " sd.close, sd.turnover_rate, sd.turnover_rate_f, sd.volume_ratio," \
          " sd.pe, sd.pe_ttm, sd.pb, sd.ps, sd.ps_ttm, sd.dv_ratio, sd.dv_ttm," \
          " sd.total_share, sd.float_share,sd.free_share, sd.total_mv, sd.circ_mv" \
          " FROM stock_dailybasic sd " \
          "WHERE sd.trade_date = '%s';" %(trade_date)
    try:
        # 执行sql语句
        cur.execute(sql)
        # 提交到数据库执行
        conn.commit()
    except:
        # 发生错误时回滚
        conn.rollback()
    # cur.close() 关闭游标
    cur.close()
    # conn.close()关闭数据库连接
    conn.close()
