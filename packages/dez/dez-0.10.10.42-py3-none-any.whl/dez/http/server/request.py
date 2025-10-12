import rel, os
from dez.io import locz
from dez.http.errors import HTTPProtocolError

class HTTPRequest(object):
    id = 0
    def __init__(self, conn):
        HTTPRequest.id += 1
        self.id = HTTPRequest.id
        self.log = conn.get_logger("HTTPRequest(%s)"%(self.id,))
        self.log.debug("__init__")
        self.shield = conn.shield
        self.conn = conn
        self.ip = conn.ip
        self.real_ip = conn.real_ip
        self.state = 'action'
        self.headers = {}
        self.case_match_headers = {}
        self.headers_complete = False
        self.write_ended = False
        self.send_close = False
        self.red_flags = []
        self.body = None
        self.body_cb = None
        self.body_stream_cb = None
        self.remaining_content = 0
        self.pending_actions = []
        self.set_close_cb(self._onclose, [])

    def __repr__(self):
        return "<HTTPRequest(%s)>"%(self.id,)

    def process(self):
        self.log.debug("process", self.state)
        return getattr(self, 'state_%s' % (self.state,), lambda : None)()

    def _onclose(self):
        self.write_ended = True

    def set_close_cb(self, cb, args):
        self.conn.set_close_cb(cb, args)

    def state_action(self):
#        print(self.conn.buffer.get_value())
        if '\r\n' not in self.conn.buffer:
            return False
        i = self.conn.buffer.find('\r\n')
        self.action = self.conn.buffer.part(0, i)
        self.log.debug("state_action", self.action)
        try:
            self.method, self.url, self.protocol = self.action.split(' ', 2)
            if "%0D+" in self.url:
                self.log.access("stripping carriage return from url: %s"%(self.url,))
                self.url = self.url.replace("%0D+", "")
            p, qs = self.url, ""
            if "?" in self.url:
                p, qs = self.url.split("?")
            os.environ.update(PATH_INFO=p, QUERY_STRING=qs)
            url_scheme, version = self.protocol.split('/',1)
            major, minor = version.split('.', 1)
            self.version_major = int(major)
            self.version_minor = int(minor)
            self.url_scheme = url_scheme.lower()
        except Exception as e:
            self.log.error("state_action", "Exception", e)
            bv = self.conn.buffer.get_value()
            if hasattr(bv, "decode"):
                self.log.error("decode()ing buffer...")
                bv = bv.decode(errors='replace')
            self.log.error(bv)
            if self.shield:
                self.flag("%s (action: '%s')"%(e, self.action))
            else:
                return self.close_now()
#            raise HTTPProtocolError, "Invalid HTTP status line"
        #self.protocol = self.protocol.lower()
        self.conn.buffer.move(i+2)
        self.state = 'headers'
        self.log.debug("state_action", self.action)
        return self.state_headers()

    def flag(self, reason):
        self.log.error("request flagged:", reason)
        self.red_flags.append(reason)

    def abort(self):
        rf = "; ".join(self.red_flags)
        self.shield.suss(self.real_ip, rf)
        self.log.error("request aborting:", rf)
        self.close_now()

    def check_headers(self):
        if not self.shield:
            return
        for header in ["cookie", "user-agent"]:
            val = self.headers.get(header)
            if val and self.shield.path(val, allow=header):
                self.flag("sketchy %s ('%s')"%(header, val))

    def state_headers(self):
        while True:
            index = self.conn.buffer.find('\r\n')
            if index == -1:
                if self.red_flags and self.real_ip not in locz:
                    self.abort()
                return False
            if index == 0:
                self.conn.buffer.move(2)
                self.content_length = int(self.headers.get('content-length', '0'))
                self.headers_complete = True
                self.state = 'waiting'
                self.log.debug("waiting", self.content_length)
                self.check_headers()
                if self.red_flags:
                    return self.abort()
                else:
                    self.conn.route(self)
                    return True
            try:
                key, value = self.conn.buffer.part(0, index).split(': ', 1)
                if key == "drp_ip" and self.ip in locz:
                    self.real_ip = self.conn.real_ip = value
            except ValueError as e:
                self.log.debug("state_headers", "ValueError", e)
                return self.close_now()
#                raise HTTPProtocolError, "Invalid HTTP header format"
            self.headers[key.lower()] = value
            self.case_match_headers[key] = key
            self.conn.buffer.move(index+2)

    def state_waiting(self):
        self.log.debug("WAITING", self.state, "(probably shouldn't happen...)")

    def read_body(self, cb, args=[]):
        self.log.debug("read_body", self.state, self.content_length)
        self.body_cb = cb, args
        self.state = 'body'
        self.remaining_content = self.content_length
        if self.remaining_content == 0:
            return self.complete()
        self.conn.read_body()
        return self.state_body()

    def read_body_stream(self, stream_cb, args=[]):
        self.remaining_content = self.content_length
        self.body_stream_cb = stream_cb, args
        self.state = 'body'
        self.conn.read_body()
        return self.state_body()

    def state_body(self):
        buf = self.conn.buffer
        blen = len(buf)
        self.log.debug("state_body", "clen:", self.content_length, "blen:", blen)
        if self.body_stream_cb:
            bytes_available = min(blen, self.remaining_content)
            self.log.debug("state_body", "available:", bytes_available, "remaining:", self.remaining_content)
            self.remaining_content -= bytes_available
            cb, args = self.body_stream_cb
            cb(buf.part(0, bytes_available), *args)
            buf.move(bytes_available)
        # Quick hack to fix body bug. TODO: clean up this whole function.
        elif blen >= self.content_length:
            self.log.debug("state_body", "len(buff) >= clen")
            self.remaining_content = 0
        elif blen >= self.content_length - 40: # this part is highly questionable!!!
            self.log.debug("state_body", "close - checking encode()d")
            try:
                if len(buf.data.encode()) == self.content_length:
                    self.log.debug("state_body", "passed encode()d clen check")
                    self.remaining_content = 0
            except:
                pass
        if self.remaining_content == 0:
            return self.complete()

    def complete(self):
        self.log.debug("complete")
        self.conn.complete()
        self.state = 'write'
        if self.body_stream_cb:
            cb, args = self.body_stream_cb
            self.log.debug("firing body_stream callback", str(cb))
            cb("", *args)
        elif self.body_cb:
            cb, args = self.body_cb
            self.log.debug("firing body callback", str(cb))
            d = self.conn.buffer.part(0, self.content_length)
            self.conn.buffer.move(self.content_length)
            if cb:
                cb(d, *args)
        self.state_write()

    def state_write(self):
        self.log.debug("state_write", self.state, self.pending_actions)
        while len(self.pending_actions):
            mode, data, cb, args, eb, ebargs = self.pending_actions.pop(0)
            if mode == "write":
                self.write(data, cb, args, eb, ebargs)
            elif len(self.pending_actions):
                self.log.error("state_write - skipping:", mode)
            else:
                if mode == "end":
                    self.end(cb, args)
                elif mode == "close":
                    self.close(cb, args)

    def write(self, data, cb=None, args=[], eb=None, ebargs=[], override=False):
        self.log.debug("write", self.state, len(data))
        if self.write_ended and not override:
            self.log.debug("WRITE", "tried to write:", data)
            return self.log.error("WRITE", "end already called")
        if self.state != 'write':
            self.log.error("write - state is not 'write'", self.state)
            if self.state == "closed":
                return self.log.error("WRITE", "state is closed - can't write %s bytes"%(len(data),));
            self.pending_actions.append(("write", data, cb, args, eb, ebargs))
            if self.state == 'waiting':
                self.log.error("write - changing state to body")
                self.state = 'body'
            self.log.error("calling process() from write()")
            return self.process()
        if len(data) == 0:
            return cb and cb(*args)
        self.conn.write(data, self.write_cb, (cb, args), eb, ebargs)

    def write_cb(self, cb=None, args=[]):
        self.log.debug("write_cb", self.write_ended, cb)
        if cb:
            cb(*args)
        if self.write_ended and not self.conn.wevent.pending():
            self._close()

    def _close(self, reason=None):
        self.conn.counter.dec("requests")
        if self.send_close:
            self.log.debug("_close", "closing!!")
            self.conn.close(reason)
        else:
            self.log.debug("_close", "restarting!!")
            self.conn.start_request()

    def dereference(self):
        self.body_stream_cb = None
        self.body_cb = None
        self.conn = None
        self.state = "closed"

    def end(self, cb=None, args=[]):
        self.log.debug("end", self.write_ended, self.state)
        if self.write_ended:
            return self.log.debug("END", "end already called", "(it's fine)")
        if self.state != "write":
            self.log.error("END", "postponing -", "state (", self.state, ") not write!")
            self.pending_actions.append(("end", None, cb, args, None, None))
            return
        self.state = "ended"
        self.write_ended = True
        self.conn.write("", self.write_cb, (cb, args))

    def close(self, cb=None, args=[], hard=False):
        self.log.debug("close", self.write_ended, self.state, hard)
        if hard or self.state == "action":
            self.send_close = True
            return self._close()
        if self.write_ended:
            return self.log.error("CLOSE", "end already called")
        if self.state != "write":
            self.log.error("CLOSE", "postponing -","state (", self.state, ") not write!")
            return self.pending_actions.append(("close", None, cb, args, None, None))
        self.send_close = True
        self.end(cb, args)

    def close_now(self, reason="hard close"):
        self.conn.buffer.exhaust()
        self.send_close = True
        self._close(reason)