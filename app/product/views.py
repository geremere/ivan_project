import json
import random

from django.contrib.auth import authenticate
from django.contrib.auth.models import User as DjangoUser
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app.product.models import User, Rate
from app.product.serializers import UserSerializer, RateSerializer


class LogIn(APIView):

    def post(self, request):
        username = request.data["username"]
        password = request.data["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            token = Token.objects.get_or_create(user=user)
            return Response(str(token[0].key), status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


class UsersListView(APIView):
    permission_classes = ((IsAuthenticated, IsAdminUser))

    def get(self, request):
        self.check_permissions(request)
        return Response([i.to_json() for i in User.objects.all()])


class DepartmentsListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = ((IsAuthenticated,))

    def get_queryset(self):
        return User.objects.filter(department=self.kwargs.get("dep"))


class RatesViewList(generics.ListAPIView):
    serializer_class = RateSerializer
    permission_classes = ((IsAuthenticated,))

    def get_queryset(self):
        user = User.objects.get(id=self.kwargs['userId'])
        rates = Rate.objects.filter(assessed_user_id=user.id)
        return rates


class DepartmentsView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return Response([i.department for i in User.objects.all()])

    # set filter
    def post(self, request):
        user = User.objects.get(login=request.user.username)
        user.departments_filter = request.data
        user.save()
        return Response(status=status.HTTP_200_OK)


class UserImageView(APIView):
    permission_classes = ((IsAdminUser, IsAuthenticated))

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


class AdminUserView(APIView):
    permission_classes = ((IsAdminUser, IsAuthenticated))

    @parser_classes((MultiPartParser,))
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
        djUser = DjangoUser.objects.get(username=user.login)
        user.delete()
        djUser.delete()
        return Response("User was deleted", status=status.HTTP_200_OK)

    def patch(self, request, userId):
        self.check_permissions(request)
        user = User.objects.get(id=userId)
        ser = UserSerializer(user, data=request.data, partial=True)
        if ser.is_valid():
            ser.save()
            return Response(ser.data, status=status.HTTP_200_OK)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)


class UserView(APIView):
    permission_classes = ((IsAuthenticated,))

    def get(self, request):
        return Response(User.objects.get(login=request.user.username).to_json(), status=status.HTTP_200_OK)


class UsersForRate(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        black_list = list(filter(lambda it: it != '',
                                 list(User.objects.get(login=request.user.username).black_list.split(","))))
        black_list = set([int(x) for x in black_list])
        dep_filter = set(
            filter(lambda it: it != '', User.objects.get(login=request.user.username).departments_filter.split(",")))
        users = list(User.objects.exclude(id__in=black_list))
        users = list(filter(lambda user: len(dep_filter) == 0 or user.department in dep_filter, users))
        if len(users) < 5:
            return Response([user.to_short_json() for user in users], status=status.HTTP_200_OK)
        else:
            return Response(random.sample(users, 5), status=status.HTTP_200_OK)


class RateView(APIView):
    permission_classes = (IsAuthenticated,)

    # make rate
    def post(self, request):
        ser = RateSerializer(data=request.data)
        if ser.is_valid():
            user = User.objects.get(id=request.data['reviewer_user'])
            if user.login == request.user.username:
                user.black_list = user.black_list + "," + str(request.data['assessed_user'])
                user.save()
                ser.save()
                return Response(ser.data, status=status.HTTP_200_OK)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

    # skip rate
    def get(self, request, assessed_user_id):
        user = User.objects.get(login=request.user.username)
        user.black_list = user.black_list + "," + str(assessed_user_id)
        user.save()
        return Response(status=status.HTTP_200_OK)
