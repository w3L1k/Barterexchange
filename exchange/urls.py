from django.urls import path

from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('login/demo/', views.demo_login_view, name='demo_login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.catalog, name='catalog'),
    path('profile/', views.profile_detail, name='my_profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('favorites/', views.favorites, name='favorites'),
    path('notifications/', views.notifications, name='notifications'),
    path('profiles/<int:pk>/', views.profile_detail, name='profile_detail'),
    path('profiles/<int:pk>/complaint/', views.profile_complaint, name='profile_complaint'),
    path('listings/new/', views.listing_create, name='listing_create'),
    path('listings/<int:pk>/', views.listing_detail, name='listing_detail'),
    path('listings/<int:pk>/complaint/', views.listing_complaint, name='listing_complaint'),
    path('listings/<int:pk>/edit/', views.listing_edit, name='listing_edit'),
    path('listings/<int:pk>/archive/', views.listing_archive, name='listing_archive'),
    path('listings/<int:pk>/delete/', views.listing_delete, name='listing_delete'),
    path('listings/<int:pk>/favorite/', views.favorite_toggle, name='favorite_toggle'),
    path('listings/<int:pk>/matches/', views.listing_matches, name='listing_matches'),
    path('listings/<int:pk>/exchange/', views.exchange_create, name='exchange_create'),
    path('exchanges/', views.exchange_dashboard, name='exchange_dashboard'),
    path('exchanges/<int:pk>/accept/', views.exchange_accept, name='exchange_accept'),
    path('exchanges/<int:pk>/review/', views.exchange_review, name='exchange_review'),
    path('exchanges/<int:pk>/<str:action>/', views.exchange_action, name='exchange_action'),
]
