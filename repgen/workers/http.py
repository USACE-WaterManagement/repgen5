from repgen import THREAD_TIMEOUT, PARAM_DT_FMT
import time
import json
import sys
import threading
from datetime import datetime, timedelta
import pytz
import signal
from ssl import SSLError
from repgen.data.value import ssl_ctx

import http.client as httplib, urllib.parse as urllib

def processSiteWorker(queue, tid, results):
	"""
	Process site worker function that continuously retrieves tasks from a queue and processes them.
	These will terminate gracefully when q.join() is called.

	Parameters:
	queue (Queue): Queue process
	tid (int): The thread ID
	results (list): List of results to be returned

	Returns:
	results (list)
	"""
	while True:
		self = queue.get(timeout=THREAD_TIMEOUT)
		print(self)
		lock = threading.Lock()
		try:
			lock.acquire()
			tz = self.dbtz
			units = self.dbunits
			ts_name = ".".join( (self.dbloc, self.dbpar, self.dbptyp, str(self.dbint), str(self.dbdur), self.dbver) )

			if self.start is None or self.end is None:
				return
			
			# Loop until we fetch some data, if missing is NOMISS
			retry_count = 10			# Go back at most this many weeks + 1
			sstart = tz.normalize(tz.localize(self.start)) if self.start.tzinfo is None else self.start
			send = tz.normalize(tz.localize(self.end)) if self.end.tzinfo is None else self.end

			path = self.path if not self.shared["use_alternate"] else self.altpath
			host = self.host if not self.shared["use_alternate"] else self.althost
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
					"office": self.dbofc if self.dbofc is not None else "",
					"timezone": str(tz),
					"pageSize": -1,					# always fetch all results
				})

				#sys.stderr.write(f"Getting {ts_name} from {start.strftime(PARAM_DT_FMT)} to {end.strftime(PARAM_DT_FMT)} in tz {tz}, with units {units}\n")

				try:
					data = None
					retry_until_alternate = 3
					while retry_until_alternate > 0:
						retry_until_alternate -= 1
						if path is None:
							path = ""

						query = f"/{path}/timeseries?"

						# The http(s) guess isn't perfect, but it's good enough. It's for display purposes only.
						#print("Fetching: %s" % ("https://" if host[-2:] == "43" else "http://") + host+query+params, file=sys.stderr)

						try:
							if sys.platform != "win32" and self.timeout:
								# The SSL handshake can sometimes fail and hang indefinitely
								# inflate the timeout slightly, so the socket has a chance to return a timeout error
								# This is a failsafe to prevent a hung process
								signal.alarm(int(self.timeout * 1.1) + 1)

							if self._conn is None:
								try:
									from repgen.util.urllib2_tls import TLS1Connection
									self._conn = TLS1Connection( host, timeout=self.timeout, context=ssl_ctx )
									self._conn.request("GET", "/{path}" )
								except SSLError as err:
									print(type(err).__name__ + " : " + str(err), file=sys.stderr)
									print("Falling back to non-SSL", file=sys.stderr)
									# SSL not supported (could be standalone instance)
									self._conn = httplib.HTTPConnection( host, timeout=self.timeout )
									self._conn.request("GET", "/{path}" )

								# Test if the connection is valid
								self._conn.getresponse().read()

							self._conn.request("GET", query+params, None, headers )
							r1 = self._conn.getresponse()

							# getresponse can also hang sometimes, so keep alarm active until after we fetch the response
							if sys.platform != "win32" and self.timeout:
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
							if retry_until_alternate == 0 and self.althost is not None and host != self.althost:
								print("Trying alternate server", file=sys.stderr)
								self.shared["use_alternate"] = True
								(host, path) = (self.althost, self.altpath)
								self._conn = None
								retry_until_alternate = 3
							else:
								print("Reconnecting to server and trying again", file=sys.stderr)
								time.sleep(3)
								try:
									self._conn.close()
								except:
									pass
								self._conn = None
							continue

					data_dict = None

					try:
						data_dict = json.loads(data)
					except json.JSONDecodeError as err:
						print(str(err), file=sys.stderr)
						print(repr(data), file=sys.stderr)

					# get the depth
					prev_t = 0
					#print repr(data_dict)

					if data_dict.get("total", 0) > 0:
						for d in data_dict["values"]:
							_t = float(d[0])/1000.0 # json returns times in javascript time, milliseconds since epoch, convert to unix time of seconds since epoch
							_dt = datetime.fromtimestamp(_t,pytz.utc)
							_dt = _dt.astimezone(self.dbtz)
							#_dt = _dt.replace(tzinfo=self.tz)
							#print("_dt: %s" % repr(_dt))
							#print _dt
							if d[1] is not None:
								#print("Reading value: %s" % d[1])
								_v = float(d[1]) # does not currently implement text operations
							else:
								_v = None
							_q = int(d[2])
							self.values.append( ( _dt,_v,_q  ) )
					else:
						print("No values were fetched.", file=sys.stderr)

					if self.ismissing():
						if self.missing == "NOMISS":
							sstart = sstart - timedelta(weeks=1)
							retry_count = retry_count - 1
							continue

					if self.time:
						self.type = "SCALAR"
						if self.missing == "NOMISS":
							# Get the last one, in case we fetched extra because of NOMISS
							for v in reversed(self.values):
								if v is not None and v[1] is not None:
									self.value = v[1]
									break
						elif len(self.values) > 0:
							self.value = self.values[-1][1]

				except Exception as err:
					print( repr(err) + " : " + str(err), file=sys.stderr )
				print("Done!")
				break
		except KeyboardInterrupt:
			print(f"Thread #{tid} received KeyboardInterrupt. Exiting...")
		except Exception as err:
			print( repr(err) + " : " + str(err), file=sys.stderr )
		finally:
			lock.release()
			queue.task_done()
			

