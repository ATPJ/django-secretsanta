from django.urls import path

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)

from account import views


app_name = "account"

urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name='create-user'),
    path('token/', TokenObtainPairView.as_view(), name='access-token'),
    path('token/refresh', TokenRefreshView.as_view(), name='refresh-token'),
    path('<str:username>/', views.UpdateAndRetrieveView.as_view(),
         name='detail')
]
