"""Integration tests for AuthService (find_or_create, JWT)."""

from app.application.services.auth_service import AuthService
from app.domain.entities.user import UserRole, UserStatus
from app.infrastructure.database.models.user import UserModel
from app.infrastructure.repositories.user_repository import UserRepository

from .conftest import create_user_in_db, fake


class TestFindOrCreateUser:
    """Verify find_or_create_user interacts correctly with the database."""

    def test_create_new_user(self, db, mock_auth_settings):
        """
        When: User does not exist yet
        Then: Should persist a new user with status PENDING and role None
        """
        repo = UserRepository(db)
        service = AuthService(user_repo=repo)

        google_id = fake.bothify("google-########")
        email = fake.email()
        name = fake.name()

        user = service.find_or_create_user(
            google_id=google_id, email=email, name=name, picture=None,
        )

        assert user.google_id == google_id
        assert user.email == email
        assert user.status == UserStatus.PENDING
        assert user.role is None

        db.expire_all()
        row = db.query(UserModel).filter_by(google_id=google_id).first()
        assert row is not None
        assert row.email == email
        assert row.status == "pending"

    def test_find_existing_user(self, db, mock_auth_settings):
        """
        When: User already exists with the given google_id
        Then: Should return existing user without creating a duplicate
        """
        existing = create_user_in_db(db)

        repo = UserRepository(db)
        service = AuthService(user_repo=repo)

        user = service.find_or_create_user(
            google_id=existing.google_id,
            email=fake.email(),
            name=fake.name(),
            picture=None,
        )

        assert user.id == existing.id
        assert user.email == existing.email

        count = db.query(UserModel).filter_by(google_id=existing.google_id).count()
        assert count == 1

    def test_create_user_with_picture(self, db, mock_auth_settings):
        """
        When: User is created with a picture URL
        Then: Picture should persist correctly
        """
        repo = UserRepository(db)
        service = AuthService(user_repo=repo)

        picture_url = fake.image_url()
        user = service.find_or_create_user(
            google_id=fake.bothify("google-########"),
            email=fake.email(),
            name=fake.name(),
            picture=picture_url,
        )

        assert user.picture == picture_url


class TestJwtRoundtrip:
    """Verify JWT creation and decoding with real user data."""

    def test_create_and_decode_jwt(self, db, mock_auth_settings):
        """
        When: JWT is created for a real user
        Then: Decoded payload should contain correct user data
        """
        user = create_user_in_db(db)

        repo = UserRepository(db)
        service = AuthService(user_repo=repo)

        token = service.create_jwt(user)
        decoded = service.decode_jwt(token)

        assert decoded["sub"] == str(user.id)
        assert decoded["email"] == user.email
        assert decoded["name"] == user.name
        assert decoded["status"] == "pending"

    def test_jwt_contains_role(self, db, mock_auth_settings):
        """
        When: User has an assigned role
        Then: JWT should contain the role claim
        """
        user = create_user_in_db(db)
        admin_email = fake.email()

        user_repo = UserRepository(db)
        user_repo.approve(user.id, UserRole.ADMIN, approved_by=admin_email)

        db.expire_all()
        approved_user = user_repo.find_by_id(user.id)

        service = AuthService(user_repo=user_repo)
        token = service.create_jwt(approved_user)
        decoded = service.decode_jwt(token)

        assert decoded["role"] == "admin"
        assert decoded["status"] == "active"

    def test_jwt_contains_expiration(self, db, mock_auth_settings):
        """
        When: JWT is created
        Then: Should include exp and iat claims
        """
        user = create_user_in_db(db)

        repo = UserRepository(db)
        service = AuthService(user_repo=repo)

        token = service.create_jwt(user)
        decoded = service.decode_jwt(token)

        assert "exp" in decoded
        assert "iat" in decoded
