"""yatube URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.contrib.flatpages import views
# noinspection PyUnresolvedReferences
from django.conf.urls import handler404, handler500

# noinspection PyRedeclaration
from django.views.generic import TemplateView

handler404 = "posts.views.page_not_found"
# noinspection PyRedeclaration
handler500 = "posts.views.server_error"

urlpatterns = [
    path('about-us/', views.flatpage, {'url': '/about-us/'}, name='about_us'),
    path('about-author/', views.flatpage, {'url': '/about-author/'}, name='about_author'),
    path('about-spec/', views.flatpage, {'url': '/about-spec/'}, name='about_spec'),
    path('terms/', views.flatpage, {'url': '/terms/'}, name='terms'),
    path("about/", include("django.contrib.flatpages.urls")),

    path("admin/", admin.site.urls),
    path("", include("posts.urls")),
    path("auth/", include("users.urls")),
    path("auth/", include("django.contrib.auth.urls")),
    path('api/v1/', include('api.urls')),
    path('docs/redoc/', TemplateView.as_view(template_name='redoc.html'), name='redoc'),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += (path("__debug__/", include(debug_toolbar.urls)),)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
