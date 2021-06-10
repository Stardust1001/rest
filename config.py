from datetime import date, datetime

from stardust.database import registe_database


db = {
	'host': '127.0.0.1',
	'user': 'root',
	'password': '123456',
	'db_name': 'blog',
	'port': 3306,
	'charset': 'utf8mb4',
	'max': 5
}

# 注册整个数据库，会把这个数据库中每个表都注册
# 这是 stardust.database.registe_table（负责注册数据表） 的快捷函数
# 注意：这个数据库中，每个表的主键，都是 id，且为自增整数类型
tables = registe_database(db)
