from django.conf.urls import url
from games import views

# type = list
# url 리스트를 사용하면 URL을 뷰로 보낼 수 있다.
urlpatterns = [
    url(r'^games/$', views.game_list),
    url(r'^games/(?P<pk>[0-9]+)/$', views.game_detail),
]