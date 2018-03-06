from .models import *


def load_keywords(file_path):
    data_dict = {}  # keyword : n
    for line in open(file_path, 'r'):
        ls = line.strip().split('\t')

        if len(ls) == 3:
            pv, category, keyword = ls

        if keyword not in data_dict:
            data_dict[keyword] = 0
        data_dict[keyword] += int(pv)

    output = []
    for keyword, pv in data_dict.items():
        output.append(Keyword(keyword=keyword, pv=pv))

    Keyword.objects.bulk_create(output)
