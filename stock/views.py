from django.shortcuts import render
from .models import Stock


# Create your views here.

def index(request):
    stocks = Stock.objects.all()
    context = {
        'stocks': stocks
    }
    return render(request, 'stock/index.html', context)


def rank_by_share_times(request):
    """
    效率太低
    """
    stocks = Stock.objects.all()
    # 效率低，3k+次查询
    for stock in stocks:
        stock.times = stock.share_set.filter(div_proc='实施').count()
    stocks = sorted(stocks, key=lambda x: x.times, reverse=True)
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
