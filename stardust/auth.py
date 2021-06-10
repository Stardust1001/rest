from flask import request, session
from itsdangerous import TimedJSONWebSignatureSerializer

jwt_serializer = TimedJSONWebSignatureSerializer('flask-restful-token', 86400)


class Auth:

	def __init__(self, app=None, includes=(), excludes=()):
		self.app = app
		self.includes = includes
		self.excludes = excludes
		if app is not None:
			self.app = app
			self.init_app(app)

	def init_app(self, app):
		before = self.make_before_request()
		app.before_request(before)

	def is_white_route(self):
		route_path = request.url[len(request.host_url) - 1:]
		is_white = True
		for item in self.includes:
			if route_path.startswith(item):
				is_white = False
		if not is_white:
			for item in self.excludes:
				if route_path.startswith(item):
					is_white = True
		return is_white
