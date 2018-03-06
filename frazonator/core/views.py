# -*- coding: utf-8 -*-
# author: Krystian Dowolski (krystian.dowolski@dealavo.com)

import unicodedata
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from core.vectorizer import Vectorizer

from .models import *

### HELPERS ###

vectorizer = Vectorizer('core/vectors.txt', 'core/stopwords.txt', 'core/keywords_vectors.txt')

def error_page(request, text):
    return render(request, 'core/main_page.html', {'err': text})

def strip_accents(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn').replace(u'ł', 'l')

### VIEWS ###

def main_page(request):
    if request.method == 'POST':
        q = request.POST.get('q')
        if q:
            return redirect('results', keyword=q)
        else:
            return error_page(request, 'Przykro nam, nie jesteśmy w stanie Ci pomóc, dopóki nie podasz frazy :(')

    return render(request, 'core/main_page.html')

def results(request, keyword):
    org_keyword = keyword
    keyword = strip_accents(keyword).lower()
    suggestions = vectorizer.word_suggestions(keyword, 1000)

    # create two queries:
    # - q1: accurate, but possibly boring (overlapping words)
    # - q2: less accurate, but not overlaping query
    q1 = suggestions[:100]
    q2 = [s for s in suggestions if not set(keyword.split()) & set(s.split())]
    q = list(set(q1 + q2))
    keywords = Keyword.objects.filter(keyword__in=q, pv__gte=250).order_by('-pv')

    # check if there is enough proposed keywords and original keyword exists
    try:
         Keyword.objects.get(keyword=keyword)
    except Keyword.DoesNotExist:
        return error_page(request, 'Ta fraza występuje tak rzadko, że odstąpimy ją za darmo.')
    if len(keywords) < 5:
        return error_page(request, 'Drogi użytkowniku, w trosce o Twoje samopoczucie postanowiliśmy nie przedstawiać Ci znalezionych fraz, gdyż nie uznaliśmy ich za satysfakcjonujące.')
    
    # calc monthly pv estimate based on weekly counts
    keywords = [Keyword(keyword=k.keyword, pv=k.pv * 4) for k in keywords]
    pv = Keyword.objects.get(keyword=keyword).pv
    pv_ext = sum([k.pv for k in keywords])
    pv_div = int(float(pv_ext) / pv * 100)

    return render(
        request,
        'core/result.html',
        {
            'keywords': keywords, 'pv': pv, 'pv_ext': pv_ext, 'pv_div': pv_div, 'keyword': org_keyword
        }
    )
