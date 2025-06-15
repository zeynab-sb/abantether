from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/orders/', include('order.urls')),
    path('api/users/', include('user.urls')),
    path('api/wallet/', include('wallet.urls')),
]
