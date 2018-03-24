from unittest import TestCase
import io
from contextlib import redirect_stdout
import requests
import json

import requests_mock

from ..fetch_facebook_posts_data import (fetch_node_feed, fetch_posts,
    format_datetime_string)


FACEBOOK_POSTS_ONE_RECORD_DATA = {
    'data': [{
        'created_time': '2018-03-19T18:17:00+0000', 
        'message': 'This is a test message', 
        'id': '11239244970_10150962953494971'},],
    'paging': {
        'cursors': {'before': 'before_cursor_AAA', 'after': 'after_cursor_ZZZ'}, 
        'next': 'https://graph.facebook.com/v2.11/11239244970/feed?access_token=AAA'}
}


FACEBOOK_POSTS_MULT_RECORD_DATA = {
    'data': [{
        'created_time': '2018-03-19T18:17:00+0000', 
        'message': 'This is a test message', 
        'id': '11239244970_10150962953494971'},
        {
        'created_time': '2018-03-19T18:17:00+0000', 
        'message': 'This is a anothertest message', 
        'id': '11239244970_10150962953494111'}],
    'paging': {
        'cursors': {'before': 'before_cursor_AAA', 'after': 'after_cursor_ZZZ'}, 
        'next': 'https://graph.facebook.com/v2.11/11239244970/feed?access_token=AAA'}
}


AUTH_TOKEN_INVALID_DATA = {
    "error":{
        "message":"Invalid OAuth access token.",
        "type":"OAuthException",
        "code":190,
        "fbtrace_id":"ADSG8pUqsRg"
    }
}



def read_access_token():
    with open('config.json') as config_file:
        data = json.load(config_file)
    return data['access_token']



def equal_dicts(d1, d2, ignore_keys=None):
    if type(ignore_keys) == str:
        ignore_keys = [ignore_keys, ]
    ignored = set(ignore_keys)
    for k1, v1 in d1.items():
        if k1 not in ignored and (k1 not in d2 or d2[k1] != v1):
            return False
    for k2, v2 in d2.items():
        if k2 not in ignored and k2 not in d1:
            return False
    return True


def sysoutput_to_dicts(out):
    return [json.loads(x) for x in out.getvalue().split('\n')[:-1]]


class TestFetchFacebookPostsData(TestCase):

    def test_raise_error_for_non_200_response(self):
        with requests_mock.Mocker() as m:
            request_url = 'https://graph.facebook.com/v2.11/account_id/feed?access_token=AAA'
            m.register_uri('GET', request_url, status_code=400, content=b'{"error":{"message":"Error validating access token: Session has expired on Saturday, 24-Mar-18 05:00:00 PDT. The current time is Saturday, 24-Mar-18 05:20:17 PDT.","type":"OAuthException","code":190,"error_subcode":463,"fbtrace_id":"ACz1b5AhZtt"}}')
            with self.assertRaises(requests.exceptions.HTTPError) as error_manager:
                fetch_node_feed('account_id', access_token='AAA')

            # It's given us a helpful exception
            self.assertIn('400 Client Error: {"error":{"message":"Error validating access token', 
                          error_manager.exception.__str__())
    
    def test_dont_raise_error_for_200_response(self):
        with requests_mock.Mocker() as m:
            request_url = 'https://graph.facebook.com/v2.11/account_id/feed?access_token=AAA'
            m.register_uri('GET', request_url, status_code=200, 
                           content=json.dumps(FACEBOOK_POSTS_ONE_RECORD_DATA).encode('utf-8'))
            response = fetch_node_feed('account_id', access_token='AAA')
            
            self.assertEqual(FACEBOOK_POSTS_ONE_RECORD_DATA, response)

    def test_can_write_schema(self):
        out = io.StringIO()
        with redirect_stdout(out):
            with requests_mock.Mocker() as m:
                request_url = 'https://graph.facebook.com/v2.11/account_id/feed?access_token=AAA'
                m.register_uri('GET', request_url, status_code=200, 
                           content=json.dumps(FACEBOOK_POSTS_ONE_RECORD_DATA).encode('utf-8'))
                fetch_posts(node_id='account_id', access_token='AAA')

        out_dicts = sysoutput_to_dicts(out)
        row_types = [x['type'] for x in out_dicts]
        # We have a schema record type
        self.assertIn('SCHEMA', row_types)
    
    def test_can_write_one_record(self):
        out = io.StringIO()
        with requests_mock.Mocker() as m:
            request_url = 'https://graph.facebook.com/v2.11/officialstackoverflow/feed?access_token=AAA'
            m.register_uri('GET', request_url, status_code=200, 
                           content=json.dumps(FACEBOOK_POSTS_ONE_RECORD_DATA).encode('utf-8'))
        
            with redirect_stdout(out):
                fetch_posts('officialstackoverflow', 'AAA')

        out_dicts = sysoutput_to_dicts(out)
        row_types = [x['type'] for x in out_dicts]
        # We wrote at least 1 record
        self.assertIn('RECORD', row_types)
        # And it contains our expected data
        self.assertTrue(equal_dicts(out_dicts[1]['record'], 
                        FACEBOOK_POSTS_ONE_RECORD_DATA['data'][0],
                        ignore_keys='created_time'))

    
    def test_can_write_multiple_records(self):
        out = io.StringIO()
        with requests_mock.Mocker() as m:
            request_url = 'https://graph.facebook.com/v2.11/officialstackoverflow/feed?access_token=AAA'
            m.register_uri('GET', request_url, status_code=200, 
                           content=json.dumps(FACEBOOK_POSTS_MULT_RECORD_DATA).encode('utf-8'))
        
            with redirect_stdout(out):
                fetch_posts('officialstackoverflow', 'AAA')

        out_dicts = sysoutput_to_dicts(out)
        row_types = [x['type'] for x in out_dicts]
        # We wrote at least 1 record
        self.assertIn('RECORD', row_types)
        # And it contains both of our expected data points
        self.assertTrue(equal_dicts(out_dicts[1]['record'], 
            FACEBOOK_POSTS_MULT_RECORD_DATA['data'][0],
            ignore_keys='created_time'))
        self.assertTrue(equal_dicts(out_dicts[2]['record'], 
            FACEBOOK_POSTS_MULT_RECORD_DATA['data'][1],
            ignore_keys='created_time'))
    
    def test_records_have_singer_format_string_times(self):
        out = io.StringIO()
        with requests_mock.Mocker() as m:
            request_url = 'https://graph.facebook.com/v2.11/officialstackoverflow/feed?access_token=AAA'
            m.register_uri('GET', request_url, status_code=200, 
                           content=json.dumps(FACEBOOK_POSTS_ONE_RECORD_DATA).encode('utf-8'))
        
            with redirect_stdout(out):
                fetch_posts('officialstackoverflow', 'AAA')

        out_dicts = sysoutput_to_dicts(out)
        row_types = [x['type'] for x in out_dicts]

        # It has been converted
        self.assertNotEqual(out_dicts[1]['record']['created_time'],
                            FACEBOOK_POSTS_ONE_RECORD_DATA['data'][0]['created_time'])
        # to the format that Singer expects
        self.assertEqual(out_dicts[1]['record']['created_time'], 
                         '2018-03-19T18:17:00Z')

    def test_format_datetime_string_correctly(self):
        fb_format_datetime = '2018-03-19T18:17:00+0000'
        formatted_datetime = format_datetime_string(fb_format_datetime)

        self.assertEqual(formatted_datetime, '2018-03-19T18:17:00Z')

    def test_invalid_config_access_token(self):
        with requests_mock.Mocker() as m:
            request_url = 'https://graph.facebook.com/v2.11/officialstackoverflow/feed?access_token=AAA'
            m.register_uri('GET', request_url, status_code=200, 
                           content=json.dumps(AUTH_TOKEN_INVALID_DATA).encode('utf-8'))

        with self.assertRaises(requests.exceptions.HTTPError) as error_manager:
            fetch_posts('officialstackoverflow', 'AAA')

        error_message = error_manager.exception.args[0]
        self.assertIn('400 Client Error', error_message)
        self.assertIn('Invalid OAuth access token', error_message)


class TestStateAndPagination(TestCase):

    def test_can_write_state(self):
        out = io.StringIO()
        with redirect_stdout(out):
            with requests_mock.Mocker() as m:
                request_url = 'https://graph.facebook.com/v2.11/account_id/feed?access_token=AAA'
                m.register_uri('GET', request_url, status_code=200, 
                           content=json.dumps(FACEBOOK_POSTS_ONE_RECORD_DATA).encode('utf-8'))
                fetch_posts(node_id='account_id', access_token='AAA')

        out_dicts = sysoutput_to_dicts(out)
        row_types = [x['type'] for x in out_dicts]
        # We have a state record type
        self.assertIn('STATE', row_types)

    def test_can_start_pulling_data_at_a_certain_page(self):
        access_token = read_access_token()
        fetch_posts('officialstackoverflow', access_token=access_token)
    