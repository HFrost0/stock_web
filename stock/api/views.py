import json
import operator
import time
from functools import reduce

from dateutil.relativedelta import relativedelta
from django.db.models import Count, Q, F, Max
from django.http import JsonResponse

from stock.api.utils import inner_join, count_current_level
from stock.models import Stock, Share, DailyBasic
import datetime


# Create your views here.


def get_shares(request):
    """
    根据查询条件获取的shares
    :param request:
    :return:
    """
    offset = int(request.GET.get('offset', default=0))
    page_size = int(request.GET.get('page_size', default=10))
    page_num = int(request.GET.get('page_num', default=1))
    prop = request.GET.get('prop', default='ann_date')
    order = request.GET.get('order', default='descending')
    ts_code = request.GET.get('ts_code', default=None)
    time_type = request.GET.get('time_type', default=None)
    start_date = request.GET.get('start_date', default=None)
    end_date = request.GET.get('end_date', default=None)
    proc_filter = request.GET.getlist('proc_filter', default=[])
    search_text = request.GET.get('search_text', default='')
    # 筛选
    shares = Share.objects
    if ts_code:
        shares = shares.filter(ts_code__ts_code=ts_code)
    elif search_text:
        shares = shares.filter(Q(ts_code__ts_code__contains=search_text) | Q(ts_code__name__contains=search_text))
    if time_type and start_date and end_date:
        if time_type == 'ann_date':
            shares = shares.filter(ann_date__lte=end_date, ann_date__gte=start_date)
        elif time_type == 'record_date':
            shares = shares.filter(record_date__lte=end_date, record_date__gte=start_date)
        elif time_type == 'imp_ann_date':
            shares = shares.filter(imp_ann_date__lte=end_date, imp_ann_date__gte=start_date)
    if len(proc_filter) != 0:
        # shares = shares.filter(reduce(operator.or_, [Q(div_proc__contains=x) for x in proc_filter]))
        shares = shares.filter(div_proc__in=proc_filter)
    # 在下面三个字段中全部数值为0则认为该分红信息无效，不发送至前端
    shares = shares.exclude(cash_div_tax=0, cash_div=0, stk_div=0)
    total = shares.count()
    # 字段添加
    shares = shares.annotate(
        name=F('ts_code__name')
    )
    # 排序
    for i in Share._meta.get_fields():
        if prop == i.attname:
            condition = '-' + prop if order == 'descending' else prop
            shares = shares.order_by(condition)
    # 划分
    shares = shares[offset:offset + page_size * page_num]

    fields = [i.attname for i in Share._meta.get_fields()]+['name']
    fields.remove('id')
    data = {
        'total': total,
        'shares': list(shares.values(*fields)),
    }
    return JsonResponse(data)


def get_stocks(request):
    """
    根据用户提供的query列表筛选股票，并在每支股票的后面标注share次数
    :return:
    """
    queries = json.loads(request.body)['queries']
    current = datetime.datetime.now()
    current_date = "{}-{}-{}".format(current.year, current.month, current.day)

    stocks = Stock.objects
    # 在开始时即查询当前daily
    # todo 当数据实时更新后改为实时日期
    current_date = DailyBasic.objects.filter(
        trade_date__lte=current_date,
    ).order_by('-trade_date')[1].trade_date
    current_daily = DailyBasic.objects.filter(
        trade_date=current_date, )
    # 至少含有ts_code_id, close
    val_list = set([i['val'] for i in queries] + ['ts_code_id', 'close'])
    current_daily = list(current_daily.values(*val_list))

    for query in queries:
        val = query['val']
        con = query['con']
        min_num = query['min']
        max_num = query['max']
        # 当类型为累积时，抽取years年末数据
        if con == 'continues':
            # 取出years，如没有直接跳过
            try:
                years = int(query['years'])
            except KeyError:
                print('KeyError')
                continue
            for i in range(years):
                # 查询在current year最近一次有数据的日期
                # todo 该日期显然可能对某些股票来说在该日可能没有数据，这样的股票会被直接筛掉
                date = DailyBasic.objects.filter(
                    trade_date__lte=str(current.year - i - 1) + '-12-31'
                ).order_by('-trade_date')[1].trade_date
                # 所有符合条件的stocks
                kwargs = {
                    'dailybasic__trade_date': date,
                    'dailybasic__{}__gte'.format(val): min_num,
                    'dailybasic__{}__lte'.format(val): max_num,
                }
                # todo *和**用法
                stocks = stocks.filter(**kwargs)
        # 当类型为等级时，查询历史数据
        elif con == 'level':
            # 取出mouths，如没有直接跳过
            try:
                mouths = query['mouths']
            except KeyError:
                print('KeyError')
                continue
            history_daily = DailyBasic.objects.filter(
                trade_date__gte=current_date + relativedelta(months=-mouths),
                trade_date__lt=current_date,
                # 不要用ts_code_id来在daily上进行数据库查询，将极大减慢速度
                # ts_code_id__in=ts_codes
            )
            history_val = list(history_daily.values('ts_code_id', val))
            ts_codes = count_current_level(current_daily, history_val, val, mouths, min_num, max_num)
            # 当前level符合条件的ts_codes进行筛选
            stocks = stocks.filter(ts_code__in=ts_codes)
        # 当类型为当前时，查询最近数据
        elif con == 'current':
            # 如果当前没有数据，直接剔除
            ts_codes = [i['ts_code_id'] for i in current_daily if i[val] and min_num <= i[val] <= max_num]
            stocks = stocks.filter(ts_code__in=ts_codes)
    # 标注分红次数
    stocks = stocks.annotate(
        share_times=Count('share', filter=Q(share__div_proc='实施')),
    )
    # 数组化
    stocks = list(stocks.values('ts_code', 'name', 'area', 'industry', 'list_date', 'share_times'))
    # 连接查询结果
    stocks = list(inner_join(stocks, current_daily))
    data = {
        'stocks': stocks,
    }
    return JsonResponse(data)


def get_stock(request):
    """
    获取当前stock的信息，以及其所有share的信息
    :param request:
    :return:
    """
    ts_code = request.GET.get('ts_code')
    stock = Stock.objects.filter(pk=ts_code)
    data = {
        # 'stock': json.loads(serialize('json', (stock,)))[0],
        'stock': list(stock.values())[0],
    }
    return JsonResponse(data)


def get_daily_basics(request):
    """
    :param request:
    :return:
    """
    ts_code = request.GET.get('ts_code')
    offset = int(request.GET.get('offset', default=0))
    page_size = int(request.GET.get('page_size', default=10))
    page_num = int(request.GET.get('page_num', default=1))
    start_date = request.GET.get('start_date', default=None)
    end_date = request.GET.get('end_date', default=None)
    prop = request.GET.get('prop', default='trade_date')
    order = request.GET.get('order', default='descending')

    daily_basics = DailyBasic.objects.filter(ts_code__ts_code=ts_code)
    # 筛选
    if start_date and end_date:
        daily_basics = daily_basics.filter(trade_date__lte=end_date, trade_date__gte=start_date)
    total = daily_basics.count()
    # 排序
    for i in DailyBasic._meta.get_fields():
        if prop == i.attname:
            condition = '-' + prop if order == 'descending' else prop
            daily_basics = daily_basics.order_by(condition)
    # 划分
    daily_basics = daily_basics[offset:offset + page_size * page_num]
    # 序列化
    fields = [i.attname for i in DailyBasic._meta.get_fields()]
    fields.remove('id')
    daily_basics = list(daily_basics.values(*fields))
    data = {
        'total': total,
        'daily_basics': daily_basics
    }
    return JsonResponse(data)
