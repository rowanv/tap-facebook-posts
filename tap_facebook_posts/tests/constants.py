
BASE_FB_URL = 'https://graph.facebook.com/v2.11/'
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


# Create the test values that the API must return. We dynamically create
# the reactions variables for both a RAW_DATA variable that simulates the
# raw data returned by the API, and a CLEAN_DATA variable that simulates
# the flattened data that our module returns


SAMPLE_COUNT = {
    "data": [
    ],
    "summary": {
        "total_count": 566,
        "viewer_reaction": "NONE"
    }
}


FACEBOOK_POSTS_ONE_RECORD_DATA = {
    'data': [{
        'created_time': '2018-03-19T18:17:00+0000',
        'message': 'This is a test message',
        'id': '11239244970_10150962953494971',
        "comment_count": {
            "data": [
            ],
            "summary": {
                "order": "ranked",
                "total_count": 7,
                "can_comment": True
            }
        },
    }, ],
    'paging': {
        'cursors': {'before': 'before_cursor_AAA', 'after': 'after_cursor_ZZZ'},
        'next': 'https://graph.facebook.com/v2.11/11239244970/feed?access_token=AAA'}
}

# Add in the reactions
REACTION_LABELS = [
    'none_reaction_count', 'sad_count', 'like_count', 'love_count',
    'pride_count', 'total_reaction_count', 'haha_count', 'wow_count',
    'thankful_count', 'angry_count'
]

FACEBOOK_POSTS_ONE_RECORD_RAW_DATA = dict(FACEBOOK_POSTS_ONE_RECORD_DATA)
FACEBOOK_POSTS_ONE_RECORD_CLEAN_DATA = dict(FACEBOOK_POSTS_ONE_RECORD_DATA)

for reaction in REACTION_LABELS:

    FACEBOOK_POSTS_ONE_RECORD_RAW_DATA['data'][0][reaction] = SAMPLE_COUNT
    FACEBOOK_POSTS_ONE_RECORD_CLEAN_DATA['data'][0][reaction] = 400
FACEBOOK_POSTS_ONE_RECORD_CLEAN_DATA['data'][0]['comment_count'] = 7

FACEBOOK_LAST_PAGE_RECORD_DATA = {
    'data': [{
        'created_time': '2018-03-19T18:17:00+0000',
        'message': 'This is a the last page record message',
        'id': '11239244970_10150962953494971'}, ],
    "comment_count": {
        "data": [
        ],
        "summary": {
            "order": "ranked",
            "total_count": 7,
            "can_comment": True
        }
    },
    'paging': {
        'cursors': {'before': 'before_cursor_BBB'}, }
}

FACEBOOK_LAST_PAGE_RECORD_CLEAN_DATA = FACEBOOK_LAST_PAGE_RECORD_DATA.copy()
FACEBOOK_LAST_PAGE_RECORD_RAW_DATA = FACEBOOK_LAST_PAGE_RECORD_DATA.copy()

for reaction in REACTION_LABELS:
    FACEBOOK_LAST_PAGE_RECORD_CLEAN_DATA['data'][0][reaction] = 400
    FACEBOOK_LAST_PAGE_RECORD_RAW_DATA['data'][0][reaction] = SAMPLE_COUNT
FACEBOOK_LAST_PAGE_RECORD_CLEAN_DATA['data'][0]['comment_count'] = 7


FACEBOOK_POSTS_MULT_RECORD_DATA = {
    'data': [{
        'created_time': '2018-03-19T18:17:00+0000',
        'message': 'This is a test message',
        'id': '11239244970_10150962953494971',
    }, {
        'created_time': '2018-03-19T18:17:00+0000',
        'message': 'This is a anothertest message',
        'id': '11239244970_10150962953494111',
        "comment_count": {
            "data": [
            ],
            "summary": {
                "order": "ranked",
                "total_count": 7,
                "can_comment": True
            }
        },
    }],
    'paging': {
        'cursors': {'before': 'before_cursor_AAA', 'after': 'after_cursor_ZZZ'},
        'next': BASE_FB_URL + '11239244970' + REACTIONS_URL + 'AAA'}
}

FACEBOOK_POSTS_MULT_RECORD_RAW_DATA = FACEBOOK_POSTS_MULT_RECORD_DATA.copy()
FACEBOOK_POSTS_MULT_RECORD_CLEAN_DATA = FACEBOOK_POSTS_MULT_RECORD_DATA.copy()

for reaction in REACTION_LABELS:
    FACEBOOK_POSTS_MULT_RECORD_RAW_DATA['data'][0][reaction] = SAMPLE_COUNT
    FACEBOOK_POSTS_MULT_RECORD_RAW_DATA['data'][1][reaction] = SAMPLE_COUNT
    FACEBOOK_POSTS_MULT_RECORD_CLEAN_DATA['data'][0][reaction] = 400
    FACEBOOK_POSTS_MULT_RECORD_CLEAN_DATA['data'][1][reaction] = 400
FACEBOOK_POSTS_MULT_RECORD_CLEAN_DATA['data'][0]['comment_count'] = 7
FACEBOOK_POSTS_MULT_RECORD_CLEAN_DATA['data'][1]['comment_count'] = 7
