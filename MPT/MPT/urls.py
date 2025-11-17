"""
URL configuration for MPT project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from analysis.views import index_view
from django.views.static import serve
from pathlib import Path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('analysis.api_urls')),
    path('', index_view),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Serve frontend build assets under /assets/ (development only)
project_root = Path(settings.BASE_DIR).parent
dist_assets = project_root / 'frontend' / 'dist' / 'assets'
urlpatterns += [
    path('assets/<path:path>', serve, {'document_root': str(dist_assets)}),
]
