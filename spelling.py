#! /usr/bin/python
# -*- coding: utf-8 -*-

__version__ = '1.0.3'
import sys
import re
import unicodedata
import pprint
from collections import defaultdict
from pymongo import Connection
from pymongo import ASCENDING, DESCENDING

kana_token = re.compile(u"([\w]+|[ぁ-ゔ]+|[ァ-ヺ]+|[一-龠]+|[ーヽヾ〆々]+)")
japanese   = unicode(open('japaneses.txt').read())


def ngrams(string, n=2):
    for i in range(len(string) - (n-1)):
        yield string[i:i+n]


def spell_check(word, db):
    finded = defaultdict(int)
    for i in ngrams(word):
        for j in db.find({u'ngram': unicode(i)}):
            for m in j['words']:
                finded[m] += 1
    return finded


def lsDustance(word):
    word = unicode(word)
    n = len(word)
    return set([word[:i]+word[i+1:] for i in range(n)] +                       # deletion
               [word[:i]+word[i+1]+word[i]+word[i+2:] for i in range(n-1)] +  # transposition
               [word[:i]+c+word[i+1:] for i in range(n) for c in japanese] +   # alteration
               [word[:i]+c+word[i:] for i in range(n+1) for c in japanese])    # insertion


def known_edits2(word, nwords):
    nwords = map(unicode, nwords)
    return set([e2 for e1 in lsDustance(word) for e2 in lsDustance(e1) if e2 in nwords])


def known_edits1(word, nwords):
    nwords = map(unicode, nwords)
    print [w for w in lsDustance(word) if w in nwords]
    return set([w for w in lsDustance(word) if w in nwords])


def main(words):

    try:
        con = Connection("localhost")
        known_words = con['ipadic']['all']
        known_words.create_index([(u"word", ASCENDING)])
        db = con['ipadic']['bigrams']
        db.create_index([(u"ngram", ASCENDING)])
    except Extension, e:
        sys.exit(e)

    count = 0
    normal = unicodedata.normalize('NFKC', unicode(words)).encode('utf-8')
    for word in normal.split():
        jp_chars = ''.join([w for w in unicode(word) if kana_token.search(w)])
        if [w for w in known_words.find({"word": jp_chars})]:
            count += 1
            break
        miss = biggest(spell_check(jp_chars, db))
        if miss:
            ## print "修正候補 :\n" +pp(miss)+ "\n"
            candidates = known_edits1(jp_chars, miss.keys()) or miss.keys() or [word]
            return min(candidates, key=lambda w: [j['cost'] for j in known_words.find({"word": w})])
        else:
            count += 1
    if count == len(normal.split()):
        return None
    else:
        pass


def biggest(seq):
    if len(seq) < 1:
        return seq
    big = max(seq.values())
    results = {}
    for i,n in seq.items():
        if n == big:
            results[i] = n
    return results


def pp(obj):
    """ 日本語を文字コードではなく日本語で表示する Python2.x用 """

    pp = pprint.PrettyPrinter(indent=4, width=160)
    str = pp.pformat(obj)
    return re.sub(r"\\u([0-9a-f]{4})", lambda x: unichr(int("0x"+x.group(1), 16)),
                  str)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        word = sys.argv[1]
    else:
        sys.exit("Please enter the word!\n")
    w = main(word)
    if w:
        print ("もしかすると：" +w+ "\n")
    else:
        print ("Not Spellmiss!!\n")
