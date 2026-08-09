from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase


class OidcSubjectMigrationTests(TransactionTestCase):
    migrate_from = [("accounts", "0002_migrate_user_module_authorizations")]
    migrate_to = [("accounts", "0003_userprofile_oidc_subject_and_auth_revoked_at")]

    def setUp(self):
        super().setUp()
        self.executor = MigrationExecutor(connection)

    def tearDown(self):
        MigrationExecutor(connection).migrate(self.migrate_to)
        super().tearDown()

    def test_existing_profiles_receive_unique_oidc_subjects(self):
        self.executor.migrate(self.migrate_from)
        old_apps = self.executor.loader.project_state(self.migrate_from).apps

        User = old_apps.get_model("auth", "User")
        UserProfile = old_apps.get_model("accounts", "UserProfile")

        legacy_user_1 = User.objects.create_user(username="legacy-user-1", password="pass123456")
        legacy_user_2 = User.objects.create_user(username="legacy-user-2", password="pass123456")
        UserProfile.objects.create(user=legacy_user_1, display_name="旧用户一")
        UserProfile.objects.create(user=legacy_user_2, display_name="旧用户二")

        self.executor = MigrationExecutor(connection)
        self.executor.migrate(self.migrate_to)
        new_apps = self.executor.loader.project_state(self.migrate_to).apps
        MigratedUserProfile = new_apps.get_model("accounts", "UserProfile")

        subjects = list(
            MigratedUserProfile.objects.order_by("user_id").values_list("oidc_subject", flat=True)
        )

        self.assertEqual(len(subjects), 2)
        self.assertTrue(all(subjects))
        self.assertEqual(len(set(subjects)), 2)
