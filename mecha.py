#!/usr/bin/python3

import socket
import sys
from threading import Thread

from conf import load_vars


def send_line (s, line):
  print('> ' + line)
  s.sendall(line.encode('utf-8'))
  s.sendall(b'\r\n')


def read_lines (s):
  buf = b''
  while True:
    data = s.recv(1) # Problems if larger
    if not data:
      break
    buf += data
    line_end = buf.find(b'\r\n')
    if line_end != -1:
      yield buf[:line_end].decode('utf-8')
      buf = buf[line_end + 2:]


def parse_msg (line):
  parts = line.split(' ')

  if parts[0][0] == ':':
    prefix = parts[0][1:]
    parts = parts[1:]
  else:
    prefix = None

  command = parts[0]
  if command.isdigit():
    command = int(command)

  params = []
  for i in range(1, len(parts)):
    if parts[i][0] != ':':
      params.append(parts[i])
    else:
      params.append(' '.join(parts[i:]))
      break

  return prefix, command, params

  
def join (s, channel):
  send_line(s, 'JOIN {:s}'.format(channel))


def say (s, target, text):
  send_line(s, 'PRIVMSG {:s} :{:s}'.format(target, text))


def register (s, nick, realname=None):
  if realname is None:
    realname = nick
  send_line(s, 'USER {:s} * * :{:s}'.format(nick, realname))
  send_line(s, 'NICK {:s}'.format(nick))


CONF_VARS = {
    'nick': str,
    'realname': str,
    'target': str,
    'irc_host': str,
    'irc_port': int,
}

CONF_FILE = 'mecha.conf'

conf = load_vars(CONF_VARS, CONF_FILE)

addr = (conf['irc_host'], conf['irc_port'])
s = socket.create_connection(addr)

def irc_to_stdout (s):
  for line in read_lines(s):
    print('<', line)
  
    prefix, cmd, params = parse_msg(line)

    if cmd == 'PING':
      send_line(s, 'PONG :{:s}'.format(params[0]))

def stdin_to_irc (s, target):
  for line in sys.stdin:
    say(s, target, line)

thread = Thread(target=irc_to_stdout, args=(s,))
thread.start()

register(s, conf['nick'])

target = conf['target']
join(s, target)
stdin_to_irc(s, target)

thread.join()
s.close()

