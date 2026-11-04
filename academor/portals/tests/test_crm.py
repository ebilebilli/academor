from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from portals.models import (
    Enrollment, Lead, LeadActivity, StudentCharge, StudentPayment, StudentProfile, StudyGroup, TeacherProfile,
)
from portals.utils import crm
from projects.models import ContactInquiry

User = get_user_model()


class CrmBase(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user('manager', password='pass12345', is_staff=True)
        self.teacher = TeacherProfile.objects.create(user=User.objects.create(username='Demo Müəllim'))
        self.group = StudyGroup.objects.create(teacher=self.teacher, name='IELTS Axşam', max_students=4)
        self.student = StudentProfile.objects.create(user=User.objects.create(username='Test Tələbə'), phone='+994551234567')
        self.group.students.add(self.student)

    def enroll(self, **kw):
        data = dict(student=self.student, course='IELTS', group=self.group, teacher=self.teacher,
                    monthly_fee=Decimal('180'), teacher_percent=Decimal('50'), start_date=date(2026, 8, 17))
        data.update(kw)
        return Enrollment.objects.create(**data)


class LeadCaptureTests(CrmBase):
    def test_contact_form_becomes_a_lead_and_repeat_is_logged(self):
        with self.captureOnCommitCallbacks(execute=True):
            ContactInquiry.objects.create(full_name='Aysu', mobile_number='055 111 22 33', subject='IELTS')
        lead = Lead.objects.get()
        self.assertEqual((lead.source, lead.status, lead.interest), ('contact_form', 'new', 'IELTS'))
        self.assertIsNotNone(lead.contact_inquiry_id)
        # same number written differently: no second card, the enquiry is logged on the first one
        with self.captureOnCommitCallbacks(execute=True):
            ContactInquiry.objects.create(full_name='Aysu M.', mobile_number='+994 55 111 22 33', subject='SAT')
        self.assertEqual(Lead.objects.count(), 1)
        self.assertTrue(lead.activities.filter(kind=LeadActivity.Kind.MESSAGE, text__contains='SAT').exists())


class BillingTests(CrmBase):
    def test_each_enrollment_is_billed_on_its_own_day_once(self):
        e = self.enroll(first_due_date=date(2026, 8, 31))
        today = date(2026, 11, 3)
        self.assertEqual(crm.sync_charges(today=today), 3)  # 31.08, 30.09, 31.10
        self.assertEqual(crm.sync_charges(today=today), 0)
        dues = list(StudentCharge.objects.order_by('due_date').values_list('due_date', flat=True))
        self.assertEqual(dues, [date(2026, 8, 31), date(2026, 9, 30), date(2026, 10, 31)])
        self.assertEqual(e.due_date_for(6), date(2027, 2, 28))

    def test_a_cancelled_month_is_not_billed_again(self):
        self.enroll(start_date=date(2026, 10, 5))
        crm.sync_charges(today=date(2026, 10, 20))
        StudentCharge.objects.update(is_cancelled=True)
        self.assertEqual(crm.sync_charges(today=date(2026, 10, 25)), 0)

    def test_waiting_and_zero_fee_enrollments_are_not_billed(self):
        self.enroll(status=Enrollment.Status.WAITING)
        self.enroll(course='Speaking', monthly_fee=0)
        self.assertEqual(crm.sync_charges(today=date(2026, 11, 3)), 0)

    def test_payments_settle_their_own_course_first_and_one_offs_are_not_credit(self):
        ielts = self.enroll(start_date=date(2026, 9, 1))
        gre = self.enroll(course='GRE Math', monthly_fee=Decimal('250'), start_date=date(2026, 10, 1))
        crm.sync_charges(today=date(2026, 10, 15))  # IELTS: Sep + Oct, GRE: Oct
        StudentPayment.objects.create(student=self.student, enrollment=ielts, amount=Decimal('360'))
        StudentPayment.objects.create(student=self.student, course='IELTS Mock test', amount=Decimal('10'))
        b = crm.balances()[self.student.pk]
        self.assertEqual((b.debt, b.credit), (Decimal('250'), Decimal('0')))
        ledger = crm.student_ledger(self.student)
        self.assertEqual(ledger['debt_by_enrollment'][gre.pk], Decimal('250'))
        self.assertEqual(ledger['debt_by_enrollment'][ielts.pk], Decimal('0'))
        self.assertEqual(crm.debtors()[0]['courses'], ['GRE Math', 'IELTS'])

    def test_teacher_share_follows_the_percent(self):
        e = self.enroll()
        pay = StudentPayment(student=self.student, enrollment=e, amount=Decimal('130'), teacher=self.teacher,
                             teacher_percent=Decimal('32.2'))
        pay.apply_teacher_share()
        pay.save()
        self.assertEqual((pay.teacher_amount, pay.teacher_status, pay.course), (Decimal('41.86'), 'pending', 'IELTS'))
        zero = StudentPayment(student=self.student, amount=Decimal('160'), teacher=self.teacher, course='GE')
        zero.apply_teacher_share()
        self.assertEqual((zero.teacher_amount, zero.teacher_status), (Decimal('0'), 'none'))

    def test_leaving_cancels_later_unpaid_months(self):
        e = self.enroll(start_date=date(2026, 8, 10))
        crm.sync_charges(today=date(2026, 11, 3))
        e.status, e.ended_at = Enrollment.Status.LEFT, date(2026, 9, 20)
        e.save()
        self.assertEqual(crm.close_enrollment_billing(e), 1)  # 10.10 cancelled, 10.08 + 10.09 stay

    def test_receipt_number_is_assigned(self):
        pay = StudentPayment.objects.create(student=self.student, amount=Decimal('50'), paid_at=date(2026, 11, 3))
        self.assertEqual(pay.receipt_number, f'Q-2611-{pay.pk:05d}')


class CrmViewTests(CrmBase):
    def test_pages_need_staff(self):
        response = self.client.get(reverse('crm:dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response['Location'])

    def test_all_pages_render_for_staff(self):
        self.client.force_login(self.staff)
        lead = Lead.objects.create(full_name='Rauf', phone='0501112233', source='phone')
        e = self.enroll(start_date=timezone.localdate() - timedelta(days=40))
        pay = StudentPayment.objects.create(student=self.student, enrollment=e, amount=Decimal('100'),
                                            teacher=self.teacher, teacher_percent=50, teacher_amount=50)
        urls = [
            reverse('crm:dashboard'), reverse('crm:leads'), reverse('crm:leads') + '?view=list',
            reverse('crm:lead', args=[lead.pk]), reverse('crm:lead_new'), reverse('crm:lead_convert', args=[lead.pk]),
            reverse('crm:student_new'), reverse('crm:student_edit', args=[self.student.pk]),
            reverse('crm:enrollment_new', args=[self.student.pk]), reverse('crm:enrollment_edit', args=[e.pk]),
            reverse('crm:student', args=[self.student.pk]), reverse('crm:payments'), reverse('crm:payment_new'),
            reverse('crm:payment_new') + f'?student={self.student.pk}', reverse('crm:payment_edit', args=[pay.pk]),
            reverse('crm:charge_new'), reverse('crm:payment_receipt', args=[pay.pk]), reverse('crm:debts'),
            reverse('crm:teachers'), reverse('crm:reports'), reverse('crm:reports') + '?month=all',
            reverse('crm:groups'), reverse('crm:group_new'), reverse('crm:group_edit', args=[self.group.pk]),
            reverse('crm:attendance'), reverse('crm:search') + '?q=Rauf',
        ] + [reverse('crm:students') + f'?tab={t}' for t in ('active', 'waiting', 'left', 'none', 'all')]
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)
        self.assertTrue(StudentCharge.objects.filter(enrollment=e).exists())  # billed on the visit

    def test_board_move_changes_status_and_logs_it(self):
        self.client.force_login(self.staff)
        lead = Lead.objects.create(full_name='Rauf', source='phone')
        response = self.client.post(
            reverse('crm:lead_move', args=[lead.pk]), data='{"status": "trial"}', content_type='application/json',
        )
        self.assertEqual(response.json(), {'ok': True, 'status': 'trial'})
        lead.refresh_from_db()
        self.assertEqual(lead.status, 'trial')
        self.assertTrue(lead.activities.filter(kind='status').exists())

    def test_board_move_to_enrolled_asks_to_convert(self):
        self.client.force_login(self.staff)
        lead = Lead.objects.create(full_name='Demo Müraciət', phone='0501234567', interest='General English')
        response = self.client.post(
            reverse('crm:lead_move', args=[lead.pk]), data='{"status": "enrolled"}', content_type='application/json',
        )
        self.assertEqual(response.json()['redirect'], reverse('crm:lead_convert', args=[lead.pk]))

    def test_converting_a_lead_creates_the_student_and_course(self):
        self.client.force_login(self.staff)
        lead = Lead.objects.create(full_name='Demo Müraciət', phone='0501234567', interest='General English')
        response = self.client.post(reverse('crm:lead_convert', args=[lead.pk]), {
            's-full_name': 'Demo Müraciət', 's-phone': '050 123 45 67',
            'e-course': 'General English', 'e-group': self.group.pk, 'e-monthly_fee': '130', 'e-teacher_percent': '50',
            'e-start_date': '2026-11-04', 'e-status': 'active',
        })
        lead.refresh_from_db()
        st = lead.student
        self.assertRedirects(response, reverse('crm:student', args=[st.pk]))
        self.assertEqual((lead.status, st.full_name, st.phone), ('enrolled', 'Demo Müraciət', '050 123 45 67'))
        e = st.crm_enrollments.get()
        self.assertEqual((e.monthly_fee, e.teacher, e.lead), (Decimal('130'), self.teacher, lead))  # teacher from group
        self.assertTrue(self.group.students.filter(pk=st.pk).exists())
        self.assertFalse(st.user.has_usable_password())

    def test_new_student_with_same_name_gets_a_distinct_login(self):
        self.client.force_login(self.staff)
        self.client.post(reverse('crm:student_new'), {
            's-full_name': 'Test Tələbə', 'e-course': 'SAT', 'e-monthly_fee': '200', 'e-teacher_percent': '0',
            'e-start_date': '2026-11-04', 'e-status': 'waiting',
        })
        self.assertTrue(User.objects.filter(username='Test Tələbə 2').exists())

    def test_full_group_is_refused(self):
        self.client.force_login(self.staff)
        self.group.max_students = 1
        self.group.save()
        response = self.client.post(reverse('crm:student_new'), {
            's-full_name': 'Yeni Tələbə', 'e-course': 'IELTS', 'e-group': self.group.pk, 'e-monthly_fee': '180',
            'e-teacher_percent': '50', 'e-start_date': '2026-11-04', 'e-status': 'active',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Qrup doludur')

    def test_taking_a_payment_opens_the_receipt_and_counts_the_teacher(self):
        self.client.force_login(self.staff)
        e = self.enroll()
        response = self.client.post(reverse('crm:payment_new'), {
            'student': self.student.pk, 'enrollment': e.pk, 'amount': '180', 'method': 'card_up',
            'paid_at': '2026-11-03', 'is_new_customer': 'on',
        })
        pay = StudentPayment.objects.get()
        self.assertRedirects(response, reverse('crm:payment_receipt', args=[pay.pk]))
        self.assertEqual((pay.received_by, pay.teacher, pay.teacher_amount, pay.course),
                         (self.staff, self.teacher, Decimal('90.00'), 'IELTS'))

    def test_payment_for_someone_elses_course_is_refused(self):
        self.client.force_login(self.staff)
        other = StudentProfile.objects.create(user=User.objects.create(username='other'))
        e = self.enroll(student=other)
        response = self.client.post(reverse('crm:payment_new'), {
            'student': self.student.pk, 'enrollment': e.pk, 'amount': '180', 'method': 'cash', 'paid_at': '2026-11-03',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(StudentPayment.objects.exists())

    def test_marking_a_teacher_month_paid(self):
        self.client.force_login(self.staff)
        e = self.enroll()
        for d in (date(2026, 10, 2), date(2026, 11, 2)):
            p = StudentPayment(student=self.student, enrollment=e, amount=Decimal('100'), paid_at=d,
                               teacher=self.teacher, teacher_percent=50)
            p.apply_teacher_share()
            p.save()
        self.client.post(reverse('crm:teachers'), {'teacher': self.teacher.pk, 'month': '2026-11'})
        statuses = dict(StudentPayment.objects.values_list('paid_at', 'teacher_status'))
        self.assertEqual(statuses, {date(2026, 10, 2): 'pending', date(2026, 11, 2): 'paid'})

    def test_new_group_with_lesson_days(self):
        self.client.force_login(self.staff)
        self.client.post(reverse('crm:group_new'), {
            'name': 'General English 2/4', 'teacher': self.teacher.pk, 'max_students': 6, 'is_active': 'on',
            'days': ['1', '3'], 'start_time': '11:00', 'duration_min': 90,
        })
        g = StudyGroup.objects.get(name='General English 2/4')
        self.assertEqual(sorted(g.schedules.values_list('weekday', flat=True)), [1, 3])

    def test_student_password_is_shown_once(self):
        self.client.force_login(self.staff)
        response = self.client.post(reverse('crm:student_password', args=[self.student.pk]))
        password = response.context['new_password']
        self.student.user.refresh_from_db()
        self.assertTrue(self.student.user.check_password(password))


class AdminLoginLandsOnCrmTests(CrmBase):
    def test_login_without_next_goes_to_the_crm(self):
        response = self.client.post(reverse('admin:login'), {'username': 'manager', 'password': 'pass12345'})
        self.assertRedirects(response, reverse('crm:dashboard'), fetch_redirect_response=False)

    def test_login_with_next_keeps_it(self):
        url = reverse('admin:login') + '?next=' + reverse('admin:index')
        response = self.client.post(url, {'username': 'manager', 'password': 'pass12345'})
        self.assertRedirects(response, reverse('admin:index'), fetch_redirect_response=False)


def _xlsx(path, sheets):
    """Tiny .xlsx writer for tests: {sheet name: [[cell, ...], ...]} (str → inline string, number → number)."""
    import zipfile
    from xml.sax.saxutils import escape

    def col(i):
        s = ''
        i += 1
        while i:
            i, r = divmod(i - 1, 26)
            s = chr(65 + r) + s
        return s

    with zipfile.ZipFile(path, 'w') as z:
        z.writestr('[Content_Types].xml', '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>')
        names = list(sheets)
        z.writestr('xl/workbook.xml', (
            '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>'
            + ''.join(f'<sheet name="{escape(n)}" sheetId="{i + 1}" r:id="rId{i + 1}"/>' for i, n in enumerate(names))
            + '</sheets></workbook>'))
        z.writestr('xl/_rels/workbook.xml.rels', (
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            + ''.join(f'<Relationship Id="rId{i + 1}" Target="worksheets/sheet{i + 1}.xml" Type="x"/>' for i in range(len(names)))
            + '</Relationships>'))
        for i, n in enumerate(names):
            rows = []
            for r, row in enumerate(sheets[n], start=1):
                cells = []
                for c, v in enumerate(row):
                    ref = f'{col(c)}{r}'
                    if v is None:
                        continue
                    if isinstance(v, (int, float)):
                        cells.append(f'<c r="{ref}"><v>{v}</v></c>')
                    else:
                        cells.append(f'<c r="{ref}" t="inlineStr"><is><t>{escape(str(v))}</t></is></c>')
                rows.append(f'<row r="{r}">{"".join(cells)}</row>')
            z.writestr(f'xl/worksheets/sheet{i + 1}.xml', (
                '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>'
                + ''.join(rows) + '</sheetData></worksheet>'))


def _serial(d):
    return (d - date(1899, 12, 30)).days


class ExcelImportTests(TestCase):
    def setUp(self):
        import tempfile

        self.dir = tempfile.mkdtemp()
        self.students = f'{self.dir}/qrup.xlsx'
        self.payments = f'{self.dir}/idare.xlsx'
        _xlsx(self.students, {
            'Tələbələr': [
                ['№', 'Ad Soyad', 'Telefon', 'Status', 'Qrup', 'Fənn', 'Müəllim', 'İştirak', 'Cəmi dərs', 'Qayıb',
                 'Davamiyyət %', 'Qeyd', 'Başlama', 'Doğum Tarixi'],
                [1, 'Ayan Nurlu', '50 000 11 22', 'Aktiv', 'General English 3/6', 'General English', 'Demo Müəllim',
                 None, None, None, None, None, _serial(date(2026, 9, 19)), _serial(date(2010, 1, 2))],
                [2, 'Kənan Dağlı', '50 000 11 22', 'Gözləyir', None, 'IELTS', 'Demo Müəllim',
                 None, None, None, None, None, _serial(date(2026, 10, 1))],
            ],
            'Qruplar': [
                ['№', 'Qrup Adı', 'Fənn', 'Müəllim', 'Saat', 'Be (Bazar ertəsi)', 'Ça (Çərşənbə axşamı)', 'Ç (Çərşənbə)',
                 'Ca (Cümə axşamı)', 'C (Cümə)', 'Ş (Şənbə)', 'B (Bazar)', 'Tələbə', 'Maks'],
                [1, 'General English 3/6', 'General English', 'Demo Müəllim', '18:30 - 20:00', None, None, '✓',
                 None, None, '✓', None, 1, 4],
            ],
            'Ayrılanlar': [
                ['ACADEMOR | Ayrılanlar'],
                ['№', 'Ad Soyad', 'Telefon', 'Fənn', 'Başladı', 'Ayrıldı', 'Səbəb', 'Ay', 'Status'],
                [1, 'Solmaz Demo', '50 000 00 31', 'General English', _serial(date(2026, 4, 16)), _serial(date(2026, 5, 16)),
                 'Vaxt problemi', 1, 'Ayrıldı'],
            ],
        })
        header = ['Tarix', 'Ay', 'Ad Soyad', 'Telefon', 'Kurs', 'Fənn (orijinal)', 'Məbləğ (₼)', 'Ödəniş Üsulu',
                  'Status', 'Qalıq Borc (₼)', 'Yeni Müştəri?', 'Müəllim', 'Müəllim Faizi (%)', 'Müəllimə Gedən (₼)',
                  'Kursa Qalan (₼)', 'Növbəti Ödəniş', 'Qeyd', 'Müəllimə ödənilib?']
        _xlsx(self.payments, {
            '💳 Ödənişlər': [
                ['TƏLƏBƏ ÖDƏNİŞLƏRİ'], header,
                [_serial(date(2026, 9, 19)), '2026-09', 'Ayan Nurlu', '050-000-11-22', 'General English', 'GE',
                 95, 'Kart - up', 'Ödənilib', None, 'Bəli ✔', 'Demo Müəllim', 0.5, 47.5, 47.5,
                 _serial(date(2026, 10, 19)), 'Konrakt ve ödəniş oldu', 'Bəli ✔'],
                [_serial(date(2026, 10, 19)), '2026-10', 'Ayan Nurlu', '050-000-11-22', 'General English', 'GE',
                 95, 'Nağd', 'Ödənilib', None, 'Xeyr', 'Demo Müəllim', 0.5, 47.5, 47.5,
                 _serial(date(2026, 11, 19)), '', 'Xeyr'],
                [_serial(date(2026, 4, 16)), '2026-04', 'Solmaz Demo', '50-000-00-31', 'General English', 'GE',
                 160, 'Kart', 'Ödənilib', None, 'Bəli ✔', 'Keçmiş Müəllim', 0, 0, 160, None, '', 'Verilməyəcək'],
                [_serial(date(2026, 10, 2)), '2026-10', 'Birdəfəlik Qonaq', '50 000 00 41', 'IELTS Mock test', 'Mock',
                 10, 'Nağd', 'Ödənilib', None, 'Bəli ✔', None, 0, 0, 10, None, 'Tək səfərlik ödəniş', None],
                [_serial(date(2026, 10, 1)), '2026-10', 'Borclu Demo', '55 000 00 01', 'English for Kids', 'Kids',
                 100, None, 'Ödənilməyib', None, 'Xeyr', 'Üçüncü Müəllim', 0, 0, 0, None, '', None],
            ],
        })

    def run_import(self, *extra):
        from io import StringIO

        from django.core.management import call_command

        out = StringIO()
        call_command('import_crm_excel', '--students', self.students, '--payments', self.payments, *extra, stdout=out)
        return out.getvalue()

    def test_dry_run_saves_nothing(self):
        self.run_import()
        self.assertFalse(StudentProfile.objects.exists())

    def test_import_builds_students_courses_and_settled_history(self):
        self.run_import('--commit')
        first = StudentProfile.objects.get(user__username='Ayan Nurlu')
        second = StudentProfile.objects.get(user__username='Kənan Dağlı')  # same phone, different person
        self.assertNotEqual(first, second)
        e = first.crm_enrollments.get()
        self.assertEqual((e.course, e.monthly_fee, e.teacher_percent, e.first_due_date, e.status, e.group.name),
                         ('General English', Decimal('95'), Decimal('50'), date(2026, 11, 19), 'active',
                          'General English 3/6'))
        self.assertEqual(sorted(e.group.schedules.values_list('weekday', flat=True)), [2, 5])
        self.assertEqual(first.birth_date, date(2010, 1, 2))
        self.assertEqual(second.crm_enrollments.get().status, 'waiting')
        left = Enrollment.objects.get(student__user__username='Solmaz Demo')
        self.assertEqual((left.status, left.ended_at, left.leave_reason), ('left', date(2026, 5, 16), 'Vaxt problemi'))
        pays = StudentPayment.objects.filter(student=first).order_by('paid_at')
        self.assertEqual([(p.method, p.teacher_status, p.teacher_amount, p.is_new_customer) for p in pays],
                         [('card_up', 'paid', Decimal('47.5'), True), ('cash', 'pending', Decimal('47.5'), False)])
        mock = StudentPayment.objects.get(course='IELTS Mock test')
        self.assertIsNone(mock.enrollment)
        # history is settled; the unpaid row is a debt, not a payment
        crm.sync_charges(today=date(2026, 11, 4))
        bal = crm.balances()
        self.assertEqual(bal[first.pk].debt, Decimal('0'))
        debtor = StudentProfile.objects.get(user__username='Borclu Demo')
        self.assertEqual(bal[debtor.pk].debt, Decimal('100'))
        self.assertFalse(StudentPayment.objects.filter(student=debtor).exists())

    def test_running_twice_adds_nothing(self):
        self.run_import('--commit')
        counts = (Enrollment.objects.count(), StudentPayment.objects.count(), StudentCharge.objects.count(),
                  StudentProfile.objects.count())
        out = self.run_import('--commit')
        self.assertEqual(counts, (Enrollment.objects.count(), StudentPayment.objects.count(),
                                  StudentCharge.objects.count(), StudentProfile.objects.count()))
        self.assertIn('payments already there: 4', out)


class ReportTests(CrmBase):
    def test_breakdown_lists_each_course_once(self):
        for d in (date(2026, 10, 1), date(2026, 10, 9), date(2026, 10, 20)):
            StudentPayment.objects.create(student=self.student, course='IELTS', amount=Decimal('100'), paid_at=d)
        rows = crm.breakdown(date(2026, 10, 1), date(2026, 10, 31), 'course')
        self.assertEqual([(r['key'], r['revenue'], r['n']) for r in rows], [('IELTS', Decimal('300'), 3)])
