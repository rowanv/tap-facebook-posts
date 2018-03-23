from unittest import TestCase

from ..fetch_facebook_posts_data import read_configs


class TestFetchFacebookPostsData(TestCase):

	def test_can_fetch_facebook_posts_data(self):
		configs = read_configs()
		print(configs)
		self.assertFalse(configs)
