import operator
from functools import reduce
from django.db.models import Count, Q, F
from django.http import JsonResponse
from stock.models import Stock, Share


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
    # 筛选
    shares = Share.objects
    if ts_code:
        shares = Share.objects.filter(ts_code__ts_code=ts_code)
    if time_type and start_date and end_date:
        if time_type == 'ann_date':
            shares = shares.filter(ann_date__lte=end_date, ann_date__gte=start_date)
        elif time_type == 'record_date':
            shares = shares.filter(record_date__lte=end_date, record_date__gte=start_date)
    if len(proc_filter) != 0:
        shares = shares.filter(reduce(operator.or_, [Q(div_proc__contains=x) for x in proc_filter]))
    shares = shares.exclude(cash_div_tax=0)
    total = shares.count()
    # 排序
    for i in Share._meta.get_fields():
        if prop == i.attname:
            condition = '-' + prop if order == 'descending' else prop
            shares = shares.order_by(condition)
    # 划分
    shares = shares[offset:offset + page_size * page_num]
    # 获得name
    stock_names = [i.ts_code.name for i in shares]
    # 序列化
    shares = list(shares.values())
    for index, i in enumerate(shares):
        i['name'] = stock_names[index]

    data = {
        'total': total,
        'shares': shares,
    }
    return JsonResponse(data)


def get_stocks(request):
    """
    获取stock列表，并在每支股票后标注share次数
    :param request:
    :return:
    """
    stocks = Stock.objects.annotate(
        share_times=Count('share', filter=Q(share__div_proc='实施'))
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


def get_daily_basic(request):
    """
    :param request:
    :return:
    """
    # 点击股票列表处某个股票代码
    ts_code = request.GET.get('ts_code')
    # 分页
    offset = int(request.GET.get('offset', default=0))
    page_size = int(request.GET.get('page_size', default=10))
    page_num = int(request.GET.get('page_num', default=1))
    # 类似地，可以提供按交易日期范围进行筛选
    start_date = request.GET.get('start_date', default=None)
    end_date = request.GET.get('end_date', default=None)
    # 可以不做排序好像没啥意义
    # prop = request.GET.get('prop', default='trade_date')
    # order = request.GET.get('order', default='descending')

    # 获得个股ts_code历史每日指标
    daily_basic = Stock.objects.get(pk=ts_code).dailybasic_set.all()
    # daily_basic = DailyBasic.objects.filter(ts_code__ts_code=ts_code)

    if start_date and end_date:
        daily_basic = daily_basic.filter(trade_date__lte=end_date, trade_date__gte=start_date)
    total = daily_basic.count()  # 历史每日指标数据数量

    # 划分
    daily_basic = daily_basic[offset:offset + page_size * page_num]
    daily_basic = list(daily_basic.values())
    data = {
        'total': total,
        'daily': daily_basic
    }
    return JsonResponse(data)
