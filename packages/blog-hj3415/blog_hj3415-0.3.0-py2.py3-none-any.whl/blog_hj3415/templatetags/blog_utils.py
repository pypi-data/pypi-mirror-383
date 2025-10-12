# templatetags/blog_utils.py
from django import template
from django.utils.safestring import mark_safe
from bs4 import BeautifulSoup

register = template.Library()

@register.filter(name='add_img_class')
def add_img_class(html: str, classes: str = 'img-fluid'):
    """
    사용: {{ item.body_html|add_img_class:"img-fluid"|safe }}
    여러 클래스: {{ item.body_html|add_img_class:"img-fluid rounded"|safe }}
    """
    if not html:
        return ''
    if BeautifulSoup is None:
        # bs4가 없을 땐 원본 그대로(또는 예외 발생시키도록 바꿔도 됨)
        return html

    soup = BeautifulSoup(html, 'lxml')  # 'html.parser'도 가능하나 lxml 권장
    class_list = [c for c in (classes or '').split() if c]

    for img in soup.find_all('img'):
        current = set(img.get('class', []))
        current.update(class_list)
        if current:
            img['class'] = sorted(current)

    return mark_safe(str(soup))

@register.filter
def remove_tags(html: str, tags_csv: str = "img,figure,picture,source,br") -> str:
    """
    tags_csv에 적은 태그만 제거/치환.
    - br은 공백으로 치환(붙어버리는 것 방지)
    - 그 외 태그는 통째로 제거
    """
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    targets = [t.strip().lower() for t in tags_csv.split(",") if t.strip()]
    for name in targets:
        for tag in soup.find_all(name):
            if name == "br":
                tag.replace_with(" ")  # 또는 "\n"로 개행 유지
            else:
                tag.decompose()
    return str(soup)

