from stardust.views import RestfulView
from app import app
import config

app.add_url_rule('/restful', view_func=RestfulView.as_view('restful'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
