from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from example import imdbviews,petviews


urlpatterns = [
    path('admin/', admin.site.urls),
    path('apiimdb/', imdbviews.checkService),
    path('apipet/', petviews.checkService),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)