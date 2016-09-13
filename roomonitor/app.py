import json
import os

import web
from web.contrib.template import render_jinja
from db import DbFactory, SensorLog, SensorStatus, Controller
from utils import query_sensor_logs, query_sensor_status, TIME_FORMAT

urls = (
    '/', 'index',
    '/logs', 'logs'
)
app = web.application(urls, globals())
renderer = render_jinja('static', encoding='utf-8')

class index:
    def GET(self):
        return renderer.index()


class logs:
    def GET(self):
        params = web.input()
        last_id = params.lastId if hasattr(params, 'lastId') else None
        logs = query_sensor_logs(last_id=last_id)
        return json.dumps(map(lambda r: {
            'id': r.id,
            'controllerName': r.controller_name,
            'sensorId': r.sensor_id,
            'status': r.status,
            'updateTime': r.update_time.strftime(TIME_FORMAT),
            'reportTime': r.report_time.strftime(TIME_FORMAT),
            'temperature': r.temperature,
            'humidity': r.humidity
        }, logs))


if __name__ == '__main__':
    app.run()
else:
    application = app.wsgifunc()
