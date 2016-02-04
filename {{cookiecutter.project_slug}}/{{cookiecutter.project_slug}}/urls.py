from django.conf.urls import *  # NOQA
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
import django.contrib.sitemaps.views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
import django.views.static

from cms.sitemaps import CMSSitemap

admin.autodiscover()

urlpatterns = i18n_patterns(
    url(r'^admin/', include(admin.site.urls)),
    url(r'^sitemap\.xml$', django.contrib.sitemaps.views.sitemap,
        {'sitemaps': {'cmspages': CMSSitemap}}),
    url(r'^', include('cms.urls')),
)

# This is only needed when using runserver.
if settings.DEBUG:
    urlpatterns = [
        url(r'^media/(?P<path>.*)$', django.views.static.serve,
            {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    ] + staticfiles_urlpatterns() + urlpatterns
