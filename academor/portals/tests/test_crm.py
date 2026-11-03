from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from portals.models import Lead, LeadActivity, StudentCharge, StudentPayment, StudentProfile, StudyGroup, TeacherProfile
from portals.utils import crm
from projects.models import ContactInquiry

User = get_user_model()


class CrmBase(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user('manager', password='pass12345', is_staff=True)
        teacher = TeacherProfile.objects.create(user=User.objects.create(username='crm_teacher'))
        self.group = StudyGroup.objects.create(teacher=teacher, name='IELTS Axşam', monthly_fee=Decimal('180'))
        self.student = StudentProfile.objects.create(user=User.objects.create(username='crm_student'), phone='+994551234567')
        self.group.students.add(self.student)


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
    def test_monthly_charges_are_created_once(self):
        period = date(2026, 10, 1)
        first = crm.generate_monthly_charges(period)
        again = crm.generate_monthly_charges(period)
        self.assertEqual((first['created'], again['created'], again['skipped']), (1, 0, 1))
        charge = StudentCharge.objects.get()
        self.assertEqual((charge.amount, charge.due_date), (Decimal('180'), date(2026, 10, 10)))

    def test_payments_cover_the_oldest_charges_first(self):
        for m in (8, 9, 10):
            crm.generate_monthly_charges(date(2026, m, 1))
        StudentPayment.objects.create(student=self.student, amount=Decimal('270'))
        ledger = crm.student_ledger(self.student)
        states = [r['state'] for r in sorted(ledger['charges'], key=lambda r: r['charge'].due_date)]
        self.assertEqual(states[:2], ['paid', 'overdue'] if date(2026, 9, 10) < timezone.localdate() else ['paid', 'partial'])
        self.assertEqual(ledger['balance'], Decimal('270'))
        debt = crm.debtors()[0]
        self.assertEqual(debt['student'], self.student)
        self.assertEqual(debt['balance'], Decimal('270'))

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
        crm.generate_monthly_charges(timezone.localdate().replace(day=1))
        pay = StudentPayment.objects.create(student=self.student, amount=Decimal('100'))
        urls = [
            reverse('crm:dashboard'), reverse('crm:leads'), reverse('crm:leads') + '?view=list',
            reverse('crm:lead', args=[lead.pk]), reverse('crm:lead_new'), reverse('crm:students'),
            reverse('crm:student', args=[self.student.pk]), reverse('crm:payments'), reverse('crm:payment_new'),
            reverse('crm:charge_new'), reverse('crm:payment_receipt', args=[pay.pk]), reverse('crm:debts'),
            reverse('crm:groups'), reverse('crm:attendance'), reverse('crm:search') + '?q=Rauf',
        ]
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

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

    def test_taking_a_payment_opens_the_receipt(self):
        self.client.force_login(self.staff)
        response = self.client.post(reverse('crm:payment_new'), {
            'student': self.student.pk, 'amount': '180', 'method': 'cash', 'paid_at': '2026-11-03',
        })
        pay = StudentPayment.objects.get()
        self.assertRedirects(response, reverse('crm:payment_receipt', args=[pay.pk]))
        self.assertEqual(pay.received_by, self.staff)

    def test_group_fee_can_be_set_from_the_groups_page(self):
        self.client.force_login(self.staff)
        self.client.post(reverse('crm:groups'), {'group': self.group.pk, 'monthly_fee': '200,50'})
        self.group.refresh_from_db()
        self.assertEqual(self.group.monthly_fee, Decimal('200.50'))


class AdminLoginLandsOnCrmTests(CrmBase):
    def test_login_without_next_goes_to_the_crm(self):
        response = self.client.post(reverse('admin:login'), {'username': 'manager', 'password': 'pass12345'})
        self.assertRedirects(response, reverse('crm:dashboard'), fetch_redirect_response=False)

    def test_login_with_next_keeps_it(self):
        url = reverse('admin:login') + '?next=' + reverse('admin:index')
        response = self.client.post(url, {'username': 'manager', 'password': 'pass12345'})
        self.assertRedirects(response, reverse('admin:index'), fetch_redirect_response=False)
