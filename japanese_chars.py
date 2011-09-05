# -*- coding: utf-8 -*-

__version = '0.0.1'

import sys
import re
import pprint
from pymongo import Connection


def main():
    con = Connection('localhost', 27017)
    db = con['ipadic']['all']
    f = open('japanese.txt', 'w')
    chars = set()
    count = 0
    for data in db.find():
        for i in data['word']:
            count += 1
            chars.update(i)

    chars.update([u'a',u'b',u'c',u'd',u'e',u'f',u'g',u'h',u'i',u'j',u'k',u'l',u'm',u'n',u'o',u'p',u'q',u'r',u's',u't',u'u',u'v',u'w',u'x',u'y',u'z'])
    print len(chars)

    for w in sorted(chars):
        f.write(w)

    print count
    f.close()


def pp(obj):
    pp = pprint.PrettyPrinter(indent=4, width=160)
    str = pp.pformat(obj)
    return re.sub(r"\\u([0-9a-f]{4})", lambda x: unichr(int("0x"+x.group(1), 16)),
                  str)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print ('\nGoodbye!')
