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
    Leaf,
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

    def test_create_mindmap_with_new_leafs(self):
        """Test creating a mindmap with new leafs"""
        payload = {
            'title': 'MindMap Sample',
            'leafs': [{'path': 'o/helo', 'text': 'because/reasons'},
                      {'path': 'hi/friends', 'text': 'just/reasons'}
                      ]
        }
        res = self.client.post(MINDMAPS_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        mindmaps = MindMap.objects.filter(user=self.user)
        self.assertEqual(mindmaps.count(), 1)
        mindmap = mindmaps[0]
        self.assertEqual(mindmap.leafs.count(), 2)
        for leaf in payload['leafs']:
            exists = mindmap.leafs.filter(
                path=leaf['path'],
                user=self.user,
                text=leaf['text']
            ).exists()
            self.assertTrue(exists)

    def test_create_mindmap_with_existing_leaf(self):
        """Test creating a new mindmap with an existing leaf."""
        leaf = Leaf.objects.create(
            user=self.user,
            path='bonjour/mon/ami',
            text='ca/va/bien?'
        )
        payload = {
            'title': 'Sample MindMap',
            'leafs': [
                {'path': 'salut/toi', 'text': 'oui/alo'},
                {'path': 'bonjour/mon/ami', 'text': 'ca/va/bien?'}
            ]
        }
        res = self.client.post(MINDMAPS_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        mindmaps = MindMap.objects.filter(user=self.user)
        self.assertEqual(mindmaps.count(), 1)
        mindmap = mindmaps[0]
        self.assertEqual(mindmap.leafs.count(), 2)
        self.assertIn(leaf, mindmap.leafs.all())
        for leaf in payload['leafs']:
            exists = mindmap.leafs.filter(
                user=self.user,
                path=leaf['path'],
                text=leaf['text']
            ).exists()
            self.assertTrue(exists)

    def test_create_leaf_on_update(self):
        """Test creating a leaf when updating a mindmap."""
        mindmap = create_mindmap(user=self.user)

        payload = {'leafs': [{'path': 'hire/me/pls'}]}
        url = detail_url(mindmap.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_leaf = Leaf.objects.get(user=self.user, path='hire/me/pls')
        self.assertIn(new_leaf, mindmap.leafs.all())

    def test_update_mindmap_assign_leaf(self):
        """Test assigning an existing leaf when updating a mindmap."""
        leaf1 = Leaf.objects.create(
            user=self.user,
            path='salut/toi',
            text='au/revoir'
        )
        mindmap = create_mindmap(user=self.user)
        mindmap.leafs.add(leaf1)

        leaf2 = Leaf.objects.create(
            user=self.user,
            path='bonjour/toi',
            text='beau/soleil'
        )
        payload = {'leafs': [
            {
                'path': 'bonjour/toi',
                'text': 'beau/soleil'
            }
        ]}

        url = detail_url(mindmap.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(leaf2, mindmap.leafs.all())
        self.assertNotIn(leaf1, mindmap.leafs.all())

    def test_clear_mindmap_leafs(self):
        """Test clearing leafs of a mindmap."""
        leaf = Leaf.objects.create(
            user=self.user,
            path='bonjour/toe',
            text='oui/msieu'
        )
        mindmap = create_mindmap(user=self.user)
        mindmap.leafs.add(leaf)

        payload = {'leafs': []}
        url = detail_url(mindmap.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(mindmap.leafs.count(), 0)


    # def test_get_mindmap_detail(self):
    #     """Test to get the mindmap details"""
    #     mindmap = create_mindmap(user=self.user)

    #     url = detail_url(mindmap.id)
    #     res = self.client.get(url)

    #     serializer = MindMapDetailSerializer(mindmap)
    #     self.assertEqual(res.data, serializer.data)


