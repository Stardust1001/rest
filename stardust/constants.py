from enum import IntEnum


# 响应的错误类型
class ErrorCodes(IntEnum):
	# 未知错误
	UNKNOWN_ERROR			= 40000
	# 缺少参数
	LESS_OF_PARAMS			= 40001
	# 无效的参数
	INVALID_PARAMS			= 40002
	# 未经配置的 model
	NOT_CONFIGURED_MODEL	= 40003
	# 用户不存在
	USER_NOT_EXISTS			= 40004
	# 用户名密码不匹配
	NAME_PASS_NOT_MATCH		= 40005
	# 组合接口没有组合的数组参数或数组参数没有元素
	BLANK_GROUP_PARAMS		= 50006


# 一些默认值
defaults = {
	# 默认分页是第一页
	'page': 1,
	# 默认一页展示10条
	'limit': 10,
	# 默认每个连接池最大连接数
	'max_connections': 5
}

# 基本响应 json 结构
base_resp = {
	'code': 200,
	'data': { },
	'err': ''
}
