"""
Tests for MindMap API.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    MindMap,
)

from mindmap.serializers import (
    MindMapSerializer,
)
MINDMAPS_URL = reverse('mindmap:mindmap-list')


def create_user(**params):
    """Helper method to create users"""
    return get_user_model().objects.create_user(**params)


def detail_url(mindmap_id):
    """Create and return a mindmap detail URL."""
    return reverse('mindmap:mindmap-detail', args=[mindmap_id])


def create_mindmap(user, **params):
    """Create and return a sample mindmap."""
    defaults = {
        'title': 'Sample mindmap title',
    }

    defaults.update(params)

    mindmap = MindMap.objects.create(user=user, **defaults)
    return mindmap


class PublicMindMapAPITests(TestCase):
    """Tests with unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required to call API."""
        res = self.client.get(MINDMAPS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateMindMapAPITests(TestCase):
    """Tests with authenticated users on MindMap requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='user@example.com',
            password='testpass123',
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_mindmaps(self):
        """Test that retrieves a list of mindmaps."""
        create_mindmap(user=self.user)
        create_mindmap(user=self.user)

        res = self.client.get(MINDMAPS_URL)

        mindmaps = MindMap.objects.all().order_by('-id')
        serializer = MindMapSerializer(mindmaps, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_mindmap_list_limited_to_user(self):
        """Test the list of mindmaps is limited to authenticated user."""
        other_user = create_user(
            email='email@test.com',
            password='password123',
        )

        create_mindmap(user=other_user)
        create_mindmap(user=self.user)

        res = self.client.get(MINDMAPS_URL)

        mindmaps = MindMap.objects.filter(user=self.user)
        serializer = MindMapSerializer(mindmaps, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_mindmap(self):
        """Test Creating a mindmap through API call"""
        payload = {
            'title': 'Sample MindMap'
        }

        res = self.client.post(MINDMAPS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        mindmap = MindMap.objects.get(id=res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(mindmap, k), v)
        self.assertEqual(mindmap.user, self.user)

    def test_partial_update(self):
        """Test partial update of MindMap"""
        mindmap = create_mindmap(
            user=self.user,
            title='First Title',
        )

        payload = {'title': 'Second Title'}
        url = detail_url(mindmap.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        mindmap.refresh_from_db()
        self.assertEqual(mindmap.title, payload['title'])
        self.assertEqual(mindmap.user, self.user)

    def test_update_user_returns_error(self):
        """Test when updating mindmap user does not change user"""
        other_user = create_user(
            email='test@test.com',
            password='testpass123'
        )

        mindmap = create_mindmap(user=self.user)

        payload = {
            'user': other_user.id
        }
        url = detail_url(mindmap.id)
        self.client.patch(url, payload)

        mindmap.refresh_from_db()
        self.assertEqual(mindmap.user, self.user)

    def test_delete_mindmap(self):
        """Test that deleting a mindmap is successful"""
        mindmap = create_mindmap(
            user=self.user
        )

        url = detail_url(mindmap.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(MindMap.objects.filter(id=mindmap.id).exists())

    def test_delete_other_users_mindmap_error(self):
        """Test that user cannot delete another user's mindmap."""
        other_user = create_user(
            email='test1@example.com',
            password='testpass123',
        )
        mindmap = create_mindmap(
            user=other_user
        )

        url = detail_url(mindmap.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(MindMap.objects.filter(id=mindmap.id).exists())
