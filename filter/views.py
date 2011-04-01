# Create your views here.

from django.http import HttpResponse
import urllib
import json
import yaml
import re
from django.conf import settings
from datetime import datetime
from django.template import Context, Template
from wsgiref.handlers import format_date_time

# From: http://stackoverflow.com/questions/275174/how-do-i-perform-html-decoding-encoding-using-python-django
from htmlentitydefs import name2codepoint
# for some reason, python 2.5.2 doesn't have this one (apostrophe)
name2codepoint['#39'] = 39

def unescapeHtml(s):
    "unescape HTML code refs; c.f. http://wiki.python.org/moin/EscapingHtml"
    return re.sub('&(%s);' % '|'.join(name2codepoint),
        lambda m: unichr(name2codepoint[m.group(1)]), s)

# TODO: attach valid rss http://feedvalidator.org emblem somewhere
# TODO: experiment with rss input box
# TODO: log hit stats, limit hits to conform to reddit api and be respectful etc.
# TODO: caching
# TODO: polymorphic OOP to support different feed sources (such as hacker news, techcrunch, etc.)

REDDIT_HOST = 'http://reddit.com'

def serializeFeeds(feeds):
    return reduce(lambda accum, feed: accum + feed['url'] + ' (' +
        str(feed['minScore']) + '), ', feeds, '');

# TODO: this should probably go into models
def redditRss(post):
    data = post['data']
    comments = int(data['num_comments'])
    score = int(data['score'])
    permalink = REDDIT_HOST + str(data['permalink'])
    contentUrl = str(data['url'])
    link = permalink if ((comments > 200) or (comments > score)) else contentUrl
    selfHtml = unescapeHtml(str(data['selftext_html'])) if data['selftext_html'] else ''

    return {
        'title': data['title'],
        'link': link,
        'description': '%d = %d - %d<br>\n'         % (score, data['ups'], data['downs']) +
            'From /r/%s<br>\n'                          % data['subreddit'] +
            '<a href="%s">[link]</a> '              % contentUrl +
            '<a href="%s">[%d comments]</a><br>\n'  % (permalink, comments) +
            selfHtml,
        'guid': permalink,
        'pubDate': format_date_time(data['created']),
    }

def returnRssFeed(request, bundle):
    # this is only configured for Reddit currently

    try:
        # TODO: this /home/dhu crap should be in settings.py or something
        feeds = yaml.load(open('/home/dhu/code/rssfilter/yaml/feeds.yaml',
                    'r').read())[0]['reddit'][bundle]
    except Exception as error:
        errorMsg = 'Unknown feed (or problem with feeds.yaml): ' + str(error)
        print(errorMsg)
        return HttpResponse(errorMsg)

    # Loop through each feed in the bundle, adding it to the list
    filtered = []
    for feed in feeds:
        # TODO: not just reddit...
        feedUrl = feed['url'] + '/.json'
        minScore = feed['minScore']

        try:
            fileStr = urllib.urlopen(feedUrl).read()
        except IOError as details:
            errorMsg = 'Cannot open url at \'' + feedUrl + '\''
            print(errorMsg)
            return HttpResponse(errorMsg)

        posts = json.loads(fileStr)['data']['children']
        # TODO: unused var
        subreddit = posts[0]['data']['subreddit']
        filtered += [redditRss(x) for x in posts if x['data']['score'] >= minScore]

    context = Context({
        'data': filtered,
        'title': bundle + ' - a filtered bundle',
        'description': 'A bundle of filtered feeds related to %s: %s' % (bundle, serializeFeeds(feeds)),
        # TODO: should not be hardcoded
        'link': request.get_host() + '/projects/rssfilter',
        'selfLink': request.build_absolute_uri(),
    })

    template = Template(open('/home/dhu/code/rssfilter/templates/rss.xml', 'r').read())
    feedXml = template.render(context)

    return HttpResponse(feedXml, mimetype='application/rss+xml')

def allFeeds(request):
    # TODO: use markdown to automatically convert from yaml to html lists
    feeds = yaml.load(open(settings.FS_ROOT + '/yaml/feeds.yaml', 'r').read())[0]
    context = Context({
        'data': feeds,
        'root': request.build_absolute_uri() + 'feed',
    })
    template = Template(open(settings.FS_ROOT + '/templates/all_feeds.html', 'r').read())
    return HttpResponse(template.render(context))
