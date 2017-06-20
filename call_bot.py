import urllib2
import urllib
import sys

# WARNING: just an example

data = dict(req=sys.argv[1])
data = urllib.urlencode(data)
req = urllib2.Request('http://slack-bot.iquality.it/itop-bot/tickets/new', data)
res = urllib2.urlopen(req)
