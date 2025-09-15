from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("barbearia.urls")),  # ✅ tudo do app barbearia
]
