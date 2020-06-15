from django.db.models import Count, Q
from django.shortcuts import render
from .models import Stock, Share


# Create your views here.

def index(request):
    stocks = Stock.objects.all()
    context = {
        'stocks': stocks
    }
    return render(request, 'stock/index.html', context)


def recent_shares(request):
    shares = Share.objects.order_by('-ann_date')[:500]
    context = {
        'shares': shares
    }
    return render(request, 'stock/share_list.html', context)


def rank_by_share_times(request):
    """
    annotate的用法
    """
    stocks = Stock.objects.annotate(
        share_times=Count('share', filter=Q(share__div_proc='实施'))
    )
    stocks = sorted(stocks, key=lambda x: x.share_times, reverse=True)
    context = {
        'stocks': stocks
    }
    return render(request, 'stock/share_times_rank.html', context)


def get_share(request, ts_code):
    stock = Stock.objects.get(pk=ts_code)
    shares = stock.share_set
    context = {
        'stock': stock,
        'shares': shares
    }
    return render(request, 'stock/detail.html', context)
