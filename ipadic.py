# -*- coding: utf-8 -*-

__version = '0.0.1'

import sys
import re
import pprint
from collections import defaultdict
from pymongo import Connection

kana_token = re.compile(u"([\w]+|[ぁ-ゔ]+|[ァ-ヺ]+|[一-龠]+|[ーヽヾ〆々]+)")


def main():
    con = Connection('localhost', 27017)
    db = con['ipadic']['all']
    inserted_db = con['ipadic']['bigrams']
    ngram = {}
    for data in db.find():
        for i in ngrams(''.join([w for w in unicode(data['word']) if kana_token.search(w)])):
            ngram.setdefault(i, []).append(data['word'])

    for i,w in ngram.items():
        inserted_db.insert({u"ngram":i, u"words":list(set(w))})


def pp(obj):
    pp = pprint.PrettyPrinter(indent=4, width=160)
    str = pp.pformat(obj)
    return re.sub(r"\\u([0-9a-f]{4})", lambda x: unichr(int("0x"+x.group(1), 16)),
                  str)


def ngrams(string, n=2):
    for i in range(len(string) - (n-1)):
        yield string[i:i+n]


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print ('\nGoodbye!')
