from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    path("", include("accounts.urls", namespace="accounts")),
    path("", include("core.urls", namespace="core")),
    path('game/', include('game.urls', namespace="game")),

    path("", include(("core.urls", "core"), namespace="core")),
    path("", include(("accounts.urls", "accounts"), namespace="accounts")),
    path("game/", include(("game.urls", "game"), namespace="game")),
]