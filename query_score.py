#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import cv2
import numpy as np
import os
import pytesseract
import requests
import sys
import unittest


is_verbose = False

def eprint(*args, **kwargs):
        print(*args, file=sys.stderr, **kwargs)

def parseCaptcha(s):
    pic_url = "https://jzzjf.12333sh.gov.cn/jzzjf/inc/code.jsp?Math.random();"
    pic = s.get(pic_url)
    image = np.asarray(bytearray(pic.content), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    text = pytesseract.image_to_string(image)
    text = text.replace(' ', '')  # Remove spaces
    if is_verbose:
        print('Captcha:', text)
        # Save it to file for future debug
        filename = "{}.{}.jpg".format(text, os.getpid())
        with open(filename, 'wb') as f:
            f.write(pic.content)
    return text


def parseHtml(s):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(s, 'html.parser')
    for table in soup.findAll('table', attrs={'border': '1'}):
        tr = table.findAll('tr', attrs={'align': 'center'})
        tr = tr[2]
        t = tr.findAll('td')
        if is_verbose:
            print(t)
        idnumber = t[1].text.strip()
        name = t[2].text.strip()
        typeStr = t[3].text.strip()
        result = t[4].text.strip()
        return [name, idnumber, typeStr, result]


def getPassword(p):
    return 'x' * 16 + p + 'x' * 16


def loginAndGetResponse():
    username = os.environ['shjzz_username']
    password = getPassword(os.environ['shjzz_password'])

    login_payload = {
        'username': username,
        'pwd': password,
        'vlidataCode': '',
        'radioCode': 1,
        'Submit': '',
    }

    loading_url = "https://jzzjf.12333sh.gov.cn/jzzjf/"
    login_url = loading_url + "login?dispatch=dologin"

    with requests.session() as s:
        # Login page
        p = s.get(loading_url)
        if is_verbose:
            print(p.text)
        if p.status_code != 200:
            eprint(p)
            raise Exception('Failed to get loading url %s' % (loading_url))

        # Get captcha parse
        text = parseCaptcha(s)
        while (len(text) != 4):
            import time
            eprint('Error parsing a captcha, try another one...')
            eprint(text)
            eprint(" ".join("{:02x}".format(ord(c)) for c in text))
            time.sleep(0.5)
            text = parseCaptcha(s)

        login_payload['vlidataCode'] = text
        if is_verbose:
            print(login_payload)

        p = s.post(login_url, data=login_payload)
        if is_verbose:
            print(p.text)
        if p.status_code != 200:
            eprint(p)
            raise Exception('Failed at login url %s' % (login_url))

        # This system returns 200 even when the captcha is wrong
        if '验证码输入错误' in p.text:
            eprint(p)
            raise Exception('Captcha wrong')
        
        return p.content


def main():
    r = loginAndGetResponse()
    r = parseHtml(r)
    print(r)
    if r is None:
        raise Exception('Failed to query')


class LocalTest(unittest.TestCase):
    def test_getPassword(self):
        r = getPassword('abc')
        # The password encode function is in
        # https://jzzjf.12333sh.gov.cn/jzzjf/pages/resource/js/encode.js
        # It is as stupid as prepend and append 16 random bytes
        print(r)
        self.assertEqual(16 * 2 + len('abc'), len(r))
        self.assertEqual('abc', r[16:-16])

    def test_parser(self):
        with open('sample_score.html', 'rb') as f:
            r = f.read()
            r = parseHtml(r)
            print(r)
            self.assertEqual(4, len(r))
            self.assertEqual('例子', r[0])
            self.assertEqual('123123199001011234', r[1])
            self.assertEqual('(续办)', r[2])
            self.assertEqual('(续办)等待受理', r[3])


def test(exargs):
    unittest.main(argv=sys.argv[:1] + exargs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Query the status of 上海居住证积分')
    parser.add_argument('-q', '--query', action='store_true',
                        help='Query the status of 上海居住证积分')
    parser.add_argument('-t', '--test', action='store_true',
                        help='Run local test')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Print verbose log')

    args, exargs = parser.parse_known_args()
    args = vars(args)

    is_verbose = args['verbose']
    if is_verbose:
        print('Will print verbose log...')
    if args['test']:
        test(exargs)
    elif args['query']:
        main()
    else:
        parser.print_help()
        exit(1)
