#!/usr/bin/python2
# -*- encoding: utf-8 -*-


import urllib
import re
from bs4 import BeautifulSoup


class Listing (object):
    def __init__ (self, soup):
        self.name = soup.find("div", class_="spandesc").find("a").string.strip()
        price_spans = soup.find("div", class_="spanprice").find_all('span')
        price_auction = price_spans[0].find('strong')
        if price_auction is not None:
            price_str = price_auction.string
        else:
            price_str = price_spans[-1].string
        euros, cents = map(int, re.match(ur"(\d+),(\d{2}) €", price_str).groups())
        self.price = 100 * euros + cents


def format_price (as_cents):
    return u'{:d},{:02d} €'.format(as_cents / 100, as_cents % 100)


def odd (integer):
    return integer & 1


def median (values):
    count = len(values)
    if count == 0:
        raise ValueError
    elif count == 1:
        return values[0]
    else:
        sorted_values = sorted(values)
        middle = count / 2
        if odd(count):
            return sorted_values[middle]
        else:
            return round((sorted_values[middle - 1] + sorted_values[middle]) /
                         2.0)


conn = urllib.urlopen("http://www.huuto.net/hakutulos?words=desucon")
if conn.getcode() == 200:
    html = conn.read()
    soup = BeautifulSoup(html)
    itemlist = soup.find(id="listpage").find("div", class_="itemlist")
    items = itemlist.find_all("div", class_="item")
    listings = map(Listing, items)
    prices = [listing.price for listing in listings]

    fmt = u"Rannekeilmoituksia Huuto.netissä: \2{:d}\2, mediaani: \2{:s}\2, maksimi: \2{:s}\2"

    out = fmt.format(len(listings),
                     format_price(int(median(prices))),
                     format_price(max(prices)))
    print out.encode('utf-8')
conn.close()
