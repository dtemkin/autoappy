import requests

API_ROOT = "http://api.careerbuilder.com/"
API_SEARCH = {"url":"", "request_method":"GET", "required_params":[], "optional_params":[]}
API_JOB = {"url":"", "request_method":"GET", "required_params":[], "optional_params":[]}
API_APPLY = {"url":"", "request_method":"POST", "required_params":[], "optional_params":[]}
AUTH = {"DeveloperKey":""} # Enter DeveloperKey Here
DEFAULTS = {"outputjson":"true"}


class CareerbuilderException(Exception):
	pass
class SearchExeception(CareerbuilderException):
	pass
class JobException(CareerbuilderException):
	pass
class ApplyException(CareerbuilderException):
	pass



class CareerbuilderClient:
	
	def __init__(self, version=2):
		self.ver = "".join(["v",version])
		self.baseurl = "".join([API_ROOT, self.ver, "/"])
	
	def Search(self):
		pass
	
	def Job(self, srcid, url=None):
		pass
	
	def Apply(self):
		pass
	
	def _process_request(self, method, endpoint, args):
		pass
	
	def _validate_required(self, required_args, args):
		pass
	
	def _validate_optional(self, optional_args, args):
		pass
	
