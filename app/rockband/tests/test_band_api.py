import tempfile
import os

from PIL import Image

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Band, Tag, Member

from rockband.serializers import BandSerializer, BandDetailSerializer

BAND_URL = reverse('rockband:band-list')


def image_upload_url(band_id):
    """
    Return URL for band image upload
    :param band_id:
    :return:
    """
    return reverse('rockband:band-upload-image', args=[band_id])


def detail_url(band_id):
    """
    Return band detail url
    """
    return reverse('rockband:band-detail', args=[band_id])


def sample_tag(user, name='Metal'):
    """
    Create and return a sample tag
    """
    return Tag.objects.create(user=user, name=name)


def sample_member(user, name='Attila'):
    """
    Create and return a sample tag
    :param user:
    :param name:
    :return:
    """
    return Member.objects.create(user=user, name=name)


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

    def test_view_band_detail(self):
        """
        Test viewing a band model
        :return:
        """
        band = sample_band(user=self.user)
        band.tags.add(sample_tag(user=self.user))
        band.members.add(sample_member(user=self.user))

        url = detail_url(band.id)
        res = self.client.get(url)

        serializer = BandDetailSerializer(band)
        self.assertEqual(res.data, serializer.data)

    def test_create_basic_band(self):
        """
        Test creating band
        :return:
        """
        payload = {
            'title': 'Iron Maiden',
            'band_members': 6,
            'tickets': 45.5
        }

        res = self.client.post(BAND_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        band = Band.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(band, key))

    def test_create_band_with_tags(self):
        """
        Test creating a band with tags
        :return:
        """
        tag1 = sample_tag(user=self.user, name='Power')
        tag2 = sample_tag(user=self.user, name='Symphonic')
        payload = {
            'title': 'Stratovarius',
            'tags': [tag1.id, tag2.id],
            'band_members': 5,
            'tickets': 29.9
        }
        res = self.client.post(BAND_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        band = Band.objects.get(id=res.data['id'])
        tags = band.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_band_with_members(self):
        """
        Test creating band with members
        :return:
        """
        member1 = sample_member(user=self.user, name='Joakim')
        member2 = sample_member(user=self.user, name='Par')
        payload = {
            'title': 'Sabaton',
            'members': [member1.id, member2.id],
            'band_members': 5,
            'tickets': 29.9
        }
        res = self.client.post(BAND_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        band = Band.objects.get(id=res.data['id'])
        members = band.members.all()
        self.assertEqual(members.count(), 2)
        self.assertIn(member1, members)
        self.assertIn(member2, members)

    def test_partial_update_band(self):
        """
        Test updating a band with patch
        :return:
        """
        band = sample_band(user=self.user)
        band.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user, name='Hard Rock')

        payload = {
            'title': 'Deep purple',
            'tags': [new_tag.id]
        }
        url = detail_url(band.id)
        self.client.patch(url, payload)

        band.refresh_from_db()
        self.assertEqual(band.title, payload['title'])
        tags = band.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    def test_full_update_band(self):
        """
        Test updating a band with put
        :return:
        """
        band = sample_band(user=self.user)
        band.tags.add(sample_tag(user=self.user))
        payload = {
            'title': 'Metallica',
            'band_members': 4,
            'tickets': 99.5
        }
        url = detail_url(band.id)
        self.client.put(url, payload)

        band.refresh_from_db()
        self.assertEqual(band.title, payload['title'])
        self.assertEqual(band.band_members, payload['band_members'])
        self.assertEqual(band.tickets, payload['tickets'])
        tags = band.tags.all()
        self.assertEqual(len(tags), 0)


class BandImageUploadTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@rockbanddev.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)
        self.band = sample_band(user=self.user)

    def teardown(self):
        self.band.image.delete()

    def test_upload_image_to_band(self):
        """
        Test uploading an image to band
        :return:
        """
        url = image_upload_url(self.band.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (10, 10))
            img.save(ntf, format='JPEG')
            ntf.seek(0)
            res = self.client.post(url, {'image': ntf}, format='multipart')

        self.band.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.band.image.path))

    def test_upload_image_bad_request(self):
        """
        Test uploading an invalid image
        :return:
        """
        url = image_upload_url(self.band.id)
        res = self.client.post(url, {'image': 'notimage'}, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_bands_by_tags(self):
        """
        Test returning bands with specific tags
        :return:
        """
        band1 = sample_band(user=self.user, title='Sabaton')
        band2 = sample_band(user=self.user, title='Slayer')
        tag1 = sample_tag(user=self.user, name='Power')
        tag2 = sample_tag(user=self.user, name='Thrash')
        band1.tags.add(tag1)
        band2.tags.add(tag2)
        band3 = sample_band(user=self.user, title='Rage')

        res = self.client.get(
            BAND_URL,
            {
                'tags': f'{tag1.id},{tag2.id}'
            }
        )

        serializer1 = BandSerializer(band1)
        serializer2 = BandSerializer(band2)
        serializer3 = BandSerializer(band3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_filter_bands_by_members(self):
        """
        Test returning bands with specific members
        :return:
        """

        band1 = sample_band(user=self.user, title='Sabaton')
        band2 = sample_band(user=self.user, title='Slayer')
        member1 = sample_member(user=self.user, name='Joakim')
        member2 = sample_member(user=self.user, name='Araya')
        band1.members.add(member1)
        band2.members.add(member2)
        band3 = sample_band(user=self.user, title='Rage')

        res = self.client.get(
            BAND_URL,
            {
                'members': f'{member1.id},{member2.id}'
            }
        )

        serializer1 = BandSerializer(band1)
        serializer2 = BandSerializer(band2)
        serializer3 = BandSerializer(band3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)
