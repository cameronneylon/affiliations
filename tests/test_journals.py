import utils
import unittest

class Journal(unittest.TestCase):
	def setUp(self):
		self.startnum = 0
		self.skipnum = 1
	
	def tearDown(self):
		pass



	def test_compbio(self):
		utils.whole_journal("data/plos-journals-xml/PLoS_Comput_Biol",
					 self.startnum,
					 self.skipnum,
					 "pcbio_parse_errors")
				 
	def test_genetics(self):
		utils.whole_journal("data/plos-journals-xml/PLoS_Genet",
					 self.startnum,
					 self.skipnum,
					 "pgen_parse_errors")

	def test_ntds(self):
		utils.whole_journal("data/plos-journals-xml/PLoS_Negl_Trop_Dis",
					 self.startnum,
					 self.skipnum,
					 "pntds_parse_errors",)
				 
	def test_pathogens(self):
		utils.whole_journal("data/plos-journals-xml/PLoS_Pathog",
					 self.startnum,
					 self.skipnum,
					 "ppat_parse_errors",)

	def test_bio(self):
		utils.whole_journal("data/plos-journals-xml/PLoS_Biol",
					 self.startnum,
					 self.skipnum,
					 "bio_parse_errors",)
				 
	def test_med(self):
		utils.whole_journal("data/plos-journals-xml/PLoS_Med",
					 self.startnum,
					 self.skipnum,
					 "med_parse_errors",)


# 	def test_one(self):
# 		for start in range(0, 120000, 5000):
# 			utils.whole_journal("data/plos-one-xml/",
# 								start,
# 								self.skipnum,
# 								"one_parse_errors)    