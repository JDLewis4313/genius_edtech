from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('chemistry/', include('chemistry.urls')),
    path('quiz/', include('quiz.urls', namespace='quiz')),
    path('code-editor/', include('code_editor.urls')),
    path('tutorials/', include('apps.tutorials.urls')),
    path('users/', include('users.urls', namespace='users')),
    path('blog/', include('apps.blog.urls', namespace='blog')),
    path('community/', include('apps.community.urls', namespace='community')),
    path('', include('apps.analytics.urls')),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
