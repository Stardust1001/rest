from pymysql.converters import escape_string
from flask import request

from .constants import ErrorCodes
from .database import tables, connect


# 从 request.args 中获取指定的参数数组对应的值
def get_args(queries=()):
	return (request.args.get(query) for query in queries)


# 根据参数值的类型，生成这个类型需要的 SQL 字符串
def get_type_sql_str(v):
	v_type = type(v)
	if v_type == str:
		v = escape_string(v)
		return f"'{v}'"
	elif v_type == int or v_type == float:
		return f'{v}'
	elif v_type == bool:
		return 'TRUE' if v else 'FALSE'
	elif v_type == list or v_type == tuple:
		# 参数值是个数组，递归
		arr_str = ', '.join((get_type_sql_str(ele) for ele in v))
		return f'({arr_str})'
	return ''


# op 查询参数所支持的比较运算符
_operators = {
	'gt': '>',
	'lt': '<',
	'gte': '>=',
	'lte': '<='
}
# 翻译 op 查询参数
def translate_op(op):
	if op is None:
		return ''
	sql = ''
	for op_key, op_value in op.items():
		if op_key == 'or':
			# or 参数，需要递归翻译
			for k, v in op_value.items():
				sub_op = { }
				sub_op[k] = v
				sub_sql = translate_op({ 'where': sub_op })
				sub_sql = sub_sql[4:]
				sql += f'or ({sub_sql}) '
		else:
			for k, v in op_value.items():
				k = escape_string(k)
				tss = get_type_sql_str(v)
				if op_key == 'where':
					if v is None:
						sql += f'and {k} is NULL '
					else:
						sql += f'and {k}={tss} '
				elif op_key == 'not':
					if v is None:
						sql += f'and {k} is not NULL '
					else:
						sql += f'and {k}!={tss} '
				elif op_key in _operators:
					symbol = _operators[op_key]
					sql += f'and {k} {symbol} {tss} '
				else:
					sql += f'and {k} {op_key} {tss} '
	return sql

def check_param_exists(param, keys=()):
	values = []
	for key in keys:
		value = param.get(key, None)
		if value is None:
			return False, {
				'code': ErrorCodes.LESS_OF_PARAMS,
				'err': f'组合调用参数缺失 : {key}'
			}
		values.append(value)
	return True, values

def check_param_model(param):
	model = param.get('model')
	if model not in tables:
		return False, {
			'code': ErrorCodes.NOT_CONFIGURED_MODEL,
			'err': f'未经配置的 model : {model}'
		}
	return True, model

def check_param_method(param):
	method = param.get('method')
	if method not in ('GET', 'POST', 'PUT', 'DELETE'):
		return False, {
			'code': ErrorCodes.INVALID_PARAMS,
			'err': f'无效的参数 : method'
		}
	return True, method

def get_con(model):
	return connect(tables[model]['meta']['db'])
