from django.db import models
from datetime import datetime
import os


# Create your models here.
# todo load csv方法增加进度条，捕获time zone warning
class Stock(models.Model):
    ts_code = models.CharField('TS代码', max_length=9, primary_key=True)
    symbol = models.CharField('股票代码', max_length=6)
    name = models.CharField('股票名称', max_length=20)
    area = models.CharField('所在地域', max_length=20)
    industry = models.CharField('所属行业', max_length=20)
    list_date = models.DateTimeField('上市日期', )

    def __str__(self):
        return '{}--{}'.format(self.ts_code, self.name)

    @staticmethod
    def load_data_from_csv():
        data_file = r'D:\datasets\stock_data\stock_info.csv'
        stock_list = []
        with open(data_file, encoding='utf-8', mode='r') as f:
            f.readline()
            for line in f:
                info = line.strip().split(',')
                t = datetime.strptime(info[5], '%Y%m%d')
                date = Stock(info[0], info[1], info[2], info[3], info[4], t)
                stock_list.append(date)
        Stock.objects.bulk_create(stock_list)


class Share(models.Model):
    ts_code = models.ForeignKey(Stock, on_delete=models.CASCADE)
    end_date = models.DateTimeField('分红年度', blank=True, null=True)
    ann_date = models.DateTimeField('预案公告日', blank=True, null=True)
    div_proc = models.CharField('实施进度', max_length=20, blank=True, null=True)
    stk_div = models.FloatField('每股送转', blank=True, null=True)
    stk_bo_rate = models.FloatField('每股送转比例', blank=True, null=True)
    stk_co_rate = models.FloatField('每股转增比例', blank=True, null=True)
    cash_div = models.FloatField('每股分红（税后）', blank=True, null=True)
    cash_div_tax = models.FloatField('每股分红（税前）', blank=True, null=True)
    record_date = models.DateTimeField('股权登记日', blank=True, null=True)
    ex_date = models.DateTimeField('除权登记日', blank=True, null=True)
    pay_date = models.DateTimeField('派息日', blank=True, null=True)
    div_listdate = models.DateTimeField('红股上市日', blank=True, null=True)
    imp_ann_date = models.DateTimeField('实施公告日', blank=True, null=True)
    base_date = models.DateTimeField('基准日', blank=True, null=True)
    base_share = models.FloatField('基准股本（万）', blank=True, null=True)

    def __str__(self):
        return '{}--{}'.format(self.ts_code, self.div_proc)

    @staticmethod
    def load_data_from_csv():
        data_dir = r'D:\datasets\stock_data\share'
        stocks = Stock.objects.all()
        for file in os.listdir(data_dir):
            with open(os.path.join(data_dir, file), encoding='utf-8', mode='r') as f:
                f.readline()
                share_list = []
                stock = stocks.get(pk=file[:-4])
                for line in f:
                    info = line.strip().split(',')
                    for i in (1, 2, 9, 10, 11, 12, 13, 14):
                        info[i] = datetime.strptime(info[i], '%Y%m%d') if info[i] else None
                    for i in (4, 5, 6, 7, 8, 15):
                        info[i] = float(info[i]) if info[i] else None
                    s = Share(
                        ts_code=stock,
                        end_date=info[1], ann_date=info[2], div_proc=info[3], stk_div=info[4], stk_bo_rate=info[5],
                        stk_co_rate=info[6], cash_div=info[7], cash_div_tax=info[8], record_date=info[9],
                        ex_date=info[10], pay_date=info[11], div_listdate=info[12], imp_ann_date=info[13],
                        base_date=info[14], base_share=info[15]
                    )
                    share_list.append(s)
                Share.objects.bulk_create(share_list)


class DailyBasic(models.Model):
    ts_code = models.ForeignKey(Stock, on_delete=models.CASCADE)
    trade_date = models.DateTimeField('交易日期', blank=True, null=True)
    close = models.FloatField('收盘价', blank=True, null=True)
    turnover_rate = models.FloatField('换手率(%)', blank=True, null=True)
    turnover_rate_f = models.FloatField('换手率(自由流通股)', blank=True, null=True)
    volume_ratio = models.FloatField('量比', blank=True, null=True)
    pe = models.FloatField('市盈率', blank=True, null=True)
    pe_ttm = models.FloatField('市盈率(TTM)', blank=True, null=True)
    pb = models.FloatField('市净率', blank=True, null=True)
    ps = models.FloatField('市销率', blank=True, null=True)
    ps_ttm = models.FloatField('市销率(TTM)', blank=True, null=True)
    dv_ratio = models.FloatField('股息率(%)', blank=True, null=True)
    dv_ttm = models.FloatField('股息率(TTM)', blank=True, null=True)
    total_share = models.FloatField('总股本(万股)', blank=True, null=True)
    float_share = models.FloatField('流通股本(万股)', blank=True, null=True)
    free_share = models.FloatField('自由流通股本(万股)', blank=True, null=True)
    total_mv = models.FloatField('总市值(万元)', blank=True, null=True)
    circ_mv = models.FloatField('流通市值(万元)', blank=True, null=True)

    def __str__(self):
        return '{}--{}'.format(self.ts_code, self.trade_date)

    @staticmethod
    def load_data_from_csv():
        data_dir = r'D:\datasets\stock_data\daily_basic'
        stocks = Stock.objects.all()
        for file in os.listdir(data_dir):
            with open(os.path.join(data_dir, file), encoding='utf-8', mode='r') as f:
                f.readline()
                daily_basic_list = []
                try:
                    stock = stocks.get(pk=file[:-4])
                except:
                    print('this stock info not exist')
                else:
                    for line in f:
                        info = line.strip().split(',')
                        info[1] = datetime.strptime(info[1], '%Y%m%d') if info[1] else None
                        for i in range(2, 18):
                            info[i] = float(info[i]) if info[i] else None
                        d = DailyBasic(
                            ts_code=stock,
                            trade_date=info[1], close=info[2], turnover_rate=info[3], turnover_rate_f=info[4],
                            volume_ratio=info[5], pe=info[6], pe_ttm=info[7], pb=info[8], ps=info[9],
                            ps_ttm=info[10], dv_ratio=info[11], dv_ttm=info[12], total_share=info[13],
                            float_share=info[14], free_share=info[15], total_mv=info[16], circ_mv=info[17]
                        )
                        daily_basic_list.append(d)
                    DailyBasic.objects.bulk_create(daily_basic_list)

