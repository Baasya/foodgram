from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'api'

router = DefaultRouter()
router.register(
    r'ingredients', views.IngredientViewSet, basename='ingredients')
router.register(r'recipes', views.RecipeViewSet, basename='recipes')
router.register(r'tags', views.TagViewSet, basename='tags')
router.register(r'users', views.CustomUserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('docs/', TemplateView.as_view(template_name='docs/redoc.html'),
         name='redoc'),
    path('auth/', include('djoser.urls.authtoken')),
]
