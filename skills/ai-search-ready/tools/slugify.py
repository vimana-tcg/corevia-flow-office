#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""slugify.py — UK/RU/EN транслітерація → ASCII anchor slug.

Imports/usage:
    from slugify import slugify_text
    slug = slugify_text("Які моделі в наявності у ОСКТРЕЙД")
    # → "iaki-modeli-v-naiavnosti-u-osktreid"
"""
from __future__ import annotations
import re

UK_TABLE = str.maketrans({
    'а':'a','б':'b','в':'v','г':'h','ґ':'g','д':'d','е':'e','є':'ie','ж':'zh',
    'з':'z','и':'y','і':'i','ї':'i','й':'i','к':'k','л':'l','м':'m','н':'n',
    'о':'o','п':'p','р':'r','с':'s','т':'t','у':'u','ф':'f','х':'kh','ц':'ts',
    'ч':'ch','ш':'sh','щ':'shch','ь':'','ю':'iu','я':'ia',
    'ы':'y','э':'e','ё':'e','ъ':'',
    'А':'a','Б':'b','В':'v','Г':'h','Ґ':'g','Д':'d','Е':'e','Є':'ie','Ж':'zh',
    'З':'z','И':'y','І':'i','Ї':'i','Й':'i','К':'k','Л':'l','М':'m','Н':'n',
    'О':'o','П':'p','Р':'r','С':'s','Т':'t','У':'u','Ф':'f','Х':'kh','Ц':'ts',
    'Ч':'ch','Ш':'sh','Щ':'shch','Ь':'','Ю':'iu','Я':'ia',
    'Ы':'y','Э':'e','Ё':'e','Ъ':'',
})


def slugify_text(text: str, max_len: int = 60) -> str:
    """Transliterate UK/RU/EN → ASCII slug suitable for HTML id attribute.

    - Strips HTML tags
    - Transliterates Cyrillic via canonical table
    - Replaces non-alphanumeric with hyphens
    - Collapses multiple hyphens
    - Trims to max_len
    - Returns 'section' if empty
    """
    text = re.sub(r'<[^>]+>', '', text or '')
    text = text.translate(UK_TABLE).lower()
    text = re.sub(r'[^a-z0-9]+', '-', text).strip('-')
    return text[:max_len] or 'section'


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        # Demo
        for t in [
            "Які моделі в наявності у ОСКТРЕЙД",
            "Скільки коштує б/у?",
            "Frequently Asked Questions",
            "Цена и условия",
        ]:
            print(f"  {t!r:50} → {slugify_text(t)!r}")
    else:
        print(slugify_text(sys.argv[1]))
