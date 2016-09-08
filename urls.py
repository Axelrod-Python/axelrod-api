# -*- coding: utf-8 -*-
from django.conf.urls import url, include
from aldryn_django.utils import i18n_patterns
import aldryn_addons.urls
from rest_framework.routers import DefaultRouter
from core.views import StrategyViewSet


urlpatterns = [
    url(r'^api-auth/', include('rest_framework.urls')),
]

router = DefaultRouter()

routes = {
    'strategies': StrategyViewSet
}

for route, viewset in routes.items():
    router.register(route, viewset, base_name=route)

urlpatterns += router.urls
urlpatterns += aldryn_addons.urls.patterns()
urlpatterns += i18n_patterns(
    *aldryn_addons.urls.i18n_patterns()  # MUST be the last entry!
)
