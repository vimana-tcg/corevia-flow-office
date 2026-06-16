#!/usr/bin/env python3
"""team_list.py — показывает «кто в офисе»: агенты по отделам + краткое описание.
Парсит frontmatter (name/description) каждого agents/*.md. Без зависимостей.
"""
import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AGENTS = os.path.join(ROOT, "agents")

DEPTS = [
    ("🎯 Продукт", ("pm-",)),
    ("📣 Маркетинг/SMM", ("brand-director", "smm-", "paid-ads", "marketing-email", "publishing-", "engagement-")),
    ("✍️ Контент", ("content-",)),
    ("🎨 Дизайн", ("web-designer", "motion-designer", "carousel-", "video-creator", "ad-creative")),
    ("🔎 SEO", ("seo-",)),
    ("🔑 Ключевые слова", ("keyword-",)),
    ("💰 Финансы", ("fin-",)),
    ("🏢 Офис/Продажи", ("office-", "sales-")),
    ("🛡️ Безопасность/QA", ("oss-vetter", "qa-")),
    ("🛠️ Инфра", ("infra-",)),
    ("🤝 Поддержка/Право", ("customer-support", "legal-")),
    ("🧠 Управление", ("agent-mentor", "memory-keeper", "founder-coach", "tech-director", "prompt-curator")),
]


def short_desc(text):
    m = re.search(r'(?ms)^description:\s*(.*?)(?:\n[a-z_]+:\s|\n---)', text)
    if not m:
        return ""
    d = " ".join(m.group(1).replace(">", " ").split())
    return (d[:90] + "…") if len(d) > 90 else d


def main():
    files = {}
    for f in sorted(os.listdir(AGENTS)):
        if not f.endswith(".md"):
            continue
        name = f[:-3]
        files[name] = short_desc(open(os.path.join(AGENTS, f), encoding="utf-8").read())
    used = set()
    print("🏢 Кто в офисе (агенты по отделам):\n")
    for dep, prefixes in DEPTS:
        members = [n for n in files if any(n.startswith(p) or n == p for p in prefixes)]
        members = [n for n in members if n not in used]
        if not members:
            continue
        print(f"## {dep}")
        for n in sorted(members):
            used.add(n)
            print(f"  • {n} — {files[n]}")
        print()
    rest = [n for n in files if n not in used]
    if rest:
        print("## Прочее")
        for n in sorted(rest):
            print(f"  • {n} — {files[n]}")
        print()
    print(f"Всего сотрудников: {len(files)}.  Спроси «как работает <имя>» — объясню простыми словами.")


if __name__ == "__main__":
    main()
