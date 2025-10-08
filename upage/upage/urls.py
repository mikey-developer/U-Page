from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import *
urlpatterns = [
    path('', home, name = 'home'),
    path('signup/', signup, name = 'signup'),
    path('publication/', publication, name = 'post'),
    path('publication/image/', publication_image, name = 'img-post'),
    path('replies/<int:id>/', posts, name = 'replies'),
    path('edit/<int:id>/', publication_edit, name = 'publication_edit'),
    path('delete/<int:id>/', publication_delete, name = 'publication_delete'),
    path('details/<int:id>/', post_details, name = 'details'),
    path('me/<str:id>/', user_profile, name = 'user'),
    path('center/', center, name = "center"),
    path('login/', login, name='login'),
    path('profile/pic/', upload_view, name = 'profile'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)