# blog-hj3415

demiansoft 템플릿의 blog와 portfolio을 구성한다.

# settings.py
```python
INSTALLED_APPS += ['blog_hj3415', 'markdownx']
AUTH_USER_MODEL = "blog_hj3415.User"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
```

# urls.py
```python
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns += [path('markdownx/', include('markdownx.urls'))]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

# 템플릿에서
- blog-detail.html
```html
<div>{{ post.body_html|add_img_class:"img-fluid"|safe }}</div>
```

- index.html
```html
<div>{{ item.body_html | striptags | truncatechars_html:80 }}</div>
```

**사용하고자하는 앱에서 url.py 와 views.py를 testapp 을 참고하여 구성한다.**