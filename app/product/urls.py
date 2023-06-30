from django.conf.urls.static import static
from django.urls import path, include
from django.conf import settings

from app.product.views import UsersListView, DepartmentsView, UserView, UserImageView, DepartmentsListView, RateView, \
    RatesViewList, LogIn

urlpatterns = [
                  path('auth/', include('rest_framework.urls')),
                  path('user/list/', UsersListView.as_view()),
                  path('user/login/', LogIn.as_view()),
                  path('user/', UserView.as_view()),
                  path('user/image/<int:userId>', UserImageView.as_view()),
                  path('user/<int:userId>', UserView.as_view()),
                  path('department/list/', DepartmentsView.as_view()),
                  path('user/by/department/<str:dep>', DepartmentsListView.as_view()),
                  path('rate/', RateView.as_view()),
                  path('rate/<int:reviewer_id>/<int:assessed_id>', RateView.as_view()),
                  path('rate/<int:userId>', RatesViewList.as_view())
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
