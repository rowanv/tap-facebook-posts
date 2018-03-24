"""
from unittest import TestCase
import argparse

from .. import create_parser


class TestTapValid(TestCase):

	def setUp(self):
		self.parser = create_parser()

	def test_can_call_tap_through_command_line(self):
		parsed = self.parser.parse_args(['--config', 'config.json'])
		self.assertTrue(parsed)
"""