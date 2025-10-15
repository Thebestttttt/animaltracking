from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('change_password/', views.Change_password, name='change_password'),
    path('stray/', views.StrayView, name='stray'),
    path('stray_create/', views.CreateStrayAnimalView, name='stray_create'),
    path('stray_edity/<int:pk>/', views.EditStrayView, name='stray_edit'),
    path('stray_comment/<int:pk>/', views.CommentStrayView, name='stray_comment'),
    path('lost/', views.LostView, name='lost'),
    path('lost_create/', views.CreateLostAnimalView, name='lost_create'),
    path('lost_edit/<int:pk>/', views.EditLostView, name='lost_edit'),
    path('lost_comment/<int:pk>/', views.CommentLostView, name='lost_comment'),
    path('delete_stray/<int:pk>/', views.DeleteStrayView, name='delete_stray'),
    path('delete_lost/<int:pk>/', views.DeleteLostView, name='delete_lost'),
    path('delete_comment_stray/<int:pk>/', views.DeleteCommentStrayView, name='delete_comment_stray'),
    path('delete_comment_lost/<int:pk>/', views.DeleteCommentLostView, name='delete_comment_lost'),
    path('manage_tag/', views.ManageTagView, name='manage_tag'),
    path('delete_tag/<int:pk>/', views.DeleteTagView, name='delete_tag'),
]