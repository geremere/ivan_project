import json

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User as DjangoUser
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import parser_classes, permission_classes
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

    @permission_classes((IsAuthenticated, IsAdminUser))
    def get(self, request):
        self.check_permissions(request)
        return Response([i.to_json() for i in User.objects.all()])


class DepartmentsListView(generics.ListAPIView):
    serializer_class = UserSerializer

    @permission_classes((IsAuthenticated,))
    def get_queryset(self):
        return User.objects.filter(department=self.kwargs.get("dep"))


class RatesViewList(generics.ListAPIView):
    serializer_class = RateSerializer

    @permission_classes((IsAuthenticated,))
    def get_queryset(self):
        user = User.objects.get(id=self.kwargs['userId'])
        rates = Rate.objects.filter(assessed_user_id=user.id)
        return rates


class DepartmentsView(APIView):

    @permission_classes((IsAuthenticated,))
    def get(self, request):
        return Response([i.department for i in User.objects.all()])


class UserImageView(APIView):

    @permission_classes((IsAdminUser, IsAuthenticated))
    def post(self, request, userId):
        self.check_permissions(request)
        user = User.objects.get(id=userId)
        _data = {"image": request.FILES['image']}
        ser = UserSerializer(user, data=_data, partial=True)
        if ser.is_valid():
            ser.save()
            return Response(ser.data, status=status.HTTP_200_OK)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

    @permission_classes((IsAuthenticated,))
    def get(self, request, userId):
        self.check_permissions(request)
        user = User.objects.get(id=userId)
        return Response("http://localhost:8000/api/v1" + user.image.url if user.image is not None else None,
                        status=status.HTTP_200_OK)


class UserView(APIView):

    @parser_classes((MultiPartParser,))
    @permission_classes((IsAdminUser, IsAuthenticated))
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

    @permission_classes((IsAdminUser, IsAuthenticated))
    def delete(self, request, userId):
        self.check_permissions(request)
        user = User.objects.get(id=userId)
        djUser = DjangoUser.objects.get(username=user.login)
        user.delete()
        djUser.delete()
        return Response("User was deleted", status=status.HTTP_200_OK)

    @permission_classes((IsAuthenticated,))
    def get(self, request):
        return Response(User.objects.get(id=request.user.id).to_json(), status=status.HTTP_200_OK)

    @permission_classes((IsAdminUser, IsAuthenticated))
    def patch(self, request, userId):
        self.check_permissions(request)
        user = User.objects.get(id=userId)
        ser = UserSerializer(user, data=request.data, partial=True)
        if ser.is_valid():
            ser.save()
            return Response(ser.data, status=status.HTTP_200_OK)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)


class RateView(APIView):

    @permission_classes((IsAuthenticated,))
    def post(self, request):
        ser = RateSerializer(data=request.data)
        if ser.is_valid():
            ser.save()
            return Response(ser.data, status=status.HTTP_200_OK)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

    # @permission_classes((IsAuthenticated,))
    # def get(self, request, reviewer_id, assessed_id):

