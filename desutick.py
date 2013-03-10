#!/usr/bin/python2
# -*- encoding: utf-8 -*-

import mechanize
import re

from conf import load_vars


CONF_FILE = 'desutick.conf'

CONF_VARS = {
    'username': str,
    'password': str,
    'login_uri': str,
    'status_uri': str,
}

conf = load_vars(CONF_VARS, CONF_FILE)

br = mechanize.Browser()

br.open(conf['login_uri'])
br.select_form(nr=0)
br['username'] = conf['username']
br['password'] = conf['password']
response = br.submit()
response = br.open(conf['status_uri'])
html = response.read()

matches = re.search(
  r'<td>Desucon 2013 -ranneke</td>\s*<td class="nc">(\d+)</td>\s*<td class="nc">([0-9.]+)</td>',
  html)

pcs = int(matches.group(1))
money = float(matches.group(2))

print "Rannekkeita tilattu: \2%d\2 (%.2f €)" % (pcs, money)

