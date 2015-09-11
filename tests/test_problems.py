import utils
import unittest

class Journal(unittest.TestCase):
	def setUp(self):
		self.startnum = 0
		self.skipnum = 1
	
	def tearDown(self):
		pass


	def test_problems(self):
		utils.whole_journal("tests/data_issues",
					 self.startnum,
					 1,
					 verbose=True,
					 errorfile="problems_parse_errors")
