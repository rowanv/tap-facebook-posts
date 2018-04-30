import os
import json
import datetime

import requests
import singer


MAX_REQUEST_ITERATIONS = 50
BASE_FACEBOOK_GRAPH_API_URL = 'https://graph.facebook.com/v2.11/'
REACTIONS_URL = (
    '/posts?fields=created_time,story,message,'
    'reactions.limit(0).summary(1).as(total_reaction_count),'
    'reactions.type(NONE).limit(0).summary(1).as(none_reaction_count),'
    'reactions.type(LIKE).limit(0).summary(1).as(like_count),'
    'reactions.type(LOVE).limit(0).summary(1).as(love_count),'
    'reactions.type(HAHA).limit(0).summary(1).as(haha_count),'
    'reactions.type(WOW).limit(0).summary(1).as(wow_count),'
    'reactions.type(SAD).limit(0).summary(1).as(sad_count),'
    'reactions.type(ANGRY).limit(0).summary(1).as(angry_count),'
    'reactions.type(THANKFUL).limit(0).summary(1).as(thankful_count),'
    'reactions.type(PRIDE).limit(0).summary(1).as(pride_count),'
    'comments.limit(0).summary(1).as(comment_count)'
    '&limit=100&access_token='
)


def get_abs_path(path):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), path)


def load_schema(entity):
    return singer.utils.load_json(get_abs_path(
                                  "schemas/{}.json".format(entity)))


def format_datetime_string(original_dt):
    """Convert datetime into formatted string that is compatible w/ Singer spec.
    """
    FB_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S+%f"
    TARGET_DATETIME_PARSE = "%Y-%m-%dT%H:%M:%SZ"
    dt = datetime.datetime.strptime(original_dt, FB_DATETIME_FORMAT)
    return dt.strftime(TARGET_DATETIME_PARSE)


def fetch_node_feed(node_id, access_token, *, after_state_marker=None):
    """Fetch the feed with all Post nodes for a given node.

    For more info, see
        https://developers.facebook.com/docs/graph-api/using-graph-api/

    node_id: str or int, unique identifier for a given node.
    access_token: str, access token to Facebook Graph API
    after_state_marker: If provided, will only fetch posts after that marker.
    """
    base_url = (BASE_FACEBOOK_GRAPH_API_URL + str(node_id) +
                REACTIONS_URL + access_token)
    if not after_state_marker:
        url = base_url
    else:
        url = base_url + '&after=' + after_state_marker
    response = requests.get(url)
    if response.status_code == 200:
        return json.loads(response.content.decode('utf-8'))
    else:
        error_message = (str(response.status_code) + ' Client Error: ' +
                         response.content.decode('utf-8'))
        raise requests.exceptions.HTTPError(error_message)


def clean_reactions_data(record):
    # Flatten the reactions data
    reactions = [
        'none_reaction_count', 'sad_count', 'like_count', 'love_count',
        'pride_count', 'total_reaction_count', 'haha_count', 'wow_count',
        'thankful_count', 'angry_count', 'comment_count',
    ]
    for key, value in record.items():
        if key in reactions:
            try:
                record[key] = record[key]['summary']['total_count']
            except TypeError:
                pass  # record is already clean
    return record


def write_records(data):
    for record in data:
        record['created_time'] = format_datetime_string(record['created_time'])
        record = clean_reactions_data(record)
        singer.write_record('facebook_posts', record)


def fetch_posts(node_id, access_token, after_state_marker=None):
    """Fetches all posts for a given node.

    node_id:  str or int, unique identifier for a given node.
    access_token: str, access token to Facebook Graph API
    after_state_marker: If provided, will only fetch posts after that marker.
    """
    current_state_marker = after_state_marker
    request_iterations_count = MAX_REQUEST_ITERATIONS
    schema = load_schema("facebook_posts")
    singer.write_schema("facebook_posts", schema, key_properties=["id"])

    node_feed = fetch_node_feed(node_id, access_token, after_state_marker=after_state_marker)
    write_records(node_feed['data'])
    try:
        while node_feed['paging']['cursors']['after'] and request_iterations_count:
            response_after_state_marker = node_feed['paging']['cursors']['after']
            # Did we already fetch the reponse marked by this state marker?
            if current_state_marker != response_after_state_marker:
                singer.write_state({'after': response_after_state_marker})
                node_feed = fetch_node_feed(
                    node_id, access_token,
                    after_state_marker=response_after_state_marker)
                write_records(node_feed['data'])
                request_iterations_count -= 1
            else:
                break
    except KeyError:
        pass
