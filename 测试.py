from collections import defaultdict

l1 = [{"index": 1, "b": 2}, {"index": 2, "b": 3}, {"index": 3, "green": "eggs"}]
l2 = [{"index": 1, "c": 4}, {"index": 2, "c": 5}]

d = defaultdict(dict)
for l in (l1, l2):
    for elem in l:
        d[elem['index']].update(elem)
l3 = d.values()
#############################
