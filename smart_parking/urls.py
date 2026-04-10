from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles import finders
from django.http import FileResponse, Http404
from django.urls import include, path


def service_worker(request):
    sw_path = finders.find("sw.js")
    if not sw_path:
        raise Http404("Service worker not found.")

    response = FileResponse(open(sw_path, "rb"), content_type="application/javascript")
    response["Service-Worker-Allowed"] = "/"
    return response


urlpatterns = [
    path("admin/", admin.site.urls),
    path("sw.js", service_worker, name="sw"),
    path("", include("parking.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
