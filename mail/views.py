from django.shortcuts import render
from .serializers import ThreadedView, DomainSettingsSerializer, DomainSerializer, MessageSerializer, AccountSerializer
from rest_framework import permissions, viewsets
from rest_framework import status
from rest_framework.response import Response
from .models import Account
from rest_framework import generics
from .permissions import IsAdminUser
from rest_framework.decorators import api_view
from rest_framework.exceptions import APIException


class AccountViewSet(viewsets.ModelViewSet):
    lookup_field = 'username'
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return (permissions.AllowAny(),)

        if self.request.method == 'POST':
            return (permissions.AllowAny(),)

        return (permissions.IsAuthenticated(), IsAccountOwner(),)

    def create(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            Account.objects.create_user(**serializer.validated_data)

            return Response(serializer.validated_data, status=status.HTTP_201_CREATED)

        return Response({
            'status': 'Bad request',
            'message': 'Account could not be created with received data.'
        }, status=status.HTTP_400_BAD_REQUEST)


class GetUserList(generics.ListAPIView):
    permission_classes = (IsAdminUser,)
    queryset = Account.objects.all()
    serializer_class = AccountSerializer


@api_view(['POST'])
def create_admin(request):
    if Account.objects.all().count() == 0:
        if request.data['password'] and request.data['confirm_password'] and request.data['password'] == request.data['confirm_password']:
            admin = Account.objects.create(username=request.data['username'], password=request.data['password'])
            admin.is_admin = True
            admin.save()
            return Response({"message": 'Admin Created'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': 'something wrong'}, status=status.HTTP_206_PARTIAL_CONTENT)
    else:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)