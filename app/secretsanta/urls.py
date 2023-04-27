from django.urls import path, include

from rest_framework.routers import DefaultRouter

from secretsanta import views

router = DefaultRouter()
router.register("event", views.EventViewSet)


urlpatterns = [
    path("", include(router.urls))
]

app_name = "santa"
