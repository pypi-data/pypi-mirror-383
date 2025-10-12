import re, sys
from dez.logging import default_get_logger
from functools import cmp_to_key
if sys.version_info > (3, 0):
    def cmp(v1, v2):
        if (v1 < v2):
            return -1
        elif (v1 == v2):
            return 0
        elif (v1 > v2):
            return 1
from dez.http.server.shield import Shield
from dez.io import locz

class Router(object):
    def __init__(self, default_cb, default_args=[], roll_cb=None, rollz={}, get_logger=default_get_logger, whitelist=[], blacklist={}, shield=False):
        self.log = get_logger("Router")
        self.default_cb = default_cb
        self.default_args = default_args
        self.roll_cb = roll_cb
        self.rollz = rollz
        self.set_whitelist(whitelist)
        self.blacklist = blacklist
        self.prefixes = []
        self.regexs = []
        self.shield = shield
        if shield:
            if type(shield) == bool:
                self.shield = Shield(blacklist, get_logger)
            else:
                self.blacklist = self.shield.blacklist

    def set_whitelist(self, whitelist):
        self.wildlist = []
        self.whitelist = []
        for ip in whitelist:
            if ip.endswith("*"):
                self.wildlist.append(ip.strip("*"))
            else:
                self.whitelist.append(ip)

    def register_cb(self, signature, cb, args):
        if "*" in signature: # write better regex detection...
            self.register_regex(signature, cb, args)
        else:
            self.register_prefix(signature, cb, args)

    def register_regex(self, restr, cb, args):
        self.regexs.append((re.compile(restr), cb, args))
        self.regexs.sort(key=cmp_to_key(self.regex_order))

    def register_prefix(self, prefix, cb, args):
        self.prefixes.append((prefix, cb, args))
        self.prefixes.sort(key=cmp_to_key(self.pref_order))

    def regex_order(self, b, a):
        return cmp(len(a[0].pattern),len(b[0].pattern))

    def pref_order(self, b, a):
        return cmp(len(a[0]),len(b[0]))

    def _denied(self, ip, url, ref):
        self.log.access("roll check!\nurl: %s\nreferer: %s\nip: %s"%(url, ref, ip))
        if self.whitelist or self.wildlist:
            if ip in self.whitelist:
                self.log.access("%s in whitelist"%(ip,))
                return False
            elif self.wildlist:
                for wild in self.wildlist:
                    if ip.startswith(wild):
                        self.log.access("%s matches %s in wildlist"%(ip, wild))
                        return False
            return True
        if self.blacklist and ip in self.blacklist:
            self.log.access("%s in blacklist"%(ip,))
            return True
        for flag, domain in list(self.rollz.items()):
            if url.startswith(flag):
                if not ref or domain not in ref:
                    return True

    def _check(self, url, req=None):
        if req and (self.shield or self.whitelist or self.blacklist or self.rollz):
            ip = req.real_ip
            if self.shield:
                if ip in locz:
                    self.log.access("skipping shield for local IP (1st proxied request)")
                else:
                    self.log.access("checking shield: %s"%(ip,))
                    self.shield(url, ip)
            if self._denied(ip, url, req.headers.get("referer", "")):
                return self.roll_cb, []
            self.log.access("passed!")
        for rx, cb, args in self.regexs:
            if rx.match(url):
                return cb, args
        for prefix, cb, args in self.prefixes:
            if url.startswith(prefix):
                return cb, args

    def _try_index(self, url):
        return self._check(url + "index.html")

    def __call__(self, req):
        url = req.url
        match = self._check(url, req) or self._try_index(url)
        if match:
            return match[0], match[1]
        return self.default_cb, self.default_args
