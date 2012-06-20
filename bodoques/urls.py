from django.conf.urls.defaults import patterns, include, url
import settings
import os

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    (r'^api/time/$', 'history.views.user_time'),
    (r'^api/time/add/$', 'history.views.add_user_time'),
    (r'^api/dash/(?P<user_id>[\d\w]+)/$', 'history.views.user_dash')
    # Examples:
    # url(r'^$', 'bodoques.views.home', name='home'),
    # url(r'^bodoques/', include('bodoques.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)

if settings.USE_DJANGO_SERVER:
    urlpatterns.extend(patterns('',
        (r'^site/(?P<path>.*)$', 'django.views.static.serve', {'document_root': os.path.dirname(os.path.realpath(__file__)) + '/site'})
    ))

