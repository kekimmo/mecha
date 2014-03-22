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

kinds = {
    'PDF-lippuja'           : "Desucon Frostbite 2014 PDF -lippu",
    'Postitettavia lippuja' : "Desucon Frostbite 2014 - postitettava lippu",
}


info = {}
total_pcs = 0
total_money = 0

for kind, name in kinds.iteritems():
  match_str = r'<td>{:s}</td>\s*<td class="nc">(\d+)</td>\s*<td class="nc">([0-9.]+)</td>'.format(name)
  matches = re.search(match_str, html)
  pcs = int(matches.group(1))
  money = float(matches.group(2))
  total_pcs += pcs
  total_money += money

print "Lippuja tilattu: \2%d\2 (%.2f €)" % (total_pcs, total_money)

