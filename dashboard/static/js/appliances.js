document.addEventListener('DOMContentLoaded', function() {
    // Handle appliance form submission via AJAX
    const applianceForm = document.getElementById('appliance-form');
    if (applianceForm) {
        applianceForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            fetch('{% url "appliances" %}', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Clear the form
                    this.reset();
                    
                    // Update the appliances list
                    const appliancesList = document.getElementById('appliances-list');
                    if (appliancesList.querySelector('.alert')) {
                        appliancesList.innerHTML = '';
                    }
                    
                    // Add new appliance to the list
                    const newAppliance = document.createElement('div');
                    newAppliance.className = 'list-group-item d-flex justify-content-between align-items-center';
                    newAppliance.innerHTML = `
                        <div>
                            <strong>${data.appliance_type_display}</strong>
                            <span class="text-muted ms-2">${data.wattage}W, ${data.hours_used} hrs/day</span>
                        </div>
                        <button class="btn btn-sm btn-outline-danger remove-appliance" data-id="${data.id}">Remove</button>
                    `;
                    appliancesList.appendChild(newAppliance);
                    
                    // Add event listener to the new remove button
                    newAppliance.querySelector('.remove-appliance').addEventListener('click', function() {
                        removeAppliance(this);
                    });
                }
            });
        });
    }
    
    // Function to handle appliance removal
    function removeAppliance(button) {
        const applianceId = button.getAttribute('data-id');
        fetch(`/appliance/${applianceId}/delete/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': '{{ csrf_token }}',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                button.closest('.list-group-item').remove();
                const appliancesList = document.getElementById('appliances-list');
                if (appliancesList.children.length === 0) {
                    appliancesList.innerHTML = 
                        '<div class="alert alert-info">No appliances added yet. Add an appliance above.</div>';
                }
            }
        });
    }
    
    // Add event listeners to all remove buttons
    document.querySelectorAll('.remove-appliance').forEach(btn => {
        btn.addEventListener('click', function() {
            removeAppliance(this);
        });
    });
});