import json
import operator
from functools import reduce
from django.db.models import Count, Q, F, Max
from django.http import JsonResponse
from stock.models import Stock, Share, DailyBasic
import datetime
import time


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
        print(search_text)
        shares = shares.filter(Q(ts_code__ts_code__contains=search_text) | Q(ts_code__name__contains=search_text))
    if time_type and start_date and end_date:
        if time_type == 'ann_date':
            shares = shares.filter(ann_date__lte=end_date, ann_date__gte=start_date)
        elif time_type == 'record_date':
            shares = shares.filter(record_date__lte=end_date, record_date__gte=start_date)
        elif time_type == 'imp_ann_date':
            shares = shares.filter(imp_ann_date__lte=end_date, imp_ann_date__gte=start_date)
    if len(proc_filter) != 0:
        shares = shares.filter(reduce(operator.or_, [Q(div_proc__contains=x) for x in proc_filter]))
    shares = shares.exclude(cash_div_tax=0)
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

    data = {
        'total': total,
        'shares': list(shares.values()),
    }
    return JsonResponse(data)


def get_stocks(request):
    """
    根据用户提供的query列表筛选股票，并在每支股票的后面标注share次数
    :return:
    """
    print(request.body)
    queries = json.loads(request.body)['queries']
    stocks = Stock.objects
    for query in queries:
        val = query['val']
        con = query['con']
        years = int(query['years']) if con in ['continues'] else None
        min_num = query['min']
        max_num = query['max']
        # years不为None时，即当类型为累积时
        if years:
            current_year = datetime.datetime.now().year
            for i in range(years):
                # 查询在current year最近一次有数据的日期
                date = DailyBasic.objects.filter(
                    trade_date__lte=str(current_year - i - 1) + '-12-31'
                ).order_by('-trade_date')[1].trade_date
                # 所有符合条件的stocks
                kwargs = {
                    'dailybasic__trade_date': date,
                    'dailybasic__{}__gte'.format(val): min_num,
                    'dailybasic__{}__lte'.format(val): max_num,
                }
                # todo *和**用法
                stocks = stocks.filter(**kwargs)
        else:
            current = datetime.datetime.now()
            date = "{}-{}-{}".format(current.year, current.month, current.day)
            date = DailyBasic.objects.filter(
                trade_date__lte=date
            ).order_by('-trade_date')[1].trade_date
            kwargs = {
                'dailybasic__trade_date': date,
                'dailybasic__{}__gte'.format(val): min_num,
                'dailybasic__{}__lte'.format(val): max_num,
            }
            stocks = stocks.filter(**kwargs)
    stocks = stocks.annotate(
        share_times=Count('share', filter=Q(share__div_proc='实施')),
        # todo 太慢
        # price=Max('dailybasic__close', filter=Q(dailybasic__trade_date='2020-07-10'))
    ).order_by('-share_times')
    data = {
        'stocks': list(stocks.values())
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
    # 在详情页面也排除每股分红为0的记录
    shares = stock[0].share_set.exclude(cash_div_tax=0)
    data = {
        # 'stock': json.loads(serialize('json', (stock,)))[0],
        'stock': list(stock.values())[0],
        # 'shares': json.loads(serialize('json', shares))
        'shares': list(shares.values())
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
    daily_basics = list(daily_basics.values())
    data = {
        'total': total,
        'daily_basics': daily_basics
    }
    return JsonResponse(data)
