import os

import numpy as np

import gensim
from .const import PV, VECTOR

from .models import *


class Vectorizer:
    CAP = 0.6

    def __init__(self, vector_file, stopwords_file, keyword_file):
        print('Init Word Vectorizer')
        self.model = gensim.models.KeyedVectors.load_word2vec_format(vector_file, binary=False)
        self.stop = set([i.strip() for i in open(stopwords_file, "r")])
        print('Model loaded')

        print('Init Keyword Vectorizer')
        if not os.path.exists(keyword_file):
            self.preprocess(keyword_file)

        self.model2 = gensim.models.KeyedVectors.load_word2vec_format(keyword_file, binary=False)
        print('Model loaded')

    def vec(self, word):
        word_list = word.strip().split(' ')
        vec_list = [0, np.zeros(100)]
        for w in word_list:
            if w in self.stop:
                word_list.remove(w)
            else:
                try:
                    vec_list[0] += 1
                    vec_list[1] += self.model[w]
                except KeyError:
                    continue

        return vec_list[1] / vec_list[0] if vec_list[0] else np.zeros(100)

    def preprocess(self, keyword_file):
        print('Starting preprocessing')
        self.result = {}  # keyword: similarity vector
        for counter, keyword in enumerate(Keyword.objects.all()):
            if not counter % 10000:
                print('counter %s' % counter)

            self.result[keyword.keyword] = {
                PV: keyword.pv,
                VECTOR: list(self.vec(keyword.keyword)),
            }

        with open(keyword_file, 'w+') as f:
            f.write('%s 100\n' % len(self.result))
            for r, r_dict in self.result.iteritems():
                f.write('%s %s\n' % (r.replace(' ', '_'), ' '.join(map(str, r_dict[VECTOR]))))

    def word_suggestions(self, word, number_of_returned_suggestion=100):
        suggestions = self.model2.similar_by_vector(self.vec(word), topn=number_of_returned_suggestion)
        suggestions = [ s for s in suggestions if s[1] > self.CAP ]
        return [s[0].replace('_', ' ') for s in suggestions if s[0].replace('_', ' ') != word]
