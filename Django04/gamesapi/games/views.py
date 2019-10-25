#from django.http import HttpResponse
#02
from games.models import GameCategory
from games.models import Game
from games.models import Player
from games.models import PlayerScore
from games.serializers import GameCategorySerializer
from games.serializers import GameSerializer
from games.serializers import PlayerSerializer
from games.serializers import PlayerScoreSerializer
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.reverse import reverse
from django.contrib.auth.models import User
from games.serializers import UserSerializer
from rest_framework import permissions
from games.permissions import IsOwnerOrReadOnly
from rest_framework.throttling import ScopedRateThrottle
from rest_framework import filters
from django_filters.rest_framework import FilterSet
from django_filters import NumberFilter, DateTimeFilter, AllValuesFilter

# Create your views here.
# rest_framework.response.Response 로 대체 한다.
'''
class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)
'''

class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    name = 'user-list'

class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    name = 'user-detail'

class GameCategoryList(generics.ListCreateAPIView):
    queryset = GameCategory.objects.all()
    serializer_class = GameCategorySerializer
    name = 'gamecategory-list'
    throttle_scope = 'game-categories'
    throttle_classes = (ScopedRateThrottle,)
    #filter_fields = ('name',)
    filter_backends = [filters.SearchFilter]
    search_fields = ('^name',)
    ordering_fields = ('name',)

class GameCategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = GameCategory.objects.all()
    serializer_class = GameCategorySerializer
    name = 'gamecategory-detail'
    throttle_scope = 'game-categories'
    throttle_classes = (ScopedRateThrottle,)

class GameList(generics.ListCreateAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    name = 'game-list'
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)
    #filter_fields = ('name', 'game_category', 'release_date', 'played', 'owner',)
    filter_backends = [filters.SearchFilter]
    search_fields = ('^name',)
    ordering_fields = ('name', 'release_date',)
    def perform_create(self, serializer):
        # 요청으로 받은 사용자로 소유자를 설정하기 위해 create 메소드에게 추가적인 owner 필드를 전달한다.
        serializer.save(owner=self.request.user)

class GameDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    name = 'game-detail'
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)

class PlayerList(generics.ListCreateAPIView):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    name = 'player-list'
    #filter_fields = ('name', 'gender',)
    filter_backends = [filters.SearchFilter]
    search_fields = ('^name',)
    ordering_fields = ('name',)

class PlayerDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    name = 'player-detail'

class PlayerScoreFilter(FilterSet):
    min_score = NumberFilter(field_name='score', lookup_expr='gte')
    max_score = NumberFilter(field_name='score', lookup_expr='lte')
    from_score_date = DateTimeFilter(field_name='score_date', lookup_expr='gte')
    to_score_date = DateTimeFilter(field_name='score_date', lookup_expr='lte')
    player_name = AllValuesFilter(field_name='player__name')
    game_name = AllValuesFilter(field_name='game__name')

    class Meta:
        model = PlayerScore
        fields = ('score', 'from_score_date', 'to_score_date', 'min_score', 'max_score','player_name','game_name')

class PlayerScoreList(generics.ListCreateAPIView):
    queryset = PlayerScore.objects.all()
    serializer_class = PlayerScoreSerializer
    name = 'playerscore-list'
    filterset_class = PlayerScoreFilter
    ordering_fields = ('score', 'score_date',)

class PlayerScoreDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = PlayerScore.objects.all()
    serializer_class = PlayerScoreSerializer
    name = 'playerscore-detail'


# Api의 루트에 대한 엔드포인트 생성
class ApiRoot(generics.GenericAPIView):
    name = 'api-root'
    def get(self, request, *args, **kwargs):
        return Response({
            'players': reverse(PlayerList.name, request=request),
            'game-categories': reverse(GameCategoryList.name, request=request),
            'games': reverse(GameList.name, request=request),
            'scores': reverse(PlayerScoreList.name, request=request),
            'users': reverse(UserList.name, request=request),
        })

# 함수기반
'''
# 데커레이터
@csrf_exempt
@api_view(['GET', 'POST'])
def game_list(request):
    # 모든 게임을 나열
    if request.method == 'GET':
        games = Game.objects.all()
        games_serializer = GameSerializer(games, many=True)
        return Response(games_serializer.data)
        #return JSONResponse(games_serializer.data)
    # 새로운 게임을 생성
    elif request.method == 'POST':
        #game_data = JSONParser().parse(request)
        game_serializer = GameSerializer(data=request.data)
        if game_serializer.is_valid():
            game_serializer.save()
            return Response(game_serializer.data, status=status.HTTP_201_CREATED)
            #return JSONResponse(game_serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(game_serializer.error, status=status.HTTP_400_BAD_REQUEST)
    #return JSONResponse(game_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(['GET', 'PUT', 'POST'])
def game_detail(request, pk): # 기존 게임을 검색, 업데이트, 삭제한다. pk는 게임의 기본키 또는 식별자
    try:
        game = Game.objects.get(pk=pk)
    except Game.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
        #return HttpResponse(status=status.HTTP_404_NOT_FOUND)
    # 게임 데이터 반환
    if request.method == 'GET':
        game_serializer = GameSerializer(game)
        return Response(game_serializer.data)
        #return JSONResponse(game_serializer.data)
    # request 요청에 포함된 json 데이터로 새 게임을 만들어 기존 게임을 대체한다.
    elif request.method == 'PUT':
        #game_data = JSONParser().parse(request)
        game_serializer = GameSerializer(game, data=request.data)
        if game_serializer.is_valid():
            game_serializer.save()
            return Response(game_serializer.data)
            #return JSONResponse(game_serializer.data)
        return Response(game_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        #return JSONResponse(game_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        game.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
        #return HttpResponse(status=status.HTTP_204_NO_CONTENT)
'''