# Create your views here.

from django.http import HttpResponse
import urllib
import json
import yaml
from datetime import datetime
from django.template import Context, Template
from wsgiref.handlers import format_date_time

# TODO: attach valid rss http://feedvalidator.org emblem somewhere


def returnRssFeed(request, feedUrl):
    #return HttpResponse(__args__)

    # this is only configured for Reddit currently
    try:
        fileStr = urllib.urlopen(feedUrl).read()
    except IOError as details:
        errorMsg = 'Cannot open url at \'' + feedUrl + '\''
        print(errorMsg)
        return HttpResponse(errorMsg)

    minScore = 50
    redditHost = 'http://reddit.com'

    try:
        posts = json.loads(fileStr)['data']['children']
        filtered = [{
            'title': x['data']['title'],
            'link': redditHost + x['data']['permalink'],
            'description': str(x['data']['score']) + '\t' +
                str(x['data']['num_comments']) + '\t' +
                str(x['data']['ups']) + '\t' +
                str(x['data']['downs']) + '\t' + x['data']['selftext'],
            'guid': redditHost + x['data']['permalink'],
            'pubDate': format_date_time(x['data']['created']),
            } for x in posts if x['data']['score'] >= minScore]

        subreddit = posts[0]['data']['subreddit']
        context = Context({
            'data': filtered,
            'title': '/r/' + subreddit + ' filtered - minimum score ' + str(minScore),
            'link': redditHost + '/r/' + subreddit,
            'selfLink': request.build_absolute_uri(),
        })
    except Exception as error:
        return HttpResponse(str(error))

    template = Template(open('templates/rss.xml', 'r').read())
    feedXml = template.render(context)

    return HttpResponse(feedXml, mimetype='application/rss+xml')
