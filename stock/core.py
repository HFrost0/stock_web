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
    print(current_date, 'shares')
    pro = ts.pro_api('06f6cd3668a4a60ffa45b3241832010a7a7a577db5ab0f354f4fe785')
    fields = ('ts_code', 'end_date', 'ann_date', 'div_proc',
              'stk_div', 'stk_bo_rate', 'stk_co_rate', 'cash_div',
              'cash_div_tax', 'record_date', 'ex_date', 'pay_date',
              'div_listdate', 'imp_ann_date', 'base_date', 'base_share')

    # 设空dividend合并
    dividend = pd.DataFrame(columns=fields)
    # 前溯一周
    for delta in range(8):
        current_date = (datetime.now() - dt.timedelta(days=delta)).strftime('%Y%m%d')
        # 以预案公告日前溯
        div_ann = pro.dividend(ann_date=current_date, fields=fields)
        # 以实施公告日前溯
        div_imp = pro.dividend(imp_ann_date=current_date, fields=fields)
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
            share[1][0] = stock
            kwargs = {fields[index]: i for index, i in enumerate(share[1])}
            Share.objects.get_or_create(**kwargs)


def load_daily_basics_from_api():
    """
    从Tushare获取daily basic数据
    :return:
    """
    current_date = datetime.now().strftime('%Y%m%d')
    # 在日志中记录
    print(current_date, 'daily record')
    pro = ts.pro_api('06f6cd3668a4a60ffa45b3241832010a7a7a577db5ab0f354f4fe785')
    fields = ['ts_code', 'trade_date', 'close', 'turnover_rate',
              'turnover_rate_f', 'volume_ratio', 'pe', 'pe_ttm', 'pb', 'ps',
              'ps_ttm', 'dv_ratio', 'dv_ttm', 'total_share', 'float_share',
              'free_share', 'total_mv', 'circ_mv']
    daily_basic = pro.daily_basic(ts_code='', trade_date=current_date, fields=fields)
    daily_basic = daily_basic.where((daily_basic.notna()), None)  # 应该是不存在空值的
    for daily in daily_basic.iterrows():
        try:
            stock = Stock.objects.get(pk=daily[1]['ts_code'])
        except:
            print('stock error', daily[1]['ts_code'])
        else:
            daily[1][0] = stock
            daily[1][1] = datetime.strptime(daily[1][1], '%Y%m%d')  # trade_date
            kwargs = {fields[index]: i for index, i in enumerate(daily[1])}
            # todo 可以bulk create
            DailyBasic.objects.get_or_create(**kwargs)
