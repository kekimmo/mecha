#!/usr/bin/python2.7
# -*- encoding: utf-8 -*-


import mechanize
import re

br = mechanize.Browser()
br.set_handle_robots(False)

br.open("https://www.facebook.com/groups/225187027634779/")
br.select_form(nr=0)
br["email"] = "feikkifeikkila@notmailinator.com"
br["pass"] = "Dah2soqu" 
res = br.submit()

raw_data = res.get_data()
data = raw_data.decode('utf-8')
title = br.title().decode('utf-8').replace(u"\n", u"")
member_count = int(re.search(ur"Jäseniä (\d+)", data).group(1))

fmt = u"\"{:s}\" -yhteisön jäsenmäärä: \2{:d}\2"
print fmt.format(title, member_count).encode('utf-8')

