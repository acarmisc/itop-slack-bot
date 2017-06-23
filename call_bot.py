import urllib2
import urllib
import sys

data = dict(req=sys.argv[1])
url = 'http://slack-bot.iquality.it/itop-bot/tickets/new'
req = urllib2.Request(url, urllib.urlencode(data))
urllib2.urlopen(req)

print 0
