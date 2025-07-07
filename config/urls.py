from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('chemistry/', include('apps.chemistry.urls')), 
    path('quiz/', include('apps.quiz.urls', namespace='quiz')), 
    path('code-editor/', include('apps.code_editor.urls')),
    path('tutorials/', include('apps.tutorials.urls')),
    path('users/', include('apps.users.urls', namespace='users')),
    path('blog/', include('apps.blog.urls', namespace='blog')),
    path('community/', include('apps.community.urls', namespace='community')),
    path("ai/", include("apps.mentari.urls")),
    path('', include('apps.analytics.urls')),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
