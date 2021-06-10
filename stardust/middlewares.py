import json
from urllib import parse
import base64
from flask import request, session

from .auth import Auth, jwt_serializer

# 检查 token 是否有效，并且提供错误信息
class TokenAuth(Auth):

	def make_before_request(self):
		def before():
			if not self.is_white_route():
				try:
					jwt_serializer.loads(request.headers.get('Authorization'))
				except Exception:
					return { 'code': 10001, 'err': '请重新登录' }
		return before


# 检查是否已登录，不然返回，并且提供错误信息
class SessionAuth(Auth):

	def make_before_request(self):
		def before():
			if not self.is_white_route():
				if not session.get('has_logined'):
					return { 'code': 10001, 'err': '请重新登录' }
		return before


# 解码 post put 参数
class DecryptForm:

	def __init__(self, app=None):
		self.app = app
		if app is not None:
			self.app = app
			self.init_app(app)

	def init_app(self, app):
		before = self.make_before_request()
		app.before_request(before)

	def make_before_request(self):
		def before():
			if request.method == 'POST' or request.method == 'PUT':
				text = str(request.data.decode('utf-8'))
				text = [char for char in text]
				text.reverse()
				text = ''.join(text)
				text = parse.unquote(base64.b64decode(text).decode('utf-8'))
				text = [char for char in text]
				text.reverse()
				text = ''.join(text)
				request.data = text.encode()
		return before
