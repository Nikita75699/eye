from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path, re_path
from django.views.static import serve

urlpatterns = [
    path('', include('home.urls')),
    path('api/', include('api.urls')),
    path('admin/', admin.site.urls),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += [re_path(r'^orthanc_db/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT,}),]
