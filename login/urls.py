from django.urls import path

from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    # url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
    #     views.activate, name='activate'),
    path('activate/<str:uidb64>/<str:token>', views.activate, name='activate'),
]
