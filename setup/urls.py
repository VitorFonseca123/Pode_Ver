
from django.contrib import admin
from django.urls import path

from PodeVer.views import AddMovie

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', AddMovie),
]
