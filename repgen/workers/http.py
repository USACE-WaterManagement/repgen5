from repgen import THREAD_TIMEOUT, PARAM_DT_FMT, MAX_CALL_SIZE, REPGEN_GITHUB_ISSUES_URL
import time
import json
import sys
from datetime import datetime, timedelta
import pytz
import signal
from ssl import SSLError
from repgen.data.value import ssl_ctx

import threading
import http.client as httplib, urllib.parse as urllib

def fetchTimeseriesCDA(v_self):
	"""
    Fetches time series data from CDA processes the results.

    This function constructs a time series name from various attributes of `v_self`, 
    handles time zone normalization, builds a request to fetch data from a specified CWMS Data API endpoint, 
    and retries the request if necessary. It processes the fetched data and stores it in in the passed in v_self (Value Class object).

    Args:
        v_self: An instance of a class that holds various attributes required for fetching 
                the time series data, including start and end times, database location, 
                parameter, type, interval, duration, version, time zone, units, paths, hosts, 
                connection, timeout, and other configurations.

    Returns:
        None

    Raises:
        AssertionError: If the start or end time is a naive datetime (i.e., without timezone info).
        Exception: Global handle if any error occurs during the data fetching process.
    """
	tz = v_self.dbtz
	units = v_self.dbunits
	ts_name = ".".join( (v_self.dbloc, v_self.dbpar, v_self.dbptyp, str(v_self.dbint), str(v_self.dbdur), v_self.dbver) )

	if v_self.start is None or v_self.end is None:
		return
	
	# Loop until we fetch some data, if missing is NOMISS
	retry_count = 10			# Go back at most this many weeks + 1
	sstart = tz.normalize(tz.localize(v_self.start)) if v_self.start.tzinfo is None else v_self.start
	send = tz.normalize(tz.localize(v_self.end)) if v_self.end.tzinfo is None else v_self.end
	path = v_self.path if not v_self.shared["use_alternate"] else v_self.altpath
	host = v_self.host if not v_self.shared["use_alternate"] else v_self.althost
	headers = { 'Accept': "application/json;version=2" }
	while(retry_count > 0):
		# Convert time to destination timezone
		# Should this actually convert the time to the destination time zone (astimezone), or simply swap the TZ (replace)?
		# 'astimezone' is be the "proper" behavior, but 'replace' mimics repgen_4.
		# This should *not* be a naive datetime
		assert sstart.tzinfo is not None, "Naive datetime; start time should contain timezone"
		assert send.tzinfo is not None, "Naive datetime; end time should contain timezone"
		start = sstart.astimezone(tz)
		end = send.astimezone(tz)
		
		params = urllib.urlencode( {
			"name": ts_name,
			"unit": units,
			"begin": start.strftime(PARAM_DT_FMT),
			"end":   end.strftime(PARAM_DT_FMT),
			"office": v_self.dbofc if v_self.dbofc is not None else "",
			"timezone": str(tz),
			"pageSize": -1,					# always fetch all results
		})

		sys.stderr.write(f"Getting {ts_name} from {start.strftime(PARAM_DT_FMT)} to {end.strftime(PARAM_DT_FMT)} in tz {tz}, with units {units}\n")

		try:
			data = None
			retry_until_alternate = 3
			while retry_until_alternate > 0:
				retry_until_alternate -= 1
				if path is None:
					path = ""

				query = f"/{path}/timeseries?"

				# The http(s) guess isn't perfect, but it's good enough. It's for display purposes only.
				print("Fetching: %s" % ("https://" if host[-2:] == "43" else "http://") + host+query+params, file=sys.stderr)

				try:
					if sys.platform != "win32" and v_self.timeout:
						# The SSL handshake can sometimes fail and hang indefinitely
						# inflate the timeout slightly, so the socket has a chance to return a timeout error
						# This is a failsafe to prevent a hung process
						signal.alarm(int(v_self.timeout * 1.1) + 1)

					if v_self._conn is None:
						try:
							from repgen.util.urllib2_tls import TLS1Connection
							v_self._conn = TLS1Connection( host, timeout=v_self.timeout, context=ssl_ctx )
							v_self._conn.request("GET", "/{path}" )
						except SSLError as err:
							print(type(err).__name__ + " : " + str(err), file=sys.stderr)
							print("Falling back to non-SSL", file=sys.stderr)
							# SSL not supported (could be standalone instance)
							v_self._conn = httplib.HTTPConnection( host, timeout=v_self.timeout )
							v_self._conn.request("GET", "/{path}" )

						# Test if the connection is valid
						v_self._conn.getresponse().read()
					
					# locals().update({'max_call_size': locals().get('max_call_size', 0) + 1})
					# print(locals().get("max_call_size"))
					# if int(locals().get("max_call_size")) > MAX_CALL_SIZE:
					# 	print(f"CALL STACK EXCEEDED. Submit ticket via: {REPGEN_GITHUB_ISSUES_URL}")
					# 	sys.exit(1)
					v_self._conn.request("GET", query+params, None, headers )
					r1 = v_self._conn.getresponse()

					# getresponse can also hang sometimes, so keep alarm active until after we fetch the response
					if sys.platform != "win32" and v_self.timeout:
						signal.alarm(0) # disable the alarm
					
					# Grab the charset from the headers, and decode the response using that if set
					# HTTP default charset is iso-8859-1 for text (RFC 2616), and utf-8 for JSON (RFC 4627)
					parts = r1.getheader("Content-Type").split(";")
					charset = "iso-8859-1" if parts[0].startswith("text") else "utf-8" # Default charset
					
					if len(parts) > 1:
						for prop in parts:
							prop_parts = prop.split("=")
							if len(prop_parts) > 1 and prop_parts[0].lower() == "charset":
								charset = prop_parts[1]

					data = r1.read().decode(charset)

					if r1.status == 200:
						break
					
					print("HTTP Error " + str(r1.status) + ": " + data, file=sys.stderr)
					if r1.status == 404:
						json.loads(data)
						# We don't care about the actual error, just if it's valid JSON
						# Valid JSON means it was a RADAR response, so we treat it as a valid response, and won't retry.
						break
				except (httplib.NotConnected, httplib.ImproperConnectionState, httplib.BadStatusLine, ValueError, OSError) as e:
					print(f"Error fetching: {e}", file=sys.stderr)
					if retry_until_alternate == 0 and v_self.althost is not None and host != v_self.althost:
						print("Trying alternate server", file=sys.stderr)
						v_self.shared["use_alternate"] = True
						(host, path) = (v_self.althost, v_self.altpath)
						v_self._conn = None
						retry_until_alternate = 3
					else:
						print("Reconnecting to server and trying again", file=sys.stderr)
						time.sleep(3)
						try:
							v_self._conn.close()
						except:
							pass
						v_self._conn = None
					continue

			data_dict = None

			try:
				data_dict = json.loads(data)
			except json.JSONDecodeError as err:
				print(str(err), file=sys.stderr)
				print(repr(data), file=sys.stderr)

			if data_dict.get("total", 0) > 0:
				for d in data_dict["values"]:
					# json returns times in javascript time,
					#  milliseconds since epoch, 
					# 	convert to unix time of seconds since epoch
					_t = float(d[0])/1000.0 
					_dt = datetime.fromtimestamp(_t,pytz.utc)
					_dt = _dt.astimezone(v_self.dbtz)
					if d[1] is not None:
						# does not currently implement text operations
						_v = float(d[1]) 
					else:
						_v = None
					_q = int(d[2])
					v_self.values.append( ( _dt,_v,_q  ) )
			else:
				print("No values were fetched.", file=sys.stderr)

			if v_self.ismissing():
				if v_self.missing == "NOMISS":
					sstart = sstart - timedelta(weeks=1)
					retry_count = retry_count - 1
					continue

			if v_self.time:
				v_self.type = "SCALAR"
				if v_self.missing == "NOMISS":
					# Get the last one, in case we fetched extra because of NOMISS
					for v in reversed(v_self.values):
						if v is not None and v[1] is not None:
							v_self.value = v[1]
							break
				elif len(v_self.values) > 0:
					v_self.value = v_self.values[-1][1]
		except Exception as err:
			print( repr(err) + " : " + str(err), file=sys.stderr )
		break

def processSiteWorker(queue):
	"""
	Process site worker function that continuously retrieves tasks from a queue and processes them.
	ALL of these will terminate gracefully when self.queue.join() is called at the end of report.py

	Parameters:
	queue (Queue): Queue process

	Returns:
	results (list)
	"""
	while True:
		value_self = queue.get(timeout=THREAD_TIMEOUT)
		# lock = threading.Lock()
		try:
			if value_self is None:
				break
			# lock.acquire()
			fetchTimeseriesCDA(value_self)
		except Exception as err:
			print( 'Thread Error:\n\t' + repr(err) + " : " + str(err), file=sys.stderr )
		finally:
			# lock.release()
			queue.task_done()