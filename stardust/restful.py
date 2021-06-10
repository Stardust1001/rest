from flask.views import MethodView

from .constants import ErrorCodes, defaults
from .database import tables, connect
from .sql_translator import translate


# restful 视图类
class Restful(MethodView):

	def __init__(self):
		self.params = None
		self.model = None
		self.pk = None
		self.api_command = None
		self.method = None
		self.con = None
		self.cursor = None
		self.resp = None

	def before_get(self):
		return self.model, self.pk, self.con, self.cursor, self.resp

	def before_post(self):
		return self.params, self.model, self.api_command, self.con, self.cursor, self.resp

	def before_put(self):
		return self.params, self.model, self.pk, self.con, self.cursor, self.resp

	def before_delete(self):
		return self.model, self.pk, self.con, self.cursor, self.resp

	def after_get(self):
		return self.resp

	def after_post(self):
		return self.resp

	def after_put(self):
		return self.resp

	def after_delete(self):
		return self.resp

	def before_response(self):
		data = self.resp['data']
		if data and type(data) == tuple:
			is_tuple = type(data[0]) == tuple
			records = data if is_tuple else [data]
			attributes = self.resp['attributes']
			json_data = []
			for record in records:
				json_data.append({
					attr: record[i] for i, attr in enumerate(attributes)
				})
			self.resp['data'] = json_data if is_tuple else json_data[0]
		if 'attributes' in self.resp:
			del self.resp['attributes']

		return self.resp

	def close(self):
		self.cursor.close()
		self.con.close()
		self.con = None

	def get(self):
		model, pk, con, cursor, resp = self.before_get()
		try:
			sql = translate(model, 'get', None, pk)
			cursor.execute(sql)
			record = cursor.fetchone()
			resp['data'] = record
			resp['attributes'] = tables[model]['attributes']
			resp = self.after_get()
		except Exception as e:
			resp['code'] = ErrorCodes.UNKNOWN_ERROR
			resp['err'] = f'发生了未知的错误 : {str(e)}'
		resp = self.before_response()
		return resp

	def post(self):
		params, model, api_command, con, cursor, resp = self.before_post()
		# command 为 add ，对应创建记录
		# command 为 search ，对应查询记录
		if api_command not in ('add', 'search'):
			resp['code'] = ErrorCodes.INVALID_PARAMS
			resp['err'] = '参数错误 : command'
			return resp
		try:
			sql = ''
			if api_command == 'add':
				sql = translate(model, 'insert', params, None)
				cursor.execute(sql)
				cursor.execute('select LAST_INSERT_ID()')
				resp['data'] = cursor.fetchone()[0]
				con.commit()
			elif api_command == 'search':
				attributes = params.get('attributes', tables[model]['attributes'])
				sql = translate(model, 'count', params, None)
				cursor.execute(sql)
				total = cursor.fetchone()[0]
				sql = translate(model, 'select', params, None)
				cursor.execute(sql)
				records = cursor.fetchall()
				resp['data'] = records
				resp['total'] = total
				resp['page'] = params.get('page', defaults['page'])
				resp['limit'] = params.get('limit', defaults['limit'])
				resp['attributes'] = attributes
			resp = self.after_post()
		except Exception as e:
			resp['code'] = ErrorCodes.UNKNOWN_ERROR
			resp['err'] = f'发生了未知错误 : {str(e)}'
		resp = self.before_response()
		return resp

	def put(self):
		params, model, pk, con, cursor, resp = self.before_put()
		try:
			sql = translate(model, 'update', params, pk)
			resp['data'] = cursor.execute(sql)
			con.commit()
			resp = self.after_put()
		except Exception as e:
			resp['code'] = ErrorCodes.UNKNOWN_ERROR
			resp['err'] = f'发生了未知错误 : {str(e)}'
		resp = self.before_response()
		return resp

	def delete(self):
		model, pk, con, cursor, resp = self.before_delete()
		try:
			sql = translate(model, 'delete', None, pk)
			resp['data'] = cursor.execute(sql)
			con.commit()
			resp = self.after_delete()
		except Exception as e:
			resp['code'] = ErrorCodes.UNKNOWN_ERROR
			resp['err'] = f'发生了未知错误 : {str(e)}'
		resp = self.before_response()
		return resp
