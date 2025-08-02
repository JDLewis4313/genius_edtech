from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # Core
    path('', include('apps.core.urls')),

    # API interface
    path('api/', include('apps.api.urls')),

    # Education
    path('chemistry/', include('apps.education.chemistry.urls')),
    path('learning/', include('apps.education.learning_modules.urls')),

    # Content
    path('blog/', include('apps.content.blog.urls')),
    path('quiz/', include('apps.content.quiz.urls')),
    path('tutorials/', include('apps.content.tutorials.urls')),
    path('code-editor/', include('apps.content.code_editor.urls')),

    # Social
    path('community/', include('apps.social.community.urls')),
    path('interactions/', include('apps.social.interactions.urls')),

    # Users & AI
    path('users/', include('apps.users.urls')),
    path('ai/', include('apps.mentari.urls')),

    # Analytics (optional routing)
    path('analytics/', include('apps.analytics.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
