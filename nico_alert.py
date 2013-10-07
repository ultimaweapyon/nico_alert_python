# coding=utf-8
# Python 2.7.3
# ubuntu 12.04
# ref: http://dic.nicovideo.jp/a/ニコ生アラート(本家)の仕様

import requests
from xml.etree.ElementTree import *
from socket import *
import re

MAIL = u'your email address'
PASS = u'your password'
ANTENNA_URL = u'https://secure.nicovideo.jp/secure/login?site=nicolive_antenna'
STATUS_URL = u'http://live.nicovideo.jp/api/getalertstatus'
PROGRAM_INFO_URL = u'http://live.nicovideo.jp/api/getstreaminfo/lv'
LIVE_URL = u'http://live.nicovideo.jp/watch/'

# * POST送信の応答(XML)をテキストとして返す
def GetLoginXML(url, payload):
	res = requests.post(url, data=payload)
	return fromstring(res.text)

# * 放送が始まったCommunityIDとお気に入りCommunityIDが同じならTrueを返す
def IsFavCom(coid, favcoms):
	for favcom in favcoms:
		if coid == favcom.text:
			return True
	return False

# * 放送内容のXMLを取得する
def GetProgramInfo(lvid):
	res = requests.get(PROGRAM_INFO_URL + lvid)
	return fromstring(res.text.encode('utf_8'))

# * 放送内容を表示する
def DispProgramInfo(stream_info_xml):
	print(u'◆ 放送が開始されました！')
	print(u'コミュニティ名 : ' + stream_info_xml.findtext(u'.//name'))
	print(u'番組タイトル : ' + stream_info_xml.findtext(u'.//title'))
	print(u'放送URL : ' + LIVE_URL + stream_info_xml.findtext(u'.//request_id'))
	print('\n')


print('[Start]')
print(MAIL + '\n')

# == 1. 認証APIその1 ==
res = GetLoginXML(ANTENNA_URL, {u'mail': MAIL, u'password': PASS})
ticket = res.findtext(u'.//ticket')

# == 2. 認証APIその2 ==
res = GetLoginXML(STATUS_URL, {u'ticket': ticket})
user_id = res.findtext(u'.//user_id')
user_name = res.findtext(u'.//user_name')
favcoms = res.findall(u'.//community_id')
host = res.findtext(u'.//addr')
port = res.findtext(u'.//port')
thread =  res.findtext(u'.//thread')

# == 3. コメントサーバー ==
addr = (gethostbyname(host), int(port))  # port needs to be integer
post_data = u'<thread thread="' + thread + '" version="20061206" res_from="-1"/> ' + '\0'  # null is required
sock = socket(AF_INET, SOCK_STREAM)
sock.connect(addr)

while True:
	sock.sendall(post_data)
	msg = sock.recv(4096)

	ids = re.split('[><]', msg)[2]
	if len(ids.split(',')) == 3:
		lvid = ids.split(',')[0]
		coid = ids.split(',')[1]
		usrid = ids.split(',')[2]

		if IsFavCom(coid, favcoms) == True:
			DispProgramInfo(GetProgramInfo(lvid))
