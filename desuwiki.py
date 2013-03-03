#!/usr/bin/python3
# -*- encoding: utf-8 -*-


import simplemediawiki
import sys

from conf import load_vars


def get_recent_changes (wiki, rcstart=None):
  query = {
    'action': 'query',
    'list': 'recentchanges',
    'rcdir': 'newer',
    'rcprop': 'user|title|ids|timestamp',
    'rvdiffto': 'prev',
    'rctype': 'edit|new',
    }

  if rcstart is not None:
    query['rcstart'] = rcstart

  changes = []
  while True:
    reply = wiki.call(query)
    changes += reply['query']['recentchanges']
    if 'query-continue' in reply:
      query.update(reply['query-continue']['recentchanges'])
    else:
      break

  return changes


def load_state (filename):
  STATE_VARS = {
      'last_timestamp': str,
      'last_revid': int,
  }
  return load_vars(STATE_VARS, filename)


def save_state (filename, state):
  f = open(filename, 'w')
  for var, value in state.items():
    f.write('{:s}: {:s}\n'.format(var, str(value)))


def get_changes (conf, state_file, state_override={}):
  state = load_state(state_file)
  state.update(state_override)

  uri_api = conf['uri_base'] + '/api.php'

  w = simplemediawiki.MediaWiki(uri_api)
  w.login(conf['username'], conf['password'])

  changes = get_recent_changes(w, state['last_timestamp'])

  if state['last_revid'] is not None:
    changes = [c for c in changes if c['revid'] > state['last_revid']]

  if changes:
    last_change = changes[-1]
    state['last_revid'] = last_change['revid']
    state['last_timestamp'] = last_change['timestamp']

  save_state(STATE_FILE, state)

  return changes


def changes_by_page_id (changes):
  res = {}
  for change in changes:
    id = change['pageid']
    if id not in res:
      res[id] = []
    res[id].append(change)
  return res


def page_uri (uri_base, title):
  return '{:s}/{:s}'.format(uri_base, title)


def diff_uri (uri_base, title, prev, cur):
  return '{:s}/index.php?title={:s}&diff={:d}&oldid={:d}'.format(
      uri_base, title, cur, prev)


def format_page_changes (uri_base, changes):
  if not changes:
    return '<?>'
  
  title = changes[-1]['title']

  new_page = (changes[0]['type'] == 'new')

  if new_page:
    msg = '{:s}: uusi sivu <{:s}>'.format(title, page_uri(uri_base, title))
  else:
    diff_prev = changes[0]['old_revid']
    diff_cur = changes[-1]['revid']
    uri = diff_uri(uri_base, title, diff_prev, diff_cur)
    count = len(changes)
    msg = '{:s}: {:d} muokkaus{:s} <{:s}>'.format(
        title, count, '' if count == 1 else 'ta', uri)
  return msg


def format_changes (uri_base, changes):
  for page_id, page_changes in changes_by_page_id(changes).items():
    page_title = page_changes[0]['title']
    yield format_page_changes(conf['uri_base'], page_changes) 


CONF_FILE = 'desuwiki.conf'
STATE_FILE = 'desuwiki.state'

CONF_VARS = {
    'uri_base': str,
    'username': str,
    'password': str,
}

conf = load_vars(CONF_VARS, CONF_FILE)

#changes = get_changes(conf, STATE_FILE, state_override={
#  'last_timestamp': '2013-03-02T16:00:00Z', 'last_revid': 0})
changes = get_changes(conf, STATE_FILE)

print('\n'.join(format_changes(conf['uri_base'], changes)))

