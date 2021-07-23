from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Band

from rockband.serializers import BandSerializer

BAND_URL = reverse('rockband:band-list')


def sample_band(user, **params):
    """
    Create and return a sample band
    :param user:
    :param params:
    :return: sample band
    """
    defaults = {
        'title': 'Sample Band',
        'band_members': 5,
        'tickets': 25.99
    }
    defaults.update(params)

    return Band.objects.create(user=user, **defaults)


class PublicBandApiTests(TestCase):
    """
    Test unauthenticated band API access
    """

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """
        Test that authentication is required
        :return:
        """
        res = self.client.get(BAND_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateBandApiTests(TestCase):
    """
    Test unauthenticated band API access
    """

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@rockbanddev.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_bands(self):
        """
        Test retrieving a list of bands
        :return:
        """
        sample_band(user=self.user)
        sample_band(user=self.user)

        res = self.client.get(BAND_URL)

        bands = Band.objects.all().order_by('-id')
        serializer = BandSerializer(bands, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_bands_limited_to_user(self):
        """
        test retrieving bands for user
        :return:
        """
        user2 = get_user_model().objects.create_user(
            'other@rockbanddevv.com',
            'testpass2'
        )
        sample_band(user=user2)
        sample_band(user=self.user)

        res = self.client.get(BAND_URL)

        bands = Band.objects.filter(user=self.user)
        serializer = BandSerializer(bands, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)
