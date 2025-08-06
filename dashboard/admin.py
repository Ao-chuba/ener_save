from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Household, Appliance, ElectricityBill

# Register your models here.

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('email',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ()}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ()}),
    )

@admin.register(Household)
class HouseholdAdmin(admin.ModelAdmin):
    list_display = ('user', 'members', 'rooms', 'created_at')
    list_filter = ('members', 'rooms', 'created_at')
    search_fields = ('user__email', 'user__username')
    ordering = ('-created_at',)

@admin.register(Appliance)
class ApplianceAdmin(admin.ModelAdmin):
    list_display = ('appliance_type', 'custom_name', 'household', 'wattage', 'hours_used')
    list_filter = ('appliance_type', 'household')
    search_fields = ('custom_name', 'household__user__email')
    ordering = ('appliance_type',)

@admin.register(ElectricityBill)
class ElectricityBillAdmin(admin.ModelAdmin):
    list_display = ('household', 'amount', 'month', 'units_consumed')
    list_filter = ('month', 'household')
    search_fields = ('household__user__email',)
    ordering = ('-month',)
