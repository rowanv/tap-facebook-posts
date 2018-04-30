from unittest import TestCase
import io
import json
from contextlib import redirect_stdout

import requests
import requests_mock

from ..fetch_facebook_posts_data import (fetch_node_feed, fetch_posts,
                                         format_datetime_string,
                                         clean_reactions_data)
from .constants import (
    BASE_FB_URL, REACTIONS_URL,FACEBOOK_POSTS_ONE_RECORD_RAW_DATA,
    FACEBOOK_POSTS_ONE_RECORD_CLEAN_DATA,
    SAMPLE_COUNT, FACEBOOK_LAST_PAGE_RECORD_RAW_DATA,
    FACEBOOK_LAST_PAGE_RECORD_CLEAN_DATA,
    FACEBOOK_POSTS_MULT_RECORD_RAW_DATA,
    FACEBOOK_POSTS_MULT_RECORD_CLEAN_DATA)


AUTH_TOKEN_INVALID_DATA = {
    "error": {
        "message": "Invalid OAuth access token.",
        "type": "OAuthException",
        "code": 190,
        "fbtrace_id": "ADSG8pUqsRg"
    }
}


def read_access_token():
    with open('config.json') as config_file:
        data = json.load(config_file)
    return data['access_token']


def equal_dicts(d1, d2, ignore_keys=None):
    if isinstance(ignore_keys, str):
        ignore_keys = [ignore_keys, ]
    ignored = set(ignore_keys)
    for k1, v1 in d1.items():
        if k1 not in ignored and (k1 not in d2 or d2[k1] != v1):
            return False
    for k2, _ in d2.items():
        if k2 not in ignored and k2 not in d1:
            return False
    return True


def sysoutput_to_dicts(out):
    return [json.loads(x) for x in out.getvalue().split('\n')[:-1]]


class TestFetchFacebookPostsData(TestCase):

    def test_raise_error_for_non_200_response(self):
        with requests_mock.Mocker() as m:
            request_url = BASE_FB_URL + 'account_id' + REACTIONS_URL + 'AAA'
            m.register_uri(
                'GET',
                request_url,
                status_code=400,
                content=b'{"error":{"message":"Error validating access token: Session has expired on Saturday, 24-Mar-18 05:00:00 PDT. The current time is Saturday, 24-Mar-18 05:20:17 PDT.","type":"OAuthException","code":190,"error_subcode":463,"fbtrace_id":"ACz1b5AhZtt"}}')
            with self.assertRaises(requests.exceptions.HTTPError) as error_manager:
                fetch_node_feed('account_id', access_token='AAA')

            # It's given us a helpful exception
            self.assertIn(
                '400 Client Error: {"error":{"message":"Error validating access token',
                error_manager.exception.__str__())

    def test_dont_raise_error_for_200_response(self):
        with requests_mock.Mocker() as m:
            request_url = BASE_FB_URL + 'account_id' + REACTIONS_URL + 'AAA'
            m.register_uri(
                'GET', request_url, status_code=200, content=json.dumps(
                    FACEBOOK_POSTS_ONE_RECORD_RAW_DATA).encode('utf-8'))
            response = fetch_node_feed('account_id', access_token='AAA')

            self.assertEqual(FACEBOOK_POSTS_ONE_RECORD_RAW_DATA, response)

    def test_can_write_schema(self):
        out = io.StringIO()
        with redirect_stdout(out):
            with requests_mock.Mocker() as m:
                request_url = BASE_FB_URL + 'account_id' + REACTIONS_URL + 'AAA'
                m.register_uri(
                    'GET', request_url, status_code=200, content=json.dumps(
                        FACEBOOK_POSTS_ONE_RECORD_RAW_DATA).encode('utf-8'))
                fetch_posts(node_id='account_id', access_token='AAA')

        out_dicts = sysoutput_to_dicts(out)
        row_types = [x['type'] for x in out_dicts]
        # We have a schema record type
        self.assertIn('SCHEMA', row_types)

    def test_can_write_one_record(self):
        out = io.StringIO()
        with requests_mock.Mocker() as m:
            request_url = BASE_FB_URL + 'officialstackoverflow' + REACTIONS_URL + 'AAA'
            m.register_uri('GET', request_url, status_code=200, content=json.dumps(
                FACEBOOK_POSTS_ONE_RECORD_RAW_DATA).encode('utf-8'))

            with redirect_stdout(out):
                fetch_posts('officialstackoverflow', 'AAA')

        out_dicts = sysoutput_to_dicts(out)
        row_types = [x['type'] for x in out_dicts]
        # We wrote at least 1 record
        self.assertIn('RECORD', row_types)
        # And it contains our expected data
        self.assertTrue(equal_dicts(out_dicts[1]['record'],
                                    FACEBOOK_POSTS_ONE_RECORD_CLEAN_DATA['data'][0],
                                    ignore_keys='created_time'))

    def test_can_write_multiple_records(self):
        out = io.StringIO()
        with requests_mock.Mocker() as m:
            request_url = BASE_FB_URL + 'officialstackoverflow' + REACTIONS_URL + 'AAA'
            m.register_uri('GET', request_url, status_code=200, content=json.dumps(
                           FACEBOOK_POSTS_MULT_RECORD_RAW_DATA).encode('utf-8'))

            with redirect_stdout(out):
                fetch_posts('officialstackoverflow', 'AAA')

        out_dicts = sysoutput_to_dicts(out)
        row_types = [x['type'] for x in out_dicts]
        # We wrote at least 1 record
        self.assertIn('RECORD', row_types)
        # And it contains both of our expected data points
        self.assertTrue(equal_dicts(out_dicts[1]['record'],
                                    FACEBOOK_POSTS_MULT_RECORD_CLEAN_DATA['data'][0],
                                    ignore_keys='created_time'))
        self.assertTrue(equal_dicts(out_dicts[2]['record'],
                                    FACEBOOK_POSTS_MULT_RECORD_CLEAN_DATA['data'][1],
                                    ignore_keys='created_time'))

    def test_records_have_singer_format_string_times(self):
        out = io.StringIO()
        with requests_mock.Mocker() as m:
            request_url = BASE_FB_URL + 'officialstackoverflow' + REACTIONS_URL + 'AAA'
            m.register_uri('GET', request_url, status_code=200, content=json.dumps(
                FACEBOOK_POSTS_ONE_RECORD_RAW_DATA).encode('utf-8'))

            with redirect_stdout(out):
                fetch_posts('officialstackoverflow', 'AAA')

        out_dicts = sysoutput_to_dicts(out)

        # It has been converted
        self.assertNotEqual(
            out_dicts[1]['record']['created_time'],
            FACEBOOK_POSTS_ONE_RECORD_RAW_DATA['data'][0]['created_time'])
        # to the format that Singer expects
        self.assertEqual(out_dicts[1]['record']['created_time'],
                         '2018-03-19T18:17:00Z')

    def test_format_datetime_string_correctly(self):
        fb_format_datetime = '2018-03-19T18:17:00+0000'
        formatted_datetime = format_datetime_string(fb_format_datetime)

        self.assertEqual(formatted_datetime, '2018-03-19T18:17:00Z')

    def test_invalid_config_access_token(self):
        out = io.StringIO()
        with requests_mock.Mocker() as m:
            request_url = (BASE_FB_URL +
                           'officialstackoverflow/feed?access_token=AAA')
            m.register_uri(
                'GET',
                request_url,
                status_code=200,
                content=json.dumps(AUTH_TOKEN_INVALID_DATA).encode('utf-8'))

        with redirect_stdout(out):
            with self.assertRaises(requests.exceptions.HTTPError) as error_manager:
                fetch_posts('officialstackoverflow', 'AAA')

        error_message = error_manager.exception.args[0]
        self.assertIn('400 Client Error', error_message)
        self.assertIn('Invalid OAuth access token', error_message)


class TestCanFetchPostStats(TestCase):

    def test_can_get_reaction_count_from_original_api_call(self):
        with requests_mock.Mocker() as m:
            reactions_url = BASE_FB_URL + 'account_id' + REACTIONS_URL + 'AAA'
            m.register_uri(
                'GET', reactions_url, status_code=200, content=json.dumps(
                    FACEBOOK_POSTS_ONE_RECORD_RAW_DATA).encode('utf-8'))

            response = fetch_node_feed('account_id', access_token='AAA')

            reaction_labels = [
                'none_reaction_count', 'sad_count', 'like_count', 'love_count',
                'pride_count', 'total_reaction_count', 'haha_count', 'wow_count',
                'thankful_count', 'angry_count'
            ]
            for r in reaction_labels:
                self.assertTrue(response['data'][0][r])

    def test_can_get_clean_reaction_count(self):
        reaction_labels = [
            'none_reaction_count', 'sad_count', 'like_count', 'love_count',
            'pride_count', 'total_reaction_count', 'haha_count', 'wow_count',
            'thankful_count', 'angry_count'
        ]
        reactions_data = {}
        for reaction in reaction_labels:
            reactions_data[reaction] = SAMPLE_COUNT

        cleaned_data = clean_reactions_data(reactions_data)

        # And our resulting data is flat
        self.assertEqual(cleaned_data['none_reaction_count'], 566)
        self.assertEqual(cleaned_data['sad_count'], 566)


    def test_can_get_clean_comment_count(self):
        reactions_data = {
            "comment_count": {
                "data": [
                ],
                "summary": {
                  "order": "ranked",
                  "total_count": 7,
                  "can_comment": True
                }
            }
        }

        cleaned_data = clean_reactions_data(reactions_data)

        # And our resulting data is flat
        self.assertEqual(cleaned_data['comment_count'], 7)


class TestStateAndPagination(TestCase):

    def test_can_write_state(self):
        out = io.StringIO()
        with redirect_stdout(out):
            with requests_mock.Mocker() as m:
                request_url = BASE_FB_URL + 'account_id' + REACTIONS_URL + 'AAA'
                m.register_uri('GET', request_url, status_code=200, content=json.dumps(
                    FACEBOOK_POSTS_ONE_RECORD_RAW_DATA).encode('utf-8'))
                fetch_posts(node_id='account_id', access_token='AAA')

        out_dicts = sysoutput_to_dicts(out)
        row_types = [x['type'] for x in out_dicts]
        # We have a state record type
        self.assertIn('STATE', row_types)

    def test_can_start_pulling_data_at_a_certain_page(self):
        out = io.StringIO()
        with requests_mock.Mocker() as m:
            # Our first request URL points at second_request_uri
            self.assertEqual(
                FACEBOOK_POSTS_ONE_RECORD_RAW_DATA['paging']['cursors']['after'],
                'after_cursor_ZZZ')
            first_request_url = (BASE_FB_URL + 'account_id' + REACTIONS_URL + 'AAA'
                                 '&after=after_cursor_YYY')
            m.register_uri(
                'GET', first_request_url, status_code=200, content=json.dumps(
                    FACEBOOK_POSTS_ONE_RECORD_RAW_DATA).encode('utf-8'))

            second_request_url = (BASE_FB_URL + 'account_id' + REACTIONS_URL + 'AAA'
                                  '&after=after_cursor_ZZZ')
            # Our second_request_uri does not have an after cursor marker
            m.register_uri(
                'GET', second_request_url, status_code=200, content=json.dumps(
                    FACEBOOK_LAST_PAGE_RECORD_RAW_DATA).encode('utf-8'))
            with self.assertRaises(KeyError):
                FACEBOOK_LAST_PAGE_RECORD_RAW_DATA['paging']['cursors']['after']

            # Fetch posts, with a cursor that points at our first URL
            with redirect_stdout(out):
                fetch_posts(node_id='account_id', access_token='AAA',
                            after_state_marker='after_cursor_YYY')

            out_dicts = sysoutput_to_dicts(out)
            # It recorded the state as expected
            row_messages = [x['record']['message']
                            for x in out_dicts if x['type'] == 'RECORD']
            state_record = [x for x in out_dicts if x['type'] == 'STATE'][0]
            # It fetched both of our messages
            self.assertIn(
                FACEBOOK_LAST_PAGE_RECORD_CLEAN_DATA['data'][0]['message'],
                row_messages)
            self.assertIn(
                FACEBOOK_POSTS_ONE_RECORD_CLEAN_DATA['data'][0]['message'],
                row_messages)
            # And recorded the state of the first call
            self.assertEqual(
                state_record['value']['after'],
                FACEBOOK_POSTS_ONE_RECORD_CLEAN_DATA['paging']['cursors']['after'])
