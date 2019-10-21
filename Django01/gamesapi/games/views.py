#from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from games.models import Game
from games.serializers import GameSerializer

# Create your views here.
# rest_framework.response.Response 로 대체 한다.
'''
class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)
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