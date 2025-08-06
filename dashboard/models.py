# Check and fix the models if necessary
from django.db import models
from django.contrib.auth.models import AbstractUser,BaseUserManager
from django.utils.translation import gettext_lazy as _

class UserManager(BaseUserManager):
    """Custom user manager where email is the unique identifier"""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user with an email and password."""
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser with an email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    username = models.CharField(max_length=150, blank=True)  # Make username optional
    
    USERNAME_FIELD = 'email'  # Use email as the login identifier
    REQUIRED_FIELDS = []      # Remove email from REQUIRED_FIELDS

    objects=UserManager()  #Use the custom manager

    def __str__(self):
        return self.email
    
class Household(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    members = models.PositiveIntegerField()
    rooms = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.email}'s household"

class Appliance(models.Model):
    HOUSEHOLD_APPLIANCES = [
        ('AC', 'Air Conditioner'),
        ('WM', 'Washing Machine'),
        ('FR', 'Refrigerator'),
        ('WH', 'Water Heater'),
        ('TV', 'Television'),
        ('MO', 'Microwave Oven'),
        ('CF', 'Ceiling Fan'),
        ('LT', 'Lights'),
        ('PC', 'Computer/Laptop'),
    ]
    
    household = models.ForeignKey(Household, on_delete=models.CASCADE)
    appliance_type = models.CharField(max_length=2, choices=HOUSEHOLD_APPLIANCES)
    wattage = models.PositiveIntegerField()
    hours_used = models.PositiveIntegerField()
    custom_name = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        display_name = self.custom_name if self.custom_name else self.get_appliance_type_display()
        return f"{display_name} - {self.household.user.email}"

class ElectricityBill(models.Model):
    household = models.ForeignKey(Household, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    month = models.DateField()
    units_consumed = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    def __str__(self):
        return f"Bill for {self.household.user.email} - {self.month.strftime('%B %Y')}"