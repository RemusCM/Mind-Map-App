"""
Tests for models.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


class ModelTests(TestCase):
    """Test models."""

    def test_create_user_with_email_successful(self):
        """Test that creating a user with an email is successful"""
        email = 'test@example.com'
        password = 'testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users."""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without an email raises a ValueError."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123')

    def test_create_superuser(self):
        """Test creating a superuser."""
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'test123',
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_mindmap(self):
        """Test that Creating a Mind Map is successful."""
        user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123',
        )

        mindmap = models.MindMap.objects.create(
            user=user,
            title='Sample MindMap Name',
            # I'm guessing I'll need to add leafs here in the future?
        )

        self.assertEqual(str(mindmap), mindmap.title)

    def test_create_leaf(self):
        """Test creation of leaf is successful"""
        user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123',
        )
        leaf = models.Leaf.objects.create(
            user=user,
            path='i/like/turtles',
            text='because/turtles'
        )

        self.assertEqual(str(leaf), leaf.path)
