from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views import defaults as default_views
from django.views.generic import TemplateView

from stig_a_view.base import views as base_views

urlpatterns = [
    path("", TemplateView.as_view(template_name="pages/home.html"), name="home"),
    path(
        "about/", TemplateView.as_view(template_name="pages/about.html"), name="about"
    ),
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    # User management
    path("users/", include("stig_a_view.users.urls", namespace="users")),
    path("accounts/", include("allauth.urls")),
    path("stigs/", view=base_views.StigIndex.as_view(), name="stigs"),
    path("stigs/<int:id>", view=base_views.StigDetail.as_view(), name="stig_detail"),
    path("stigs/<int:stig_id>/controls/<int:id>", view=base_views.ControlView.as_view(), name="control_detail"),
    path("stigs/<int:stig_id>/controls/<str:id>", view=base_views.ControlView.as_view(), name="control_detail"),
    path("products/<int:id>", view=base_views.ProductView.as_view(), name="product_detail"),
    path("products/<str:id>", view=base_views.ProductView.as_view(), name="product_detail")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
