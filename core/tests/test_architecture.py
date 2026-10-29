from django.test import TestCase, override_settings
from django.conf import settings
from unittest.mock import MagicMock

from core.database.context import (
    get_current_database,
    set_current_database,
    reset_current_database,
    tenant_context,
)
from core.database.routers import TenantRouter
from core.security import encrypt_secret, decrypt_secret
from core.permissions import IsTenantUser
from apps.testapp.models import Product
from core.tenancy.models import Tenant
from core.authentication.models import CustomUser


class SecurityEncryptionTestCase(TestCase):
    def test_encryption_and_decryption_with_key(self):
        sample_key = "a" * 43 + "="
        from cryptography.fernet import Fernet

        key = Fernet.generate_key().decode()
        with override_settings(TENANT_DB_ENCRYPTION_KEY=key):
            raw_password = "SuperSecretPassword123!"
            encrypted = encrypt_secret(raw_password)
            self.assertNotEqual(encrypted, raw_password)

            decrypted = decrypt_secret(encrypted)
            self.assertEqual(decrypted, raw_password)

    def test_decryption_fallback_on_unencrypted_text(self):
        # Existing database entries before encryption must not crash
        with override_settings(TENANT_DB_ENCRYPTION_KEY="invalid-or-present-key"):
            raw_password = "legacy_plain_password"
            decrypted = decrypt_secret(raw_password)
            self.assertEqual(decrypted, raw_password)


class DatabaseRouterTestCase(TestCase):
    def setUp(self):
        self.router = TenantRouter()

    def test_default_app_routes_to_default(self):
        self.assertEqual(self.router.db_for_read(Tenant), "default")
        self.assertEqual(self.router.db_for_write(Tenant), "default")
        self.assertEqual(self.router.db_for_read(CustomUser), "default")

    def test_tenant_app_raises_when_context_missing(self):
        set_current_database(None)
        with self.assertRaises(RuntimeError):
            self.router.db_for_read(Product)

    def test_tenant_app_routes_to_active_context(self):
        token = set_current_database("tenant_acme")
        try:
            self.assertEqual(self.router.db_for_read(Product), "tenant_acme")
            self.assertEqual(self.router.db_for_write(Product), "tenant_acme")
        finally:
            reset_current_database(token)

    def test_allow_migrate_rules(self):
        self.assertTrue(self.router.allow_migrate("default", "tenancy"))
        self.assertFalse(self.router.allow_migrate("tenant_acme", "tenancy"))

        self.assertTrue(self.router.allow_migrate("tenant_acme", "testapp"))
        self.assertFalse(self.router.allow_migrate("default", "testapp"))


class TenantContextManagerTestCase(TestCase):
    def test_context_restores_on_normal_exit(self):
        initial = get_current_database()
        token = set_current_database("default")
        with tenant_context("default"):
            self.assertEqual(get_current_database(), "default")
        self.assertEqual(get_current_database(), "default")
        reset_current_database(token)

    def test_context_restores_on_exception(self):
        token = set_current_database("default")
        try:
            with self.assertRaises(ValueError):
                with tenant_context("default"):
                    raise ValueError("Simulated view error")
            self.assertEqual(get_current_database(), "default")
        finally:
            reset_current_database(token)


class TenantPermissionTestCase(TestCase):
    def setUp(self):
        self.permission = IsTenantUser()

    def test_unauthenticated_request_rejected(self):
        request = MagicMock()
        request.user = None
        self.assertFalse(self.permission.has_permission(request, None))

        request.user = MagicMock()
        request.user.is_authenticated = False
        self.assertFalse(self.permission.has_permission(request, None))

    def test_user_without_tenant_rejected(self):
        request = MagicMock()
        request.user.is_authenticated = True
        request.user.is_superuser = False
        request.user.tenant = None
        self.assertFalse(self.permission.has_permission(request, None))

    def test_inactive_tenant_rejected(self):
        request = MagicMock()
        request.user.is_authenticated = True
        request.user.is_superuser = False
        request.user.tenant.is_active = False
        self.assertFalse(self.permission.has_permission(request, None))

    def test_matching_active_tenant_accepted(self):
        request = MagicMock()
        request.user.is_authenticated = True
        request.user.is_superuser = False
        request.user.tenant.is_active = True
        request.user.tenant.db_alias = "tenant_valid"

        token = set_current_database("tenant_valid")
        try:
            self.assertTrue(self.permission.has_permission(request, None))
        finally:
            reset_current_database(token)

    def test_cross_tenant_mismatch_rejected(self):
        request = MagicMock()
        request.user.is_authenticated = True
        request.user.is_superuser = False
        request.user.tenant.is_active = True
        request.user.tenant.db_alias = "tenant_valid"

        token = set_current_database("tenant_attacker")
        try:
            self.assertFalse(self.permission.has_permission(request, None))
        finally:
            reset_current_database(token)
