from django.db.models import Count, Q
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .forms import TimeForm
from .models import Stock, Share


# Create your views here.

def index(request):
    stocks = Stock.objects.all()
    form = TimeForm()
    context = {
        'stocks': stocks,
        'form': form
    }
    return render(request, 'stock/index.html', context)


def recent_shares(request):
    """# 按照预案公告日排序，取前100，代做分页"""
    # shares = Share.objects.exclude(cash_div_tax=0).order_by('-ann_date')[:100]
    # 方便测试，暂时不进行筛选
    shares = Share.objects.order_by('-ann_date')[:100]
    context = {
        'shares': shares
    }
    return render(request, 'stock/share_list.html', context)


def get_shares_by_time_point(request):
    """按照时间点查询，目前最多显示100条，之后可做分页"""
    if request.method == 'POST':
        form = TimeForm(request.POST)
        if form.is_valid():
            shares = Share.objects.filter(
                ann_date__lte=form.data['end_point'],
                ann_date__gte=form.data['start_point']
            ).exclude(cash_div_tax=0).order_by('-ann_date')[:100]
            context = {
                'shares': shares,
            }
            return render(request, 'stock/share_list.html', context)
    return HttpResponseRedirect(reverse('stock:index'))


def rank_by_share_times(request):
    """
    annotate的用法
    """
    stocks = Stock.objects.annotate(
        share_times=Count('share', filter=Q(share__div_proc='实施'))
    ).order_by('-share_times')
    # stocks = sorted(stocks, key=lambda x: x.share_times, reverse=True)
    context = {
        'stocks': stocks
    }
    return render(request, 'stock/share_times_rank.html', context)


def get_share(request, ts_code):
    stock = Stock.objects.get(pk=ts_code)
    # 在详情页面也排除每股分红为0的记录
    shares = stock.share_set.exclude(cash_div_tax=0)
    context = {
        'stock': stock,
        'shares': shares
    }
    return render(request, 'stock/detail.html', context)
