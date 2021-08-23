from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def sample_user(email='test@rockbanddev.com', password='testpass'):
    """Create a sample user"""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Test creating a new user with an e-mail is successful"""
        email = 'test@unicorndev.com'
        password = 'Testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized"""
        email = 'test@ROCKBANDDEV.COM'
        user = get_user_model().objects.create_user(
            email,
            'test123'
        )

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating user with no email raisesw error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123')

    def test_create_new_superuser(self):
        """Test creating a new superuser"""
        user = get_user_model().objects.create_superuser(
            'test@rockbanddev.com',
            'test123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """Test the tag string representation"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Power Metal'
        )

        self.assertEqual(str(tag), tag.name)

    def test_members_str(self):
        """
        Test the ingredient string representation
        :return:
        """
        member = models.Member.objects.create(
            user=sample_user(),
            name='Hendrix'
        )

        self.assertEqual(str(member), member.name)

    def test_band_str(self):
        """
        Test the band string representation
        :return:
        """
        band = models.Band.objects.create(
            user=sample_user(),
            title='Metallica',
            band_members=4,
            tickets=20.0
        )

        self.assertEqual(str(band), band.title)

    @patch('uuid.uuid4')
    def test_band_file_name_uuid(self, mock_uuid):
        """
        Test that image is saved in the correct location
        :return:
        """
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.band_image_file_path(None, 'myimage.jpg')

        exp_path = f'uploads/band/{uuid}.jpg'
        self.assertEqual(file_path, exp_path)
