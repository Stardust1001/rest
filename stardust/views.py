import json
from copy import deepcopy

from flask import request

from .constants import base_resp, ErrorCodes
from .database import tables, connect
from .decorators import CheckArgs, check_model, check_json_body
from .utils import get_args
from .restful import Restful


# restful 视图类
class RestfulView(Restful):

	def __init__(self):
		Restful.__init__(self)
		(self.model,) = get_args(('model',))
		resp = self.resp = deepcopy(base_resp)
		self.method = request.method
		self.db = tables[self.model]['meta']['db']
		self.con = connect(self.db)
		try:
			self.cursor = self.con.cursor()
		except Exception as e:
			resp['code'] = ErrorCodes.UNKNOWN_ERROR
			resp['err'] = f'发生了未知错误 : {str(e)}'
			return
		if self.method in ('GET', 'PUT', 'DELETE'):
			(self.pk,) = get_args(('id',))
		if self.method in ('POST', 'PUT'):
			self.params = json.loads(request.data)
			if self.method == 'POST':
				(self.api_command,) = get_args(('command',))

	# get 请求，校验 query 参数的 model 和 id
	@CheckArgs(queries=('model', 'id'))
	# 校验 model 是否已配置
	@check_model
	def get(self):
		if self.resp['err']:
			return self.resp
		resp = super().get()
		self.close()
		return resp

	# 查询或创建的接口，校验 model 和 command 参数
	@CheckArgs(queries=('model', 'command'))
	@check_model
	@check_json_body
	def post(self):
		if self.resp['err']:
			return self.resp
		resp = super().post()
		self.close()
		return resp

	@CheckArgs(queries=('model', 'id'))
	@check_model
	@check_json_body
	def put(self):
		if self.resp['err']:
			return self.resp
		resp = super().put()
		self.close()
		return resp

	@CheckArgs(queries=('model', 'id'))
	@check_model
	def delete(self):
		if self.resp['err']:
			return self.resp
		resp = super().delete()
		self.close()
		return resp
