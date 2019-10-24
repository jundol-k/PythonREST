from rest_framework import serializers
from games.models import GameCategory
from games.models import Game
from games.models import Player
from games.models import PlayerScore
from django.contrib.auth.models import User

# 01
'''
class GameSerializer(serializers.Serializer):
    pk = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=200)
    release_date = serializers.DateTimeField()

    game_category = serializers.CharField(max_length=200)
    played = serializers.BooleanField(required=False)

    def create(self, validated_data):
        return Game.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.release_date = validated_data.get('release_date', instance.release_date)
        instance.game_category = validated_data.get('game_category', instance.game_category)
        instance.played = validated_data.get('played', instance.played)
        instance.save()
        return instance
'''
#03
class UserGameSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Game
        fields = ('url', 'name')

class UserSerializer(serializers.HyperlinkedModelSerializer):
    games = UserGameSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('url', 'pk', 'username', 'games')

#02
class GameCategorySerializer(serializers.HyperlinkedModelSerializer):
    games = serializers.HyperlinkedRelatedField(
        many = True,
        read_only=True,
        view_name='game-detail')

    class Meta:
        model = GameCategory
        fields = ('url', 'pk', 'name', 'games')
#02
#03
class GameSerializer(serializers.HyperlinkedModelSerializer):
    # 소유자 사용자 이름만 표시하려고한다 (읽기 전용)
    owner = serializers.ReadOnlyField(source='owner.username')
    # We want to display the game cagory's name instead of the id
    game_category = serializers.SlugRelatedField(queryset = GameCategory.objects.all(), slug_field='name')

    class Meta:
        model = Game
        depth = 4
        fields = ('url',
                  'owner',
                  'name',
                  'release_date',
                  'game_category',
                  'release_date',
                  'played')

#02
class ScoreSerializer(serializers.HyperlinkedModelSerializer):
    # We want to display all the details for the game
    game = GameSerializer()
    # We don't include the player because it will be nested in the player
    class Meta:
        model = PlayerScore
        fields = ('url', 'pk', 'score', 'score_date', 'game')

#02
class PlayerSerializer(serializers.HyperlinkedModelSerializer):
    scores = ScoreSerializer(many=True, read_only=True)
    gender = serializers.ChoiceField(choices=Player.GENDER_CHOICES)
    gender_description = serializers.CharField(source='get_gender_display', read_only=True)

    class Meta:
        model = Player
        fields = ('url', 'name', 'gender', 'gender_description', 'scores')

#02
class PlayerScoreSerializer(serializers.ModelSerializer):
    player = serializers.SlugRelatedField(queryset=Player.objects.all(), slug_field='name')
    # We want to display the game's name instead of the id
    game = serializers.SlugRelatedField(queryset=Game.objects.all(), slug_field='name')

    class Meta:
        model = PlayerScore
        fields = ('url', 'pk', 'score', 'score_date', 'player', 'game')