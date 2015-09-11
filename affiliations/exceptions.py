class AffiliationsError(Exception):
	"""
	Generic class for module exceptions
	"""
	
class ParseError(AffiliationsError):
	"""
	Generic class for parsing errors
	"""	
	
class AuthorParsingError(ParseError):
	"""
	Error in parsing author information
	"""

	
class AddressParsingError(ParseError):
	"""
	Error in parsing address information
	"""
	
class ArticleParsingError(ParseError):
	"""
	Error in parsing article information
	"""

class IntegrityError(AffiliationsError):
	"""
	Generic Class for Data Integrity Issues
	"""

class CorrespondingAuthorError(IntegrityError):
	"""
	Failure to identify a corresponding author
	"""

