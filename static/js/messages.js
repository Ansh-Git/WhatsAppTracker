document.addEventListener('DOMContentLoaded', function() {
    // Handle reply button clicks
    const replyButtons = document.querySelectorAll('.reply-btn');
    const replyModal = new bootstrap.Modal(document.getElementById('replyModal'));
    
    replyButtons.forEach(button => {
        button.addEventListener('click', function() {
            const phoneNumber = this.getAttribute('data-phone');
            document.getElementById('recipient-phone').value = phoneNumber;
            replyModal.show();
        });
    });
    
    // Handle send reply button
    document.getElementById('send-reply-btn').addEventListener('click', function() {
        const phone = document.getElementById('recipient-phone').value;
        const message = document.getElementById('reply-message').value.trim();
        
        if (!message) {
            alert('Please enter a message');
            return;
        }
        
        // Show loading state
        const button = this;
        const originalHtml = button.innerHTML;
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> Sending...';
        
        // Send API request
        fetch('/api/send_message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                phone: phone,
                message: message
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to send message');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // Clear message input and close modal
                document.getElementById('reply-message').value = '';
                replyModal.hide();
                
                // Optionally, show a success message or reload page to show the sent message
                alert('Message sent successfully!');
                window.location.reload();
            } else {
                alert('Error: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error sending message: ' + error.message);
        })
        .finally(() => {
            // Reset button state
            button.disabled = false;
            button.innerHTML = originalHtml;
        });
    });
    
    // Handle search functionality
    document.getElementById('search-button').addEventListener('click', function() {
        const searchQuery = document.getElementById('search-input').value.trim().toLowerCase();
        const filterValue = document.getElementById('filter-select').value;
        
        const rows = document.querySelectorAll('.message-row');
        rows.forEach(row => {
            const content = row.children[1].textContent.toLowerCase();
            const contact = row.children[0].textContent.toLowerCase();
            const direction = row.classList.contains('table-success') ? 'incoming' : 'outgoing';
            
            const matchesSearch = searchQuery === '' || 
                                  content.includes(searchQuery) ||
                                  contact.includes(searchQuery);
                                  
            const matchesFilter = filterValue === 'all' || 
                                  (filterValue === 'incoming' && direction === 'incoming') ||
                                  (filterValue === 'outgoing' && direction === 'outgoing');
                                  
            row.style.display = matchesSearch && matchesFilter ? '' : 'none';
        });
    });
    
    // Filter select change handler
    document.getElementById('filter-select').addEventListener('change', function() {
        document.getElementById('search-button').click();
    });
    
    // Search input keyup handler for immediate filtering
    document.getElementById('search-input').addEventListener('keyup', function(e) {
        if (e.key === 'Enter') {
            document.getElementById('search-button').click();
        }
    });
});
