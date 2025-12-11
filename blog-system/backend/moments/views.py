from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Moment, MomentLike
from .serializers import MomentSerializer, MomentCreateSerializer


class MomentViewSet(viewsets.ModelViewSet):
    """瞬间视图集"""
    queryset = Moment.objects.filter(visibility='public').select_related('author')
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return MomentCreateSerializer
        return MomentSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        # 登录用户可以查看自己的私密瞬间
        if self.request.user.is_authenticated:
            queryset = Moment.objects.filter(
                Q(visibility='public') | Q(author=self.request.user)
            ).select_related('author')
        return queryset

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'like']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """点赞瞬间"""
        moment = self.get_object()
        like, created = MomentLike.objects.get_or_create(
            moment=moment,
            user=request.user
        )
        if not created:
            like.delete()
            moment.likes = max(0, moment.likes - 1)
            liked = False
        else:
            moment.likes += 1
            liked = True
        moment.save(update_fields=['likes'])
        return Response({'liked': liked, 'likes': moment.likes})
