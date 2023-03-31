from django.urls import path

from account import views


app_name = "account"

urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name='create-user'),
    path('token/', views.CreateTokenView.as_view(), name='token'),
    path('<str:username>/', views.UpdateAndRetrieveView.as_view(),
         name='detail')
]
