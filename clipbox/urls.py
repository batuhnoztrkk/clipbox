from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

def home_redirect(request):
    if request.user.is_authenticated:
        return redirect('panels:list')
    else:
        return redirect('accounts:login')  # login sayfasına yönlendir

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_redirect, name='home'),  # ana sayfa için yönlendirme view'u
    path('accounts/', include('accounts.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('videos/', include('videos.urls')),
    path('panel/', include('panels.urls')),  # panel app
]

from django.conf import settings
from django.conf.urls.static import static
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)