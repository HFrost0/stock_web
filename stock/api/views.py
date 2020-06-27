import json
import time

from django.db.models import Count, Q
from django.http import JsonResponse
from django.core.serializers import serialize
# Create your views here.
from stock.models import Stock, Share


def get_stocks(request):
    stocks = Stock.objects.all()
    data = {
        'stocks': json.loads(serialize('json', stocks)),
    }
    return JsonResponse(data)


def get_recent_shares(request):
    shares = Share.objects.exclude(cash_div_tax=0).order_by('-ann_date')[:100]
    data = {
        'shares': json.loads(serialize('json', shares))
    }
    return JsonResponse(data)


# def get_shares_by_time_point(request):
#     """按照时间点查询，目前最多显示100条，之后可做分页"""
#     if request.method == 'POST':
#         form = TimeForm(request.POST)
#         if form.is_valid():
#             shares = Share.objects.filter(
#                 ann_date__lte=form.data['end_point'],
#                 ann_date__gte=form.data['start_point']
#             ).exclude(cash_div_tax=0).order_by('-ann_date')[:100]
#             context = {
#                 'shares': shares,
#             }
#             return render(request, 'stock/share_list.html', context)
#     return HttpResponseRedirect(reverse('stock:index'))


def rank_by_share_times(request):
    """
    annotate的用法
    """
    stocks = Stock.objects.annotate(
        share_times=Count('share', filter=Q(share__div_proc='实施'))
    ).order_by('-share_times')
    # stocks = sorted(stocks, key=lambda x: x.share_times, reverse=True)
    data = {
        'stocks': json.loads(serialize('json', stocks))
    }
    return JsonResponse(data)


def get_share(request, ts_code):
    stock = Stock.objects.get(pk=ts_code)
    # 在详情页面也排除每股分红为0的记录
    shares = stock.share_set.exclude(cash_div_tax=0)
    data = {
        'stock': json.loads(serialize('json', (stock,)))[0],
        'shares': json.loads(serialize('json', shares))
    }
    return JsonResponse(data)
