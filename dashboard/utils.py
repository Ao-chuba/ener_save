from decimal import Decimal
from calendar import monthrange

def calculate_consumption(household, appliances, bill):
    # Constants
    avg_tariff = 11# Average electricity rate per kWh
    real_world_usage_factor = 0.4  # Factor to account for real-world usage patterns
    
    # Step 1: Calculate appliance-based consumption with real-world factor
    daily_wh = sum(app.wattage * app.hours_used for app in appliances)
    daily_kwh = daily_wh / 1000
    days_in_month = monthrange(bill.month.year, bill.month.month)[1] if bill and bill.month else 30
    appliance_based_kwh = daily_kwh * days_in_month * real_world_usage_factor

    # Step 2: Calculate bill-based consumption
    bill_based_kwh = None
    if bill and bill.units_consumed:
        bill_based_kwh = float(bill.units_consumed)
    elif bill and bill.amount:
        bill_based_kwh = float(bill.amount) / avg_tariff

    # Step 3: Determine primary consumption display
    if bill and bill.units_consumed:
        actual_kwh = float(bill.units_consumed)
        consumption_source = "Bill Units"
    elif bill and bill.amount:
        actual_kwh = float(bill.amount) / avg_tariff
        consumption_source = "Bill Amount Estimation"
    elif appliances:
        actual_kwh = appliance_based_kwh
        consumption_source = "Appliance Calculation"
    else:
        actual_kwh = 0
        consumption_source = "No Data"

    # Step 4: Per person usage
    members = household.members if household.members > 0 else 1
    per_person = actual_kwh / members

    # Step 5: Benchmark-based rating system
    avg_indian_consumption = 330
    low_threshold = avg_indian_consumption * 0.8
    high_threshold = avg_indian_consumption * 1.2

    if actual_kwh < low_threshold:
        rating = 'Good'
        color = 'success'
    elif actual_kwh <= high_threshold:
        rating = 'Average'
        color = 'warning'
    else:
        rating = 'High'
        color = 'danger'

    # Step 6: Appliance-level breakdown with real-world factor and normalized percentages
    appliance_data = []
    if appliances:
        total_monthly_kwh = 0
        temp_appliance_data = []
        
        # Calculate raw values with real-world factor
        for app in appliances:
            monthly_kwh = (app.wattage * app.hours_used * days_in_month) / 1000 * real_world_usage_factor
            total_monthly_kwh += monthly_kwh
            
            appliance_name = app.custom_name if app.custom_name else app.get_appliance_type_display()
            temp_appliance_data.append({
                'name': appliance_name,
                'monthly_kwh': monthly_kwh
            })

        # Calculate normalized percentages
        if total_monthly_kwh > 0:
            for app in temp_appliance_data:
                percentage = (app['monthly_kwh'] / total_monthly_kwh) * 100
                appliance_data.append({
                    'name': app['name'],
                    'kwh': round(app['monthly_kwh'], 1),
                    'percentage': round(percentage, 1)
                })

    # Step 7: Return all metrics
    return {
        'total_kwh': round(actual_kwh, 1),
        'per_person': round(per_person, 1),
        'rating': rating,
        'color': color,
        'appliance_data': appliance_data,
        'appliance_based_kwh': round(appliance_based_kwh, 1),
        'bill_based_kwh': round(bill_based_kwh, 1) if bill_based_kwh else None,
        'consumption_source': consumption_source,
        'avg_consumption': avg_indian_consumption,
        'low_threshold': round(low_threshold, 1),
        'high_threshold': round(high_threshold, 1),
        'usage_percentage': min(100, max(0, (actual_kwh / high_threshold) * 100)) if high_threshold > 0 else 0
    }

def expected_bill_for_indian_household(members, rooms, avg_rate_per_unit=7.5):
    """
    Estimate expected monthly electricity usage and bill based on household size and rooms.
    """
    if members <= 2 and rooms <= 2:
        expected_kwh = 100
    elif members <= 4 and rooms <= 3:
        expected_kwh = 230
    elif members <= 6 and rooms <= 4:
        expected_kwh = 335
    else:
        expected_kwh = 390

    expected_bill = expected_kwh * avg_rate_per_unit

    return {
        'expected_kwh': expected_kwh,
        'expected_bill': round(expected_bill, 2)
    }