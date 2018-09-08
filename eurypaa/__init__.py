import flask 
import settings


class MyFlask(flask.Flask):
    def get_send_file_max_age(self, name):
	#if name.lower().endswith('.js'):
        #    return 60
        return flask.Flask.get_send_file_max_age(self, name)


app = MyFlask('eurypaa')
app.config.from_object('eurypaa.settings')


import views
