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
    pic_url = "https://jzh.12333sh.gov.cn/jzh/image.jsp?Math.random();"
    pic = s.get(pic_url)
    image = np.asarray(bytearray(pic.content), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    text = pytesseract.image_to_string(image)
    text.replace(" ", "")  # Remove spaces
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
    for td in soup.findAll('td', attrs={'class': 'td_bg'}):
        if is_verbose:
            print(td)
        t = td.findAll('td', attrs={'align': 'center'})
        idnumber = t[2].text.strip()
        name = t[3].text.strip()
        result = t[5].text.strip()
        return [name, idnumber, result]


def getUsername(u):
    import hashlib
    # The site use md5(bin(username)) as the user name
    str_bytes = str.encode(u)
    m = hashlib.md5(str_bytes)
    if is_verbose:
        print('MD5 username: %s' % (m.hexdigest()))
    return m.hexdigest()


def loginAndGetResponse():
    username = getUsername(os.environ['shjzh_username'])
    password = os.environ['shjzh_password']

    login_payload = {
        'loginInfo.login_username': username,
        'loginInfo.login_password': password,
        'loginInfo.login_type': 0,
        'Rand': '',
        'radioCode': 1,
    }

    accept_payload = {
        'username': username,
        'Button': '我接受'
    }

    loading_url = "https://jzh.12333sh.gov.cn/jzh/"
    login_url = "https://jzh.12333sh.gov.cn/jzh/userLoginAction!login.action"
    accept_url = "https://jzh.12333sh.gov.cn/jzh/userLoginAction!LoginPerson.action"
    myinfo_url = "https://jzh.12333sh.gov.cn/jzh/personInfoAction!myInfo.action"

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
            time.sleep(0.5)
            text = parseCaptcha(s)

        login_payload['Rand'] = text
        if is_verbose:
            print(login_payload)

        p = s.post(login_url, data=login_payload)
        if is_verbose:
            print(p.text)
        if p.status_code != 200:
            eprint(p)
            raise Exception('Failed at login url %s' % (login_url))

        # Press Accept button
        p = s.post(accept_url, data=accept_payload)
        if is_verbose:
            print(p.text)
        if p.status_code != 200:
            eprint(p)
            raise Exception('Failed at accept url %s' % (accept_url))

        p = s.get(myinfo_url)
        if is_verbose:
            print(p.text)
        if p.status_code != 200:
            eprint(p)
            raise Exception('Failed at myinfo url %s' % (myinfo_url))
        return p.content


def main():
    r = loginAndGetResponse()
    r = parseHtml(r)
    print(r)


class LocalTest(unittest.TestCase):
    def test_getUserName(self):
        r = getUsername('abc')
        # This is the test in md5.js in the site
        self.assertEqual('900150983cd24fb0d6963f7d28e17f72', r)

    def test_parser(self):
        with open('sample.html', 'rb') as f:
            r = f.read()
            r = parseHtml(r)
            self.assertEqual(3, len(r))
            self.assertEqual('例子', r[0])
            self.assertEqual('123123199001011234', r[1])
            self.assertEqual('受理通过', r[2])
            print(r)


def test(exargs):
    unittest.main(argv=sys.argv[:1] + exargs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Query the status of 上海居转户')
    parser.add_argument('-q', '--query', action='store_true',
                        help='Query the status of 上海居转户')
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
