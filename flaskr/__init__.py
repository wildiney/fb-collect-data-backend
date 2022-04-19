import os

from flask import Flask
from flask_cors import CORS, cross_origin

import facebook
import requests
import pandas as pd
import numpy as np
import datetime as dt

from config.config import config


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    cors = CORS(app)
    app.config['CORS_HEADERS'] = 'Content-Type'

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    def graph():
        return facebook.GraphAPI(access_token=config.token, version='3.1')

    @app.route('/')
    def home():
        return {"fans": fans(), "engagement": engagement()}

    @app.route('/facebook/basic-info')
    def basic_info():
        fb = graph().get_object(id=config.page_id,
                                fields='country_page_likes, emails,featured_video, name, category, about, website, birthday, fan_count, engagement, followers_count')
        return fb

    @app.route('/facebook/fans')
    def fans():
        fb = graph().get_object(id=config.page_id, fields='fan_count')
        return {
            "status": 200,
            "message": "suceess",
            "fans": fb['fan_count']
        }

    @app.route('/facebook/engagement')
    def engagement():
        fb = graph().get_object(id=config.page_id, fields='engagement')
        return {
            "status": 200,
            "message": "success",
            "engagement": fb['engagement']['count']
        }

    @app.route('/facebook/fans/last90days')
    def fans_last_90_days():
        today = dt.datetime.now()
        dt_90 = today - dt.timedelta(days=90)
        fb = graph().get_connections(
            id=config.page_id, connection_name="insights", metric="page_fans", since=dt_90, until=today)
        return fb

    @app.route('/facebook/fans/by-idiom')
    def fans_by_idiom():
        today = dt.datetime.now()
        fb = graph().get_connections(
            id=config.page_id, connection_name="insights", metric="page_fans_locale", since=today, until=today)
        return fb

    @app.route('/facebook/fans/by-city')
    def fans_by_city():
        today = dt.datetime.now()
        dt_90 = today - dt.timedelta(days=90)
        fb = graph().get_connections(id=config.page_id, connection_name='insights',
                                     metric='page_fans_city', since=today, until=today)
        return fb

    @app.route('/facebook/fans/by-country')
    def fans_by_country():
        today = dt.datetime.now()
        dt_90 = today - dt.timedelta(days=90)
        fb = graph().get_connections(id=config.page_id, connection_name='insights',
                                     metric='page_fans_country', since=today, until=today)
        return fb

    @app.route('/facebook/fans/byperiod')
    @cross_origin()
    def fans_by_period():
        values = []
        now = dt.datetime.now()
        today = dt.date.today()
        year_start = 2019
        year_end = now.year
        metric = "page_fans"

        for year in range(year_start, year_end+1):
            for month in range(1, 12):
                if year == year_end and month == 4:
                    break
                since = str(year)+"-"+str(month).rjust(2, '0')+"-14"
                until = str(year)+"-"+str(month+1).rjust(2, '0')+"-15"
                try:
                    fas = graph().get_connections(
                        id=config.page_id, connection_name='insights', metric=metric, since=since, until=until)
                    for x in fas['data'][0]['values']:
                        values.append(
                            {'x': x['end_time'][0:10], 'y': x['value']})
                except:
                    print(since, until)

        return {"data": values}

    return app
