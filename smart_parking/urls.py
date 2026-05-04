from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
import os

def service_worker(request):
    sw_path = os.path.join(settings.BASE_DIR, 'static', 'sw.js')
    with open(sw_path, 'r') as f:
        content = f.read()
    return HttpResponse(content, content_type='application/javascript')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('sw.js', service_worker, name='sw'),    # ← ADD THIS
    path('', include('parking.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
