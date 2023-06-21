import json

from rest_framework import generics, status
from rest_framework.decorators import parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from app.product.models import User, Rate
from app.product.serializers import UserSerializer, RateSerializer
from jobs.jobs import update
from django.contrib.auth.models import User as DjangoUser


class UsersListView(APIView):
    permission_classes = (IsAdminUser,)

    def get(self, request):
        self.check_permissions(request)
        return Response([i.to_json() for i in User.objects.all()])


class DepartmentsListView(generics.ListAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.filter(department=self.kwargs.get("dep"))


class RatesViewList(generics.ListAPIView):
    serializer_class = RateSerializer

    def get_queryset(self):
        user = User.objects.get(id=self.kwargs['userId'])
        rates = Rate.objects.filter(assessed_user_id=user.id)
        return rates


class DepartmentsView(APIView):

    def get(self, request):
        return Response([i.department for i in User.objects.all()])


class UserImageView(APIView):
    permission_classes = (IsAdminUser,)

    def post(self, request, userId):
        self.check_permissions(request)
        user = User.objects.get(id=userId)
        _data = {"image": request.FILES['image']}
        ser = UserSerializer(user, data=_data, partial=True)
        if ser.is_valid():
            ser.save()
            return Response(ser.data, status=status.HTTP_200_OK)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, userId):
        self.check_permissions(request)
        user = User.objects.get(id=userId)
        return Response("http://localhost:8000/api/v1" + user.image.url if user.image is not None else None,
                        status=status.HTTP_200_OK)


@parser_classes((MultiPartParser,))
class UserView(APIView):
    permission_classes = (IsAdminUser,)

    def post(self, request):
        self.check_permissions(request)
        _data = json.loads(request.data['data'])
        _data["image"] = request.FILES['image']
        ser = UserSerializer(data=_data, context={"request": request})
        if ser.is_valid():
            ser.save()
            DjangoUser.objects.create_user(username=_data['login'], password=_data['password'])
            return Response(ser.data, status=status.HTTP_201_CREATED)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, userId):
        self.check_permissions(request)
        user = User.objects.get(id=userId)
        user.delete()
        return Response("User was deleted", status=status.HTTP_200_OK)

    def get(self, request, userId):
        return Response(User.objects.get(id=userId).to_json(), status=status.HTTP_200_OK)

    def patch(self, request, userId):
        self.check_permissions(request)
        user = User.objects.get(id=userId)
        ser = UserSerializer(user, data=request.data, partial=True)
        if ser.is_valid():
            ser.save()
            return Response(request.data, status=status.HTTP_200_OK)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)


class RateView(APIView):

    def post(self, request):
        ser = RateSerializer(data=request.data)
        if ser.is_valid():
            ser.save()
            return Response(ser.data, status=status.HTTP_200_OK)
            update()
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        rate = Rate.objects.get(assessed_user_id=request.data['assessed_user'],
                                reviewer_user_id=request.data['reviewer_user'])

        ser = RateSerializer(rate, data=request.data, partial=True)
        if ser.is_valid():
            ser.save()
            update()
            return Response(ser.data, status=status.HTTP_200_OK)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
