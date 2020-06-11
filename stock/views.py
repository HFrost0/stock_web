from django.shortcuts import render
from .models import Stock


# Create your views here.

def index(request):
    stocks = Stock.objects.all()
    context = {
        'stocks': stocks
    }
    return render(request, 'stock/index.html', context)


def get_share(request, ts_code):
    stock = Stock.objects.get(pk=ts_code)
    shares = stock.share_set
    context = {
        'stock': stock,
        'shares': shares
    }
    return render(request, 'stock/detail.html', context)
