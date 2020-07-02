import tushare as ts
from datetime import datetime
from stock.models import Stock, Share, DailyBasic


def load_shares_from_api():
    """
    从tushare api获取数据
    """
    current_date = datetime.now().strftime('%Y%m%d')
    # 在日志中记录
    print(current_date)
    pro = ts.pro_api('06f6cd3668a4a60ffa45b3241832010a7a7a577db5ab0f354f4fe785')
    dividend = pro.dividend(ann_date=current_date,
                            fields=['ts_code', 'end_date', 'ann_date', 'div_proc', 'stk_div', 'stk_bo_rate',
                                    'stk_co_rate', 'cash_div', 'cash_div_tax', 'record_date', 'ex_date', 'pay_date',
                                    'div_listdate', 'imp_ann_date', 'base_date', 'base_share'])
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
    daily_basic = daily_basic.where((daily_basic.notna()), None)  # 应该是不存在空值的
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
