#!/usr/bin/python3
# -*- coding: utf-8 -*-

import socket
import os
import sys
from threading import Thread
import time

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
      line_data = buf[:line_end]
      buf = buf[line_end + 2:]
      try:
        yield line_data.decode('utf-8')
      except UnicodeDecodeError:
        yield line_data.decode('iso-8859-15')


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
    if parts[i] and parts[i][0] != ':':
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


def irc_to_stdout (s):
  for line in read_lines(s):
    print('<', line)
  
    prefix, cmd, params = parse_msg(line)

    if cmd == 'PING':
      send_line(s, 'PONG :{:s}'.format(params[0]))


def file_to_irc (f, s):
  GAP = 2
  last_sent = 0
  for line in f:
    if not line:
      line = ' '
    wait = last_sent + GAP - time.time()
    if wait > 0:
      time.sleep(wait)
    say(s, target, line)
    last_sent = time.time()


CONF_VARS = {
    'nick': str,
    'realname': str,
    'target': str,
    'irc_host': str,
    'irc_port': int,
    'pid_file': str,
    'fifo_file': str,
}

CONF_FILE = 'mecha.conf'

conf = load_vars(CONF_VARS, CONF_FILE)

pid_file = conf['pid_file']

try:
  with open(pid_file, 'x') as f:
    f.write('{:d}\n'.format(os.getpid()))
except FileExistsError:
  print('PID file exists at {:s}.\nNot running.'.format(pid_file),
      file=sys.stderr)
  sys.exit(1)

fifo = conf['fifo_file']

try:
  addr = (conf['irc_host'], conf['irc_port'])
  s = socket.create_connection(addr)

  thread = Thread(target=irc_to_stdout, args=(s,))
  thread.daemon = True
  thread.start()

  register(s, conf['nick'])

  target = conf['target']
  join(s, target)

  os.mkfifo(fifo)
  while True:
    with open(fifo, 'r') as f:
      file_to_irc(f, s)
except:
  print('Stopping: {:s}'.format(sys.exc_info()[0]), file=sys.stderr)
finally:
  s.close()
  os.remove(pid_file)
  os.remove(fifo)

