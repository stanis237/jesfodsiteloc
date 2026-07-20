from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Member, FinanceEntry

class MemberModelTests(TestCase):
    def setUp(self):
        # Create a user and associated Member
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.member = Member.objects.create(
            user=self.user,
            name='Test Member',
            email='test@example.com',
            role='bureau',  # bureau member for profile view reduction
            position='president',
        )
        # Finance entries
        FinanceEntry.objects.create(member=self.member, type='inscription', amount=1000, is_paid=True)
        FinanceEntry.objects.create(member=self.member, type='fdr', amount=5000, is_paid=True)
        # Initially create a paid amande so total_amendes = 0 for a_jour test
        FinanceEntry.objects.create(member=self.member, type='amande', amount=200, is_paid=True)
        FinanceEntry.objects.create(member=self.member, type='tontine', amount=3000, is_paid=True)

    def test_is_bureau_property(self):
        self.assertTrue(self.member.is_bureau)

    def test_total_fdr(self):
        self.assertEqual(self.member.total_fdr, 5000)

    def test_total_amendes(self):
        # Only paid amande counted, amount=200
        self.assertEqual(self.member.total_amendes, 0)

    def test_total_tontine(self):
        self.assertEqual(self.member.total_tontine, 3000)

    def test_inscription_paid(self):
        self.assertTrue(self.member.inscription_paid)

    def test_situation_a_jour(self):
        # No unpaid amendes and inscription paid => 'a_jour'
        self.assertEqual(self.member.situation, 'a_jour')

    def test_situation_pas_a_jour_when_unpaid(self):
        # Add an unpaid amende
        FinanceEntry.objects.create(member=self.member, type='amande', amount=100, is_paid=False)
        self.assertEqual(self.member.situation, 'pas_a_jour')

class ProfileViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='bureau_user', password='secret')
        self.member = Member.objects.create(
            user=self.user,
            name='Bureau User',
            email='bureau@example.com',
            role='bureau',
            phone='0123456789',
            school_level='lycee',
            position='president',
        )
        self.client.login(username='bureau_user', password='secret')

    def test_profile_view_hides_fields_for_bureau(self):
        response = self.client.get(reverse('profile'))  # assuming url name 'profile'
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        # Fields wrapped in the conditional should not appear
        self.assertNotIn('Téléphone', content)
        self.assertNotIn('Niveau scolaire', content)
        self.assertNotIn('Rôle', content)

    def test_profile_view_shows_fields_for_reunion(self):
        # Change role to reunion and reload
        self.member.role = 'reunion'
        self.member.save()
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        # The French labels and phone number should be present
        self.assertIn('Téléphone', content)
        self.assertIn('0123456789', content)
        self.assertIn('Niveau scolaire', content)
        self.assertIn('Rôle', content)
