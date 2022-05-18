"""
Tests for leafs APIs
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Leaf

from mindmap.serializers import LeafSerializer

LEAFS_URL = reverse('mindmap:leaf-list')


def detail_url(leaf_id):
    """Create and return an leaf detail URL."""
    return reverse('mindmap:leaf-detail', args=[leaf_id])


def create_user(email='test@example.com', password='testpass123'):
    """Create and return a user"""
    return get_user_model().objects.create_user(email=email, password=password)


class PublicLeafsApiTests(TestCase):
    """Unauthenticated Leafs API requests"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retrieving leafs"""
        res = self.client.get(LEAFS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateLeafsApiTests(TestCase):
    """Test authenticated Leafs API Requests"""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_leafs(self):
        """Test retrieving a list of leafs."""
        Leaf.objects.create(
            user=self.user,
            path='i/like/turtles',
            text='because/turtles'
        )
        Leaf.objects.create(
            user=self.user,
            path='i/eat/tomato',
            text='because/fruit'
        )

        res = self.client.get(LEAFS_URL)

        leafs = Leaf.objects.all().order_by('-path')
        serializer = LeafSerializer(leafs, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_leafs_limited_to_user(self):
        """Test that list of leafs is limit to authenticated user."""
        other_user = create_user(email='other@test.com')
        Leaf.objects.create(
            user=other_user,
            path='another/path',
            text='wrong'
        )
        leaf = Leaf.objects.create(
            user=self.user,
            path='what/fruit',
            text='right'
        )

        res = self.client.get(LEAFS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['path'], leaf.path)
        self.assertEqual(res.data[0]['id'], leaf.id)

    def test_update_leaf(self):
        """Test to update a leaf"""
        leaf = Leaf.objects.create(
            user=self.user,
            path='o/helo',
            text='no/way'
        )

        payload = {'path': 'oh/hello'}
        url = detail_url(leaf.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        leaf.refresh_from_db()
        self.assertEqual(leaf.path, payload['path'])

    def test_delete_leaf(self):
        """Test to delete a leaf"""
        leaf = Leaf.objects.create(
            user=self.user,
            path='o/helo',
            text='no/way'
        )

        url = detail_url(leaf.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        leafs = Leaf.objects.filter(user=self.user)
        self.assertFalse(leafs.exists())


