#!/usr/bin/env python3
"""Fill empty msgstr for entries referenced from portal templates/static."""
from pathlib import Path

try:
    import polib
except ImportError:
    polib = None

ROOT = Path(__file__).resolve().parents[1]
LOCALE = ROOT / "locale"

AZ = {
    "PDF opens in a new tab for viewing or download.": "PDF yeni tabda baxış və ya yükləmə üçün açılır.",
    "JPG, PNG, WebP": "JPG, PNG, WebP",
    "Profiles, scores & attendance": "Profil, ballar və davamiyyət",
    "Total quiz time": "Ümumi quiz vaxtı",
    "Average": "Orta",
    "Longest": "Ən uzun",
    "Attempts": "Cəhdlər",
    "Compare how long each quiz attempt took.": "Hər quiz cəhdinin nə qədər çəkdiyini müqayisə edin.",
    "Newest first": "Əvvəlcə ən yeni",
    "Longest first": "Əvvəlcə ən uzun",
    "0:00": "0:00",
    "elapsed": "keçib",
    "entries": "qeyd",
    "Quiz and lesson scores grouped by day will show up here.": "Gün üzrə quiz və dərs balları burada görünəcək.",
    "No questions saved yet. Add the first one using the form on the right.": "Hələ sual yoxdur. Sağdakı formadan birincini əlavə edin.",
    "Pick a class session from the calendar, then mark one or more students.": "Təqvimdən dərs sessiyasını seçin, sonra bir və ya bir neçə tələbə üçün qeyd edin.",
    "Select one or more students, then choose a matching class session below.": "Bir və ya bir neçə tələbə seçin, sonra aşağıdan uyğun dərs sessiyasını seçin.",
    "The selected students are not in the same group, or have no scheduled class this week.": "Seçilmiş tələbələr eyni qrupda deyil və ya bu həftə planlaşdırılmış dərs yoxdur.",
    "Students appear here once they are assigned to your study groups in the admin panel.": "Tələbələr admin panelində tədris qruplarınıza təyin olunduqda burada görünəcək.",
    "Students inherit the course from the group you create — pick the matching course below.": "Tələbələr yaratdığınız qrupun kursunu miras alır — aşağıdan uyğun kursu seçin.",
    "No courses are assigned to your profile yet. Ask Academor administration to add course specializations.": "Profilinizə hələ kurs təyin olunmayıb. Academor administrasiyasından kurs ixtisasları əlavə etməsini xahiş edin.",
    "Track attendance across your groups and mark sessions in a few clicks.": "Qruplarınız üzrə davamiyyəti izləyin və bir neçə kliklə sessiyaları qeyd edin.",
    "When the student completes quizzes, time spent on each attempt appears here as an easy-to-read timeline.": "Tələbə quizləri tamamladıqda, hər cəhddə sərf olunan vaxt burada oxunaqlı xətt şəklində görünür.",
    "Your parent profile is not linked to any student accounts yet.": "Valideyn profiliniz hələ heç bir tələbə hesabına bağlanmayıb.",
    "Switch to light mode": "İşıqlı rejimə keç",
    "Switch to dark mode": "Qaranlıq rejimə keç",
}

RU = {
    "PDF opens in a new tab for viewing or download.": "PDF откроется в новой вкладке для просмотра или скачивания.",
    "JPG, PNG, WebP": "JPG, PNG, WebP",
    "Profiles, scores & attendance": "Профиль, оценки и посещаемость",
    "Total quiz time": "Общее время тестов",
    "Average": "Среднее",
    "Longest": "Самое длинное",
    "Attempts": "Попытки",
    "Compare how long each quiz attempt took.": "Сравните, сколько времени заняла каждая попытка.",
    "Newest first": "Сначала новые",
    "Longest first": "Сначала самые длинные",
    "0:00": "0:00",
    "elapsed": "прошло",
    "entries": "записей",
    "Quiz and lesson scores grouped by day will show up here.": "Оценки за тесты и уроки по дням появятся здесь.",
    "No questions saved yet. Add the first one using the form on the right.": "Вопросов пока нет. Добавьте первый через форму справа.",
    "Pick a class session from the calendar, then mark one or more students.": "Выберите занятие в календаре, затем отметьте одного или нескольких учеников.",
    "Select one or more students, then choose a matching class session below.": "Выберите одного или нескольких учеников, затем подходящее занятие ниже.",
    "The selected students are not in the same group, or have no scheduled class this week.": "Выбранные ученики не в одной группе или на этой неделе нет занятий.",
    "Students appear here once they are assigned to your study groups in the admin panel.": "Ученики появятся здесь после назначения в ваши группы в админке.",
    "Students inherit the course from the group you create — pick the matching course below.": "Курс наследуется от созданной группы — выберите подходящий курс ниже.",
    "No courses are assigned to your profile yet. Ask Academor administration to add course specializations.": "Курсы ещё не назначены. Попросите администрацию Academor добавить специализации.",
    "Track attendance across your groups and mark sessions in a few clicks.": "Отслеживайте посещаемость по группам и отмечайте занятия в несколько кликов.",
    "When the student completes quizzes, time spent on each attempt appears here as an easy-to-read timeline.": "После прохождения тестов время каждой попытки отображается здесь.",
    "Your parent profile is not linked to any student accounts yet.": "Родительский профиль ещё не привязан к ученикам.",
    "Switch to light mode": "Переключить на светлую тему",
    "Switch to dark mode": "Переключить на тёмную тему",
}


def fill(lang, mapping):
    if polib is None:
        print("polib not installed")
        return
    po_path = LOCALE / lang / "LC_MESSAGES" / "django.po"
    po = polib.pofile(str(po_path))
    updated = 0
    for entry in po:
        refs = " ".join(f"{path}:{line}" for path, line in entry.occurrences)
        if "templates/portals/" not in refs and "portals/static/portals/" not in refs:
            continue
        if entry.msgstr or not entry.msgid:
            continue
        if entry.msgid in mapping:
            entry.msgstr = mapping[entry.msgid]
            updated += 1
    po.save(str(po_path))
    print(f"{lang}: filled {updated} portal entries")


if __name__ == "__main__":
    fill("az", AZ)
    fill("ru", RU)
