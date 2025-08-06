from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from .forms import HouseholdForm, ApplianceForm, BillForm
from .models import Household, Appliance, ElectricityBill
from .utils import calculate_consumption
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model
# views.py
from .forms import EmailUserCreationForm, EmailAuthenticationForm

import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .gemini_api import GeminiAPI

from .utils import calculate_consumption, expected_bill_for_indian_household
# Add this to your views.py file

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .models import Appliance
 # Import from utils
@require_POST
def delete_appliance(request, pk):
    """
    Delete an appliance via AJAX request
    """
    try:
        # Get the appliance, ensuring it belongs to the current user's household
        appliance = get_object_or_404(
            Appliance, 
            id=pk, 
            household__user=request.user
        )
        
        # Delete the appliance
        appliance.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Appliance deleted successfully'
        })
        
    except Appliance.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Appliance not found or you do not have permission to delete it'
        }, status=404)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
    
def register_view(request):
    if request.method == 'POST':
        form = EmailUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('household')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = EmailUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = EmailAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')  # 'username' is actually email
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('household')
        messages.error(request, "Invalid email or password.")
    else:
        form = EmailAuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')

@login_required
def data_entry_household(request):
    existing = Household.objects.filter(user=request.user).first()
    
    if existing and not request.GET.get('edit'):  # Add ?edit=true to URL to edit
        messages.info(request, "Your household info is already set")
        return redirect('appliances')
        
    if request.method == 'POST':
        form = HouseholdForm(request.POST, instance=existing)
        if form.is_valid():
            household = form.save(commit=False)
            household.user = request.user
            household.save()
            messages.success(request, "Household information saved!")
            return redirect('appliances')
    else:
        form = HouseholdForm(instance=existing)
    
    return render(request, 'data_entry/household.html', {
        'form': form,
        'editing': existing is not None
    })

@login_required
def data_entry_appliances(request):
    household = Household.objects.filter(user=request.user).first()
    if not household:
        messages.warning(request, "Please enter your household information first.")
        return redirect('household')
    
    if request.method == 'POST':
        form = ApplianceForm(request.POST)
        if form.is_valid():
            appliance = form.save(commit=False)
            appliance.household = household
            appliance.save()
            
            # Fix: Use get_appliance_type_display or custom_name instead of name
            appliance_name = appliance.custom_name if appliance.custom_name else appliance.get_appliance_type_display()
            messages.success(request, f"{appliance_name} added successfully!")
            
            # Reset the form after submission to allow adding more appliances
            form = ApplianceForm()
        else:
            # Debug form errors
            print(f"Form errors: {form.errors}")
            messages.error(request, f"Form has errors: {form.errors}")
    else:
        form = ApplianceForm()
    
    # Get all appliances for this household
    appliances = Appliance.objects.filter(household=household)
    return render(request, 'data_entry/appliances.html', {
        'form': form,
        'appliances': appliances
    })

@login_required
def data_entry_bill(request):
    household = Household.objects.filter(user=request.user).first()
    if not household:
        messages.warning(request, "Please enter your household information first.")
        return redirect('household')
    
    appliances = Appliance.objects.filter(household=household)
    if not appliances:
        messages.warning(request, "Please add some appliances to your household.")
        return redirect('appliances')
    
    if request.method == 'POST':
        form = BillForm(request.POST)
        if form.is_valid():
            bill = form.save(commit=False)
            bill.household = household
            
            # Calculate units consumed based on bill amount if not provided
            if not bill.units_consumed:
                # Assuming a standard rate of Rs. 11 per unit
                avg_rate_per_unit = 11.0
                bill.units_consumed = float(bill.amount) / avg_rate_per_unit
            
            bill.save()
            
            # Add debug message to check if this part executes
            messages.success(request, "Bill information saved successfully!")
            print("Bill saved and redirecting to results...")
            
            # Force redirect to results page
            return redirect('results')
        else:
            # Display form errors in a more user-friendly way
            print(f"Form errors: {form.errors}")
            error_messages = []
            for field, errors in form.errors.items():
                field_name = form[field].label or field
                for error in errors:
                    error_messages.append(f"{field_name}: {error}")
            
            error_text = "<br>".join(error_messages)
            messages.error(request, f"Form has errors: {error_text}")
    else:
        form = BillForm()
    
    return render(request, 'data_entry/bill.html', {'form': form})

@login_required
def results(request):
    household = Household.objects.filter(user=request.user).first()
    if not household:
        messages.warning(request, "Please enter your household information first.")
        return redirect('household')
    
    bill = ElectricityBill.objects.filter(household=household).order_by('-month').first()
    if not bill:
        messages.warning(request, "Please enter your bill information first.")
        return redirect('bill')
        
    appliances = Appliance.objects.filter(household=household)
    if not appliances:
        messages.warning(request, "Please add some appliances to your household.")
        return redirect('appliances')
    
    # Debug prints
    print(f"Household: {household.id}, Members: {household.members}, Rooms: {household.rooms}")
    print(f"Bill: {bill.id}, Amount: {bill.amount}, Units: {bill.units_consumed}")
    print(f"Appliances count: {appliances.count()}")
    
    # Calculate consumption and rating
    consumption_data = calculate_consumption(household, appliances, bill)
    
    # Debug print consumption data
    print(f"Consumption data: {consumption_data}")
     # Calculate progress percentage safely

    try:
        total = float(consumption_data['total_kwh'])
        high = float(consumption_data['high_threshold'])
        if high > 0:
            progress = min((total / high) * 100, 100)
        else:
            progress = 0
    except (KeyError, ValueError, ZeroDivisionError):
        progress = 0

    # Add to context
    consumption_data['progress_percentage'] = round(progress, 1)
    expected = expected_bill_for_indian_household(household.members, household.rooms)

    return render(request, 'results.html', {
        'household': household,
        'bill': bill,
        'consumption_data': consumption_data,
        'expected':expected
    })
# Add the tips view function here
@login_required
def tips(request):
    """
    View function to display the energy-saving tips page with chat interface.
    If the user has entered household data, it will be passed to the template
    for more personalized tips.
    """
    # Get the user's household data if available
    household = Household.objects.filter(user=request.user).first()
    appliances = []
    
    if household:
        appliances = Appliance.objects.filter(household=household)
    
    context = {
        'household': household,
        'appliances': appliances
    }
    
    return render(request, 'tips.html', context)

@csrf_exempt
def gemini_chat(request):
    print(f"=== GEMINI CHAT VIEW CALLED ===")
    print(f"Method: {request.method}")
    print(f"Content-Type: {request.content_type}")
    print(f"Headers: {dict(request.headers)}")
    
    if request.method == 'POST':
        try:
            print(f"Request body: {request.body}")
            
            # Parse JSON data
            data = json.loads(request.body)
            user_message = data.get('message', '')
            household_data = data.get('household_data', {})
            
            print(f"Parsed message: {user_message}")
            print(f"Parsed household_data: {household_data}")
            
            if not user_message:
                print("No message provided")
                return JsonResponse({'error': 'No message provided'}, status=400)
            
            # Get response from Gemini API
            print("Calling GeminiAPI.generate_response...")
            response = GeminiAPI.generate_response(user_message, household_data)
            print(f"Got response: {response}")
            
            return JsonResponse({'response': response})
            
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {str(e)}")
            return JsonResponse({'error': f'Invalid JSON: {str(e)}'}, status=400)
        except Exception as e:
            print(f"General error: {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)
    
    print("Method not POST")
    return JsonResponse({'error': 'Method not allowed'}, status=405)