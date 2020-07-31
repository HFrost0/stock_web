import time


def inner_join(stocks, current_daily):
    """
    连接stock列表和current daily列表 生成器
    :param stocks:
    :param current_daily:
    :return:
    """
    for r1 in stocks:
        for index, r2 in enumerate(current_daily):
            if r1['ts_code'] == r2['ts_code_id']:
                row = dict((k1, v1) for k1, v1 in r1.items())
                row.update((k2, v2) for k2, v2 in r2.items() if k2 != 'ts_code_id')
                yield row


def count_current_level(current_daily, history_val, val, mouths, min_level=0., max_level=1.):
    """
    在current_daily中添加val的当前水平current_level，并返回在范围之中的ts_codes列表
    格式: current_level-{val}-{mouths}
    :param current_daily:
    :param history_val:
    :param val:
    :param mouths:
    :param min_level:
    :param max_level:
    :return: 符合min和max level值的ts_code列表
    """
    # (day+4)*n复杂
    a = time.time()
    ts_codes = []
    # 字典仅包括当前含有值的
    price_dict = {i['ts_code_id']: i[val] for i in current_daily if i[val]}
    gte_dict = {i['ts_code_id']: 0 for i in current_daily if i[val]}
    total_dict = {i['ts_code_id']: 0 for i in current_daily if i[val]}
    for i in history_val:
        if i['ts_code_id'] in price_dict:
            # history或当前字段为None直接跳过
            if i[val] is not None and i[val] <= price_dict[i['ts_code_id']]:
                gte_dict[i['ts_code_id']] += 1
            total_dict[i['ts_code_id']] += 1
    add_name = 'current_level-{}-{}'.format(val, mouths)
    for i in current_daily:
        # 1. 当前值没有时
        # 2. 当有当前值，但是目标时间范围没有数据时
        if i[val] is None or total_dict[i['ts_code_id']] == 0:
            i[add_name] = None
        else:
            i[add_name] = round(gte_dict[i['ts_code_id']] / total_dict[i['ts_code_id']], 4)
            if min_level <= i[add_name] <= max_level:
                ts_codes.append(i['ts_code_id'])
    b = time.time()
    print('count:', b - a)
    return ts_codes
