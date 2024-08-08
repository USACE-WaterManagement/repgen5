from queue import Queue

__version__ = "5.1.0"
# =========================================== #
#              THREADING VARS				  #
# =========================================== #
THREAD_COUNT = 15
THREAD_TIMEOUT = 120 # Seconds to consider thread is still alive
MAX_CALL_SIZE   = 200 # if the threads exceed this, kill it!
# =========================================== #
REPGEN_GITHUB_ISSUES_URL = "https://github.com/USACE-WaterManagement/repgen5/issues"
# CDA Constants 
PARAM_DT_FMT = "%Y-%m-%dT%H:%M:%S"
# =========================================== #
# Global Variables Shared Between Classes     #
# =========================================== #
queue = Queue()
threads = []
