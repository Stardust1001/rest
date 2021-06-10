import json
from copy import deepcopy

from flask import request

from .constants import ErrorCodes, base_resp
from .decorators import check_json_body
from .restful import Restful
from .utils import check_param_exists, check_param_model, check_param_method, get_con


# restful 组合调用 视图类
class GroupView(Restful):

	def __init__(self):
		self.con = self.cursor = None
		self.is_single_con = self.is_atomic = False

	@check_json_body
	def post(self):
		params = json.loads(request.data)
		# 检查 group 参数
		ok, result = check_param_exists(params, ('group',))
		if not ok:
			return result
		(group,) = result

		con = model = pk = None

		# 是不是原子性操作
		self.is_atomic = params.get('is_atomic', False)
		# 是不是单个 connection
		is_single_con = self.is_single_con = params.get('is_single_con', False)
		if is_single_con == True:
			# 检查用来标记创建新 connection 的 model 参数，只是用来生成一个单一的 connection
			ok, result = check_param_model(params)
			if not ok:
				return result
			model = result
			# 创建单个 connection 实例 con，还有 cursor，供整个组合调用
			ok, result = get_con_cursor(model)
			if not ok:
				return result
			(con,) = (self.con, self.cursor) = result

		# 响应对象，组合调用的每个调用返回值，都放进 resp['data'] 数组里面
		group_resp = deepcopy(base_resp)
		data = group_resp['data'] = []
		# 迭代组合调用的每个元素，进行调用
		for item in group:
			self.params = item
			# 检查 model 参数
			ok, result = check_param_model(item)
			if not ok:
				data.append(result)
				continue
			self.model = result
			# 检查 method 参数
			ok, result = check_param_method(item)
			if not ok:
				data.append(result)
				continue
			method = result
			# 需要 pk 的调用方式
			if method in ('GET', 'PUT', 'DELETE'):
				ok, result = check_param_exists(item, ('id',))
				if not ok:
					data.append(result)
					continue
				(self.pk,) = result
			ele_resp = self.resp = deepcopy(base_resp)
			ok, ele_resp = self._check_con(self.model, ele_resp)
			if ok:
				# GET 调用
				if method == 'GET':
					ele_resp = self._get()
				# PUT 调用
				elif method == 'PUT':
					ele_resp = self._put()
				# DELETE 调用
				elif method == 'DELETE':
					ele_resp = self._delete()
				# POST 调用
				else:
					ele_resp = self._post()
				# 返回值 ok 为 False 则表明是 原子性操作，单 con 模式，出现了错误，而且可能出在数据库操作里面，这里回滚
				if ele_resp['err'] and self.is_atomic and self.is_single_con:
					# 回滚
					con.rollback()
					# 关闭 connection
					con.close()
					# 返回响应
					group_resp['code'] = ele_resp['code']
					group_resp['err'] = ele_resp['err']
					return group_resp
			if not self.is_single_con:
				self.close()
			# 没有需要回滚的错误，那就把这个调用的结果放进 resp['data'] 里
			data.append(ele_resp)
		# 如果是单 con 模式，这里请求结束了，关闭 connection
		if self.is_single_con:
			self.close()
		return group_resp

	def _get(self):
		return super().get()

	def _put(self):
		return super().put()

	def _delete(self):
		return super().delete()

	def _post(self):
		self.api_command = self.params.get('command')
		return super().post()

	def _check_con(self, model, resp):
		if self.con is None:
			self.con = get_con(model)
			try:
				self.cursor = self.con.cursor()
			except Exception as e:
				resp['code'] = ErrorCodes.UNKNOWN_ERROR
				resp['err'] = f'发生了未知错误 : {str(e)}'
				return False, resp
		return True, resp
