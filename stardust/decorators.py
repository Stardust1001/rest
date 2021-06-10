import json
from functools import wraps
from flask import request

from .constants import ErrorCodes
from .database import tables


# 检查 request.args （url 的 query ? 参数） 里某些参数是否存在
# 不存在就返回，并且提供错误信息
class CheckArgs:

	def __init__(self, queries=()):
		self.queries = queries

	def __call__(self, func):
		def wrapper(*args, **kwargs):
			for query in self.queries:
				if request.args.get(query, None) is None:
					return {
						'code': ErrorCodes.LESS_OF_PARAMS,
						'err': f'参数缺失 : {query}'
					}
			return func(*args, **kwargs)
		return wrapper


# 检查 request.args 里的 model 参数对应的数据表是否已在 database.py 里的 tables 中配置
# 没配置就返回，并且提供错误信息
def check_model(func):
	@wraps(func)
	def wrapper(*args, **kwargs):
		model = request.args.get('model')
		if model not in tables:
			return {
				'code': ErrorCodes.NOT_CONFIGURED_MODEL,
				'err': f'未经配置的 model : {model}'
			}
		return func(*args, **kwargs)
	return wrapper


# 检查请求体 json 是否正确
def check_json_body(func):
	@wraps(func)
	def wrapper(*args, **kwargs):
		if not json.loads(request.data):
			return {
				'code': ErrorCodes.INVALID_PARAMS,
				'err': f'请求体无效'
			}
		return func(*args, **kwargs)
	return wrapper
