# modal-hj3415

모달창을 띄우는 모듈.


1. 프로젝트의 settings.py 에 추가한다.
```python
INSTALLED_APPS = [
    'modal_hj3415',
]
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

2. makemigration, migrate 실행

3. urls.py
```python
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    ...
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

3. 사용 위치의 html에 작성한다.
```html
{% load modal_tags %}
...
{% show_modal %}
또는
{% show_modals %} - 여러창을 띄우는 기능
```


## 사용법
최신 것만 타입별 1개씩:
{% show_modals only_latest=True %}

우선순위 바꾸기:
{% show_modals priority=("rotate_bg","link_video","single_bg","image_only") %}

자동 오픈 끄기(사용자 트리거로만 열고 싶을 때):
{% show_modals auto_open=False %}
