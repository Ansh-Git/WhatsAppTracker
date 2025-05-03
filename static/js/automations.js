document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const newAutomationBtn = document.getElementById('new-automation-btn');
    const saveAutomationBtn = document.getElementById('save-automation-btn');
    const automationModal = new bootstrap.Modal(document.getElementById('automationModal'));
    const deleteConfirmModal = new bootstrap.Modal(document.getElementById('deleteConfirmModal'));
    const form = document.getElementById('automationForm');
    let currentAutomationId = null;
    let automationToDelete = null;
    
    // Set up trigger type change handler
    document.getElementById('trigger-type').addEventListener('change', function() {
        const triggerType = this.value;
        const triggerValueContainer = document.getElementById('trigger-value-container');
        const triggerValueInput = document.getElementById('trigger-value');
        
        if (triggerType === 'keyword') {
            triggerValueContainer.style.display = 'block';
            triggerValueInput.placeholder = 'Enter keywords separated by commas';
            document.querySelector('label[for="trigger-value"]').textContent = 'Trigger Keywords';
            document.querySelector('#trigger-value-container .form-text').textContent = 
                'When a message contains any of these keywords, the automation will be triggered.';
        } else if (triggerType === 'new_contact') {
            triggerValueContainer.style.display = 'none';
            triggerValueInput.value = 'new_contact';
        }
    });
    
    // Create new automation
    newAutomationBtn.addEventListener('click', function() {
        resetForm();
        document.getElementById('automationModalLabel').textContent = 'New Automation';
        currentAutomationId = null;
        automationModal.show();
    });
    
    // Save automation
    saveAutomationBtn.addEventListener('click', function() {
        // Validate form
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }
        
        // Get form values
        const name = document.getElementById('automation-name').value;
        const triggerType = document.getElementById('trigger-type').value;
        const triggerValue = document.getElementById('trigger-value').value;
        const responseText = document.getElementById('response-text').value;
        const isActive = document.getElementById('is-active').checked;
        
        // Prepare data
        const data = {
            name: name,
            trigger_type: triggerType,
            trigger_value: triggerValue,
            response_text: responseText,
            is_active: isActive
        };
        
        // Add id if editing existing automation
        if (currentAutomationId) {
            data.id = currentAutomationId;
        }
        
        // Show loading state
        const button = this;
        const originalHtml = button.innerHTML;
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> Saving...';
        
        // Send API request
        fetch('/api/automations', {
            method: currentAutomationId ? 'PUT' : 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to save automation');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                automationModal.hide();
                window.location.reload(); // Reload to show new/updated automation
            } else {
                alert('Error: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error saving automation: ' + error.message);
        })
        .finally(() => {
            // Reset button state
            button.disabled = false;
            button.innerHTML = originalHtml;
        });
    });
    
    // Edit automation buttons
    document.querySelectorAll('.edit-automation-btn').forEach(button => {
        button.addEventListener('click', function() {
            const automationId = this.getAttribute('data-automation-id');
            
            // Get automation data from the table row
            const row = document.querySelector(`tr[data-automation-id="${automationId}"]`);
            const name = row.children[0].textContent;
            const triggerType = row.children[1].textContent;
            const triggerValue = row.children[2].textContent;
            const responseTextPreview = row.children[3].textContent;
            const isActive = row.querySelector('.automation-status-toggle').checked;
            
            // Set form values
            document.getElementById('automation-id').value = automationId;
            document.getElementById('automation-name').value = name;
            document.getElementById('trigger-type').value = triggerType;
            document.getElementById('trigger-value').value = triggerValue;
            document.getElementById('is-active').checked = isActive;
            
            // For the response text, we need to fetch the full content from the server
            fetch(`/api/automations?id=${automationId}`)
                .then(response => response.json())
                .then(data => {
                    const automation = data.find(a => a.id == automationId);
                    if (automation) {
                        document.getElementById('response-text').value = automation.response_text;
                    }
                })
                .catch(error => {
                    console.error('Error fetching automation:', error);
                    // Use preview text as fallback
                    const previewText = responseTextPreview.endsWith('...') ? 
                                       responseTextPreview.slice(0, -3) : 
                                       responseTextPreview;
                    document.getElementById('response-text').value = previewText;
                });
            
            // Update form for editing
            document.getElementById('automationModalLabel').textContent = 'Edit Automation';
            currentAutomationId = automationId;
            
            // Show/hide trigger value based on trigger type
            document.getElementById('trigger-type').dispatchEvent(new Event('change'));
            
            automationModal.show();
        });
    });
    
    // Delete automation buttons
    document.querySelectorAll('.delete-automation-btn').forEach(button => {
        button.addEventListener('click', function() {
            automationToDelete = this.getAttribute('data-automation-id');
            deleteConfirmModal.show();
        });
    });
    
    // Confirm delete button
    document.getElementById('confirm-delete-btn').addEventListener('click', function() {
        if (!automationToDelete) return;
        
        const button = this;
        const originalHtml = button.innerHTML;
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> Deleting...';
        
        fetch(`/api/automations?id=${automationToDelete}`, {
            method: 'DELETE'
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to delete automation');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // Remove row from table
                const row = document.querySelector(`tr[data-automation-id="${automationToDelete}"]`);
                if (row) row.remove();
                
                // Check if table is now empty
                const tbody = document.querySelector('#automations-table tbody');
                if (tbody.children.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="7" class="text-center">No automations found. Create your first one!</td></tr>';
                }
                
                deleteConfirmModal.hide();
            } else {
                alert('Error: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error deleting automation: ' + error.message);
        })
        .finally(() => {
            button.disabled = false;
            button.innerHTML = originalHtml;
            automationToDelete = null;
        });
    });
    
    // Toggle automation status
    document.querySelectorAll('.automation-status-toggle').forEach(toggle => {
        toggle.addEventListener('change', function() {
            const automationId = this.getAttribute('data-automation-id');
            const isActive = this.checked;
            
            fetch('/api/automations', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    id: automationId,
                    is_active: isActive
                })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to update automation status');
                }
                return response.json();
            })
            .then(data => {
                if (!data.success) {
                    // Revert toggle if update failed
                    this.checked = !isActive;
                    alert('Error: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                // Revert toggle if update failed
                this.checked = !isActive;
                alert('Error updating automation status: ' + error.message);
            });
        });
    });
    
    // Helper function to reset the form
    function resetForm() {
        form.reset();
        document.getElementById('automation-id').value = '';
        document.getElementById('trigger-type').value = 'keyword';
        document.getElementById('trigger-type').dispatchEvent(new Event('change'));
    }
});
