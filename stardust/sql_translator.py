from pymysql.converters import escape_string
from flask import request

from .database import tables
from .utils import get_type_sql_str, translate_op
from .constants import defaults


# 把参数翻译成 SQL 语句的主函数
# 根据请求类型，对应翻译
def translate(model, command, params, pk):
	sql = ''
	# 获取一条记录
	if command == 'get':
		sql = get(model, pk)
	# 查询数条记录
	elif command == 'select':
		sql = select(model, params)
	# 查询条件对应的记录总数
	elif command == 'count':
		sql = count(model, params)
	# 插入一条记录
	elif command == 'insert':
		sql = insert(model, params)
	# 更新一条记录
	elif command == 'update':
		sql = update(model, params, pk)
	# 删除一条记录
	elif command == 'delete':
		sql = delete(model, pk)
	return sql


def get(model, pk):
	sql = f'select * from {model} '
	sql += _append_id(model, pk)

	return sql


def select(model, params):
	sql = 'select '

	# 页码
	page = int(params.get('page', defaults['page']))
	# 每页条数
	limit = int(params.get('limit', defaults['limit']))
	# 排序规则
	order = params.get('order', [])
	# 查询条件
	op = params.get('op', None)
	# 要获取的字段列表，不提供就默认获取这个表中配置的所有字段
	attributes = params.get('attributes', None)
	if attributes is None:
		attributes = tables[model]['attributes']
	sql += escape_string(', '.join(attributes)) + ' '

	sql += f'from {model} where TRUE '

	# 翻译 op 查询参数
	op_sql = translate_op(op)
	# 如果是 op or 参数， op_sql 开头会有 'or' 文字，需要去除
	if op_sql.startswith('or'):
		sql = sql[0:-6] + op_sql[2:]
	else:
		sql = sql + op_sql

	# 如果翻译参数为空，sql 会以 where TRUE 结尾，就不再需要 where TRUE，去除掉
	if sql.endswith('where TRUE '):
		sql = sql[0:-11] + ' '
	# 排序
	if order:
		sql += ' order by '
		for i, o in enumerate(order):
			sql += escape_string(' '.join(o)) + ', '
		sql = sql[0:-2] + ' '
	# 分页
	sql += f'limit {(page - 1) * limit}, {limit}'

	return sql


def count(model, params):
	select_sql = select(model, params)
	from_index = select_sql.index(f'from {model}')
	limit_index = select_sql.rindex('limit')
	return f'select count(*) {select_sql[from_index:limit_index]}'


def insert(model, params):
	sql = f'insert into {model} '

	keys = params.keys()
	values = params.values()

	keys_str = ', '.join(keys)
	keys_str = escape_string(keys_str)
	sql += f'({keys_str}) values('
	for v in values:
		if v is None:
			sql += 'NULL, '
		else:
			tss = get_type_sql_str(v)
			sql += f'{tss}, '
	sql = sql[0:-2] + ')'

	return sql


def update(model, params, pk):
	sql = f'update {model} set '
	for k, v in params.items():
		k = escape_string(k)
		if v is None:
			sql += f'{k}=NULL, '
		else:
			tss = get_type_sql_str(v)
			sql += f'{k}={tss}, '

	sql = sql[0:-2] + ' ' + _append_id(model, pk)

	return sql


def delete(model, pk):
	sql = f'delete from {model} '
	sql += _append_id(model, pk)

	return sql


# 表的主键不知道什么情况，需要根据 table 的 meta 配置来往 sql 里添加
def _append_id(model, pk):
	id_name = tables[model]['meta']['id_name']
	id_type = tables[model]['meta']['id_type']

	sql_suffix = f'where {id_name}='

	if id_type == str:
		pk = escape_string(pk)
		sql_suffix += f"'{pk}'"
	else:
		sql_suffix += f'{pk}'

	return sql_suffix
