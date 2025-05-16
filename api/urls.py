from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from example import imdbviews,petviews,bakeryviews


urlpatterns = [
    path('admin/', admin.site.urls),
    path('apiimdb/', imdbviews.checkService),
    path('apipet/', petviews.checkService),
    # path('apibakery/', bakeryviews.checkService),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)