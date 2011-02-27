# Create your views here.

from django.http import HttpResponse
import urllib
import json
import yaml
from django.conf import settings
from datetime import datetime
from django.template import Context, Template
from wsgiref.handlers import format_date_time

# TODO: attach valid rss http://feedvalidator.org emblem somewhere
# TODO: experiment with rss input box
# TODO: log hit stats, limit hits to conform to reddit api and be respectful etc.
# TODO: caching

REDDIT_HOST = 'http://reddit.com'

def serializeFeeds(feeds):
    return reduce(lambda accum, feed: accum + feed['url'] + ' (' +
        str(feed['minScore']) + '), ', feeds, '');

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
        filtered += [{
            'title': x['data']['title'],
            'link': REDDIT_HOST + x['data']['permalink'],
            'description': str(x['data']['score']) + ' = ' +
                str(x['data']['ups']) + ' - ' +
                str(x['data']['downs']) + '  |  ' +
                str(x['data']['num_comments']) + '<br><br>\n' +
                'From <a href="' + str(feed['url']) + '">' +
                feed['url'] + '</a><br>' +
                '<a href="' + str(x['data']['url']) + '">' +
                str(x['data']['url']) + '</a><br>' +
                (str(x['data']['selftext_html']) if x['data']['selftext_html'] else ''),
            'guid': REDDIT_HOST + x['data']['permalink'],
            'pubDate': format_date_time(x['data']['created']),
            } for x in posts if x['data']['score'] >= minScore]

    context = Context({
        'data': filtered,
        'title': bundle + ' - a filtered bundle',
        'description': 'A bundle of filtered feeds related to ' + bundle +':' +
            serializeFeeds(feeds),
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



