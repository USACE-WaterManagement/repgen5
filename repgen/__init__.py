__version__ = "5.1.0"
# =========================================== #
#              THREADING VARS				  #
# =========================================== #
THREAD_COUNT = 15
THREAD_TIMEOUT = 30 # Seconds to consider thread is still alive
# =========================================== #
REPGEN_GITHUB_ISSUES_URL = "https://github.com/USACE-WaterManagement/repgen5/issues"
# CDA Constants 
PARAM_DT_FMT = "%Y-%m-%dT%H:%M:%S"
# =========================================== #
# Global Variables Shared Between Classes     #
# =========================================== #
threads = []
queue = None