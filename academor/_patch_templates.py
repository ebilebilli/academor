import re
from pathlib import Path

templates_dir = Path(__file__).resolve().parent / "templates"

for f in templates_dir.glob("*.html"):
    text = f.read_text(encoding="utf-8")
    if "{% load static %}" not in text:
        text = text.replace("<!DOCTYPE html>\n", "<!DOCTYPE html>\n{% load static %}\n", 1)

    def static_href(m):
        path = m.group(1)
        return f'href="{{% static \'assets/{path}\' %}}"'

    def static_src(m):
        path = m.group(1)
        return f'src="{{% static \'assets/{path}\' %}}"'

    text = re.sub(
        r'href="(img/[^"]+|css/[^"]+|lib/[^"]+)"',
        static_href,
        text,
    )
    text = re.sub(
        r'src="(img/[^"]+|js/[^"]+|lib/[^"]+)"',
        static_src,
        text,
    )

    repl = {
        'href="index.html"': 'href="{% url \'projects:home-page\' %}"',
        'href="about.html"': 'href="{% url \'projects:about-page\' %}"',
        'href="courses.html"': 'href="{% url \'projects:courses-page\' %}"',
        'href="team.html"': 'href="{% url \'projects:team-page\' %}"',
        'href="testimonial.html"': 'href="{% url \'projects:reviews-page\' %}"',
        'href="404.html"': 'href="{% url \'projects:home-page\' %}"',
        'href="contact.html"': 'href="{% url \'projects:contact-page\' %}"',
    }
    for old, new in repl.items():
        text = text.replace(old, new)

    f.write_text(text, encoding="utf-8")
    print("Patched", f.name)
