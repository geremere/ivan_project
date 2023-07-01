from django.conf.urls.static import static
from django.urls import path, include
from django.conf import settings

from app.product.views import UsersListView, DepartmentsView, UserView, UserImageView, DepartmentsListView, RateView, \
    RatesViewList, LogIn, UsersForRate, AdminUserView

urlpatterns = [
                  path('auth/', include('rest_framework.urls')),
                  path('admin/user/list/', UsersListView.as_view()),
                  path('user/login/', LogIn.as_view()),
                  path('admin/user/', AdminUserView.as_view()),
                  path('admin/user/<int:userId>', AdminUserView.as_view()),
                  path('user/', UserView.as_view()),
                  path('admin/user/image/<int:userId>', UserImageView.as_view()),
                  path('user/<int:userId>', UserView.as_view()),
                  path('departments/', DepartmentsView.as_view()),
                  path('user/by/department/<str:dep>', DepartmentsListView.as_view()),
                  path('rate/', RateView.as_view()),
                  path('rate/<int:assessed_user_id>', RateView.as_view()),
                  path('rate/<int:userId>', RatesViewList.as_view()),
                  path('rate/users/', UsersForRate.as_view()),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
