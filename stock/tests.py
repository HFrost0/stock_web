from datetime import datetime
import tushare as ts
from django.test import TestCase
from stock.models import Stock, Share, DailyBasic
from stock_web.settings import TS_TOKEN

pro = ts.pro_api(TS_TOKEN)


def to_file(years):
    """将最近years年的每年最后一天的daily basic放入文件缓存"""
    current_year = datetime.now().year
    dates = []
    for i in range(years):
        date = DailyBasic.objects.filter(
            trade_date__lte=str(current_year - i - 1) + '-12-31'
        ).order_by('-trade_date')[1].trade_date
        dates.append(date)
    with open('dates.csv', mode='w') as f:
        f.write(','.join([str(date) for date in dates]))


# Create your tests here.
def test_shares_api(ann_date):
    dividend = pro.dividend(ann_date=ann_date,
                            fields=['ts_code', 'end_date', 'ann_date', 'div_proc', 'stk_div', 'stk_bo_rate',
                                    'stk_co_rate', 'cash_div', 'cash_div_tax', 'record_date', 'ex_date',
                                    'pay_date',
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
                stk_bo_rate=share[1][5], stk_co_rate=share[1][6], cash_div=share[1][7],
                cash_div_tax=share[1][8],
                record_date=share[1][9], ex_date=share[1][10], pay_date=share[1][11], div_listdate=share[1][12],
                imp_ann_date=share[1][13], base_date=share[1][14], base_share=share[1][15]
            )


# Create your tests here.
def test_shares_api0(imp_ann_date):
    dividend = pro.dividend(imp_ann_date=imp_ann_date,
                            fields=['ts_code', 'end_date', 'ann_date', 'div_proc', 'stk_div', 'stk_bo_rate',
                                    'stk_co_rate', 'cash_div', 'cash_div_tax', 'record_date', 'ex_date',
                                    'pay_date',
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
                stk_bo_rate=share[1][5], stk_co_rate=share[1][6], cash_div=share[1][7],
                cash_div_tax=share[1][8],
                record_date=share[1][9], ex_date=share[1][10], pay_date=share[1][11], div_listdate=share[1][12],
                imp_ann_date=share[1][13], base_date=share[1][14], base_share=share[1][15]
            )


def test_daily_basics_api(current_date):
    fields = ['ts_code', 'trade_date', 'close', 'turnover_rate',
              'turnover_rate_f', 'volume_ratio', 'pe', 'pe_ttm', 'pb', 'ps',
              'ps_ttm', 'dv_ratio', 'dv_ttm', 'total_share', 'float_share',
              'free_share', 'total_mv', 'circ_mv']
    daily_basic = pro.daily_basic(ts_code='', trade_date=current_date, fields=fields)
    daily_basic = daily_basic.where((daily_basic.notna()), None)  # 应该是不存在空值的
    daily_basic_list = []
    for daily in daily_basic.iterrows():
        try:
            stock = Stock.objects.get(pk=daily[1]['ts_code'])
        except:
            print('stock error', daily[1]['ts_code'])
        else:
            daily[1][0] = stock
            daily[1][1] = datetime.strptime(daily[1][1], '%Y%m%d')  # trade_date
            kwargs = {fields[index]: i for index, i in enumerate(daily[1])}
            d = DailyBasic(**kwargs)
            daily_basic_list.append(d)
    DailyBasic.objects.bulk_create(daily_basic_list)


class HelloTest(TestCase):
    def test_api(self):
        test_daily_basics_api('20200710')
