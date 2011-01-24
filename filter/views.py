# Create your views here.

from django.http import HttpResponse

def returnRssFeed(request, feedName):
    #return HttpResponse(__args__)
    return HttpResponse("You want the feed for " + feedName)

