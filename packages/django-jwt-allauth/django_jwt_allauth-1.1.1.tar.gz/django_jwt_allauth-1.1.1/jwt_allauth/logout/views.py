from django.utils.translation import gettext_lazy as _
from django.conf import settings
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

from jwt_allauth.logout.serializers import RemoveRefreshTokenSerializer
from jwt_allauth.tokens.models import RefreshTokenWhitelistModel
from jwt_allauth.constants import REFRESH_TOKEN_COOKIE


class LogoutView(APIView):
    """
    Calls Django logout method and delete the Token object
    assigned to the current User object.

    Accepts/Returns nothing.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        return self.http_method_not_allowed(request, *args, **kwargs)

    def post(self, request):
        return self.logout(request)

    @staticmethod
    def logout(request):
        data = request.data.copy()
        
        if getattr(settings, 'JWT_ALLAUTH_REFRESH_TOKEN_AS_COOKIE', False):
            refresh_token = request.COOKIES.get(REFRESH_TOKEN_COOKIE)
            if refresh_token:
                data['refresh'] = refresh_token
            else:
                return Response(
                    {"detail": _("Refresh token cookie not found.")},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        try:
            RemoveRefreshTokenSerializer(
                data=data,
                context={'user': request.user.id}
            ).is_valid(raise_exception=True)
            return Response(
                {"detail": _("Successfully logged out.")},
                status=status.HTTP_200_OK
            )
        except (TokenError, InvalidToken):
            return Response(
                {"detail": _("Invalid token.")},
                status=status.HTTP_400_BAD_REQUEST
            )


class LogoutAllView(APIView):
    """
    Logout from all devices.

    Accepts/Returns nothing.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        return self.http_method_not_allowed(request, *args, **kwargs)

    def post(self, request):
        return self.logout(request)

    @staticmethod
    def logout(request):
        RefreshTokenWhitelistModel.objects.filter(user=request.user.id).delete()
        return Response(
            {"detail": _("Successfully logged out from all devices.")},
            status=status.HTTP_200_OK
        )
