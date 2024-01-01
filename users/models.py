from django.db import models
from django.db import models
from utils.models_utils import BaseModel
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
from django.core.validators import RegexValidator


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    # https://www.fomfus.com/articles/how-to-use-email-as-username-for-django-authentication-removing-the-username/
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""

        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        extra_fields.setdefault("phone_number", "+112345678901")
        extra_fields.setdefault("first_name", "SuperFirstName")
        extra_fields.setdefault("last_name", "SuperLastName")

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser, BaseModel):
    objects = UserManager()
    
    class UserGender(models.TextChoices):
        UNSPECIFIED = ("unspecified", "Unspecified")
        MALE = ("male", "Male")
        FEMALE = ("female", "Female")

    username = None
    email = models.EmailField("email address", unique=True)
    USERNAME_FIELD = 'email'
    USERNAME_REQUIRED = False
    REQUIRED_FIELDS = []

    # Todo: Validate this with Twilio API instead of simple Regex https://www.twilio.com/docs/glossary/what-e164
    phone_number = models.CharField(
        max_length=15,
        default="+112345678901",
        blank=True,
        validators=[
            RegexValidator(
                "^\+[1-9]\d{1,14}$",
                (
                    'Not a valid E164 format phone number. '
                ),
            ),
        ],
    )

    dob = models.DateField(null=True, blank=True, verbose_name="date of birth")
    profile_picture = models.ImageField(default='', blank= True, upload_to= 'user/profile_picture/')
    email_verified = models.BooleanField(default=False)
    gender = models.CharField(
        max_length=50,
        choices=UserGender.choices,
        null=True,
        blank=True,
        default="unspecified",
        verbose_name="gender",
    )

    def __str__(self):
        return f"user-{self.email}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self):
        age = (
            round(((timezone.localdate() - self.dob).days / 365)) if self.dob else None
        )
        return age
