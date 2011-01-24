from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    #(r'^rssfilter/', include('rssfilter.foo.urls')),
    (r'^feed/(?P<feedUrl>.+)$', 'filter.views.returnRssFeed'),
    #(r'^(?P<feedName>\w+)\.rss$', 'filter.views.returnRssFeed'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)
