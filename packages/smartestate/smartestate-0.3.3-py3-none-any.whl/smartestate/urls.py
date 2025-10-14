"""smartestate URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
# TODO: Temporary fix only!
from django.urls import re_path

from . import views as home_views
from listings import views as listings_views

urlpatterns = [
    path('', home_views.home, name='home'),
    path('listings/', include('listings.urls')),
    path('pages/', include('pages.urls')),
    path('rental-listings/', listings_views.list_rental, name='rental_listings'),
    path('for-sale-listings/', listings_views.list_for_sale,
        name='for_sale_listings'),
    path('broker/', include('broker.urls')),
    path('admin/', admin.site.urls),
    path('cookies/', include('cookie_consent.urls')),
    path('rest/', include('rest.urls')),
]

# TODO: Temporary fix only!
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    from django.views.static import serve
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
    ]
