from datetime import date, datetime
from copy import deepcopy
import pymysql
from DBUtils.PooledDB import PooledDB

from .constants import defaults


pools = { }

# 注册管理的所有数据表，在这个对象里
# key 为表名，value 为表的配置
tables = { }


# 根据 cf 配置，连接数据库
def connect(cf):
	pool_name = cf['host'] + '-' + str(cf['port']) + '-' + cf['db_name']
	if hasattr(pools, pool_name):
		 return pools[pool_name].connection()
	con_charset = 'utf8mb4'
	if hasattr(cf, 'charset'):
		con_charset = cf['charset']
	max_con = defaults['max_connections']
	if hasattr(cf, 'max'):
		max_con = cf['max']
	pool = PooledDB(
		pymysql,
		max_con,
		host=cf['host'],
		port=cf['port'],
		user=cf['user'],
		passwd=cf['password'],
		database=cf['db_name'],
		charset=con_charset
	)
	pools[pool_name] = pool
	return pool.connection()

# mysql 字段类型到 python 数据类型的映射
_mysql_type_2_py_type = {
	'int': int,
	'bigint': int,
	'float': float,
	'char': str,
	'varchar': str,
	'text': str,
	'tinyint': bool,
	'date': date,
	'datetime': datetime
}

# python 数据类型到 javascript 数据类型的映射
_py_type_2_js_type = {
	str: 'string',
	int: 'number',
	float: 'number',
	date: 'date',
	datetime: 'date',
	bool: 'boolean'
}

# 表的基本配置
_base_meta = {
	# 表的主键名
	'id_name': 'id',
	# 表的主键的类型
	'id_type': int,
	# 表对应的数据库配置，cf，供 connect 函数调用
	'db': None
}


# 注册整个数据库，主键名得是 id，主键类型得是 int
def registe_database(db, metas={}):
	tableDict = { }
	con = connect(db)
	try:
		cursor = con.cursor()
		cursor.execute('show tables')
		table_names = (ele[0] for ele in cursor.fetchall())
		for name in table_names:
			if hasattr(metas, name):
				meta = metas[name]
			else:
				meta = deepcopy(_base_meta)
				meta['db'] = db
			tableDict[name] = registe_table(name, meta)
		con.close()
	except Exception:
		con.close()
	return tableDict


# 注册一个数据表，meta 为基本配置，包括 id_name id_type db
# fields 是这个数据表需要管理的所有字段
# 注册一个数据表之后，会把这个表放到 tables 对象中，并且返回这个配置好的表
def registe_table(name, meta=None, fields=None):
	# 这是一个注册的数据表的配置信息
	table = {
		# meta 是里有表的基本配置，id_name id_type db
		'meta': meta,
		# fields 是这个表要管理的所有字段，为一个对象，key 为字段名称，value 为字段类型
		'fields': fields,
		# fields 的 javascript 形式，key 为字段名称，value 为字段的 javascript 类型
		'fields_js': { },
		# attributes 是这个表要管理的所有字段的名称数组
		'attributes': []
	}
	if fields is None:
		# 没有提供 fields 参数，就自动连接数据库读取数据表的信息，配置 fields
		table['fields'] = { }
		con = connect(meta['db'])
		try:
			cursor = con.cursor()
			db_name = meta['db']['db_name']
			sql = f"select COLUMN_NAME, DATA_TYPE from information_schema.COLUMNS where table_name='{name}' and table_schema='{db_name}'"
			cursor.execute(sql)
			records = cursor.fetchall()
			for field, f_type in records:
				py_type = _mysql_type_2_py_type[f_type]
				table['fields'][field] = py_type
			con.close()
		except Exception:
			con.close()
	for k, v in table['fields'].items():
		table['fields_js'][k] = _py_type_2_js_type[v]
	table['attributes'] = tuple(table['fields'].keys())
	tables[name] = deepcopy(table)
	return table
