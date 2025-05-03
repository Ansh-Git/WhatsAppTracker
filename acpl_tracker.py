import logging
import requests
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)

def track_acpl_cargo(tracking_number):
    """
    Track ACPL cargo using the tracking number.
    
    Args:
        tracking_number (str): The tracking number to look up
        
    Returns:
        dict: A dictionary containing the tracking information or error message
    """
    url = "https://acplcargo.com/GCTRACKING.php"
    
    try:
        # First, make a POST request to submit the tracking number
        payload = {
            'tracking': tracking_number,
            'submit': 'Submit'
        }
        
        logger.info(f"Sending tracking request for number: {tracking_number}")
        session = requests.Session()
        response = session.post(url, data=payload)
        response.raise_for_status()
        
        # Check if we have tracking results
        if "No Tracking Information available" in response.text:
            return {
                "success": False,
                "message": f"No tracking information found for number {tracking_number}"
            }
            
        # Parse the HTML response
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the tracking information table (ACPL specific structure)
        tracking_info = {}
        
        # ACPL typically shows tracking info in a table with specific structure
        # Look for the specific container that holds tracking information
        content_container = soup.find('div', {'class': 'grid_9'})
        if content_container:
            logger.info("Found main content container")
            
            # Get tracking number from the page
            tracking_info["GC Number"] = tracking_number
            
            # Look for the status information which is typically in strong tags
            status_tags = content_container.find_all('strong')
            if status_tags:
                for tag in status_tags:
                    text = tag.get_text(strip=True)
                    if ":" in text:
                        parts = text.split(":", 1)
                        key = parts[0].strip()
                        value = parts[1].strip()
                        tracking_info[key] = value
                    elif len(text) > 0:
                        # This might be a status message
                        tracking_info["Status"] = text
        
        # Try to extract tracking information from all tables on the page
        tables = soup.find_all('table')
        if tables:
            logger.info(f"Found {len(tables)} tables to analyze")
            # Process each table
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['th', 'td'])
                    if len(cells) >= 2:
                        key = cells[0].get_text(strip=True)
                        value = cells[1].get_text(strip=True)
                        if key and value:
                            # Clean up the key to make it more readable
                            key = re.sub(r'[^a-zA-Z0-9\s]', '', key).strip()
                            tracking_info[key] = value
        
        # Extract from specific ACPL format using direct CSS selectors
        # Try to find labels and their values
        labels = soup.select('label.control-label')
        for label in labels:
            key = label.get_text(strip=True).rstrip(':')
            # Look for the next element which might contain the value
            value_elem = label.find_next(['span', 'div', 'p', 'input'])
            if value_elem:
                # Try to get value from input
                if value_elem.name == 'input':
                    value = value_elem.get('value', '')
                else:
                    value = value_elem.get_text(strip=True)
                
                if key and value:
                    tracking_info[key] = value
        
        # If we still don't have enough information, try a more aggressive approach
        if len(tracking_info) <= 1:  # Only has GC Number
            # Extract all text and try to find patterns
            all_text = soup.get_text(separator='\n', strip=True)
            lines = all_text.split('\n')
            
            for line in lines:
                line = line.strip()
                if ':' in line:
                    parts = line.split(':', 1)
                    key = parts[0].strip()
                    value = parts[1].strip()
                    if key and value and len(key) < 50:  # Reasonable key length
                        tracking_info[key] = value
                        
            # Look for specific ACPL patterns
            status_pattern = re.search(r'Status\s*[:]\s*([^\n]+)', all_text, re.IGNORECASE)
            if status_pattern and "Status" not in tracking_info:
                tracking_info["Status"] = status_pattern.group(1).strip()
                
            date_pattern = re.search(r'(Date|Delivery)\s*[:]\s*([^\n]+)', all_text, re.IGNORECASE)
            if date_pattern and "Delivery Date" not in tracking_info:
                tracking_info["Delivery Date"] = date_pattern.group(2).strip()
        
        # If we still don't have any tracking data, return the raw HTML for diagnosis
        if len(tracking_info) <= 1:
            logger.warning("Could not extract structured tracking information, returning raw HTML for manual inspection")
            return {
                "success": True,
                "message": "Raw tracking response retrieved",
                "raw_html": response.text
            }
        
        # Return the tracking information we found
        logger.info(f"Successfully extracted {len(tracking_info)} tracking data fields")
        return {
            "success": True,
            "message": "Tracking information retrieved",
            "tracking_data": tracking_info
        }
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error tracking ACPL cargo: {str(e)}")
        return {
            "success": False,
            "message": f"Error connecting to ACPL tracking: {str(e)}"
        }
    except Exception as e:
        logger.error(f"Unexpected error tracking ACPL cargo: {str(e)}")
        return {
            "success": False,
            "message": f"Unexpected error: {str(e)}"
        }

def format_tracking_result(result):
    """
    Format the tracking result into a readable message for WhatsApp.
    
    Args:
        result (dict): The tracking result from track_acpl_cargo
        
    Returns:
        str: A formatted message to send via WhatsApp
    """
    if not result.get("success", False):
        return f"❌ *Tracking Error*: {result.get('message', 'Unknown error')}"
    
    if "tracking_data" in result and result["tracking_data"]:
        # Format structured data
        message = "📦 *ACPL Cargo Tracking Information*\n\n"
        
        # Define important fields to show first (if present)
        priority_fields = [
            "GC Number", "GCNumber", "tracking", "Tracking", "gc_ref", "Status", "status", 
            "Current Status", "Delivery Date", "delivery_date", "Current Location", 
            "Origin", "Destination", "Sent Date", "sender", "receiver"
        ]
        
        # First show priority fields in order
        for field in priority_fields:
            for key in result["tracking_data"]:
                if key.lower() == field.lower() or key.replace(" ", "").lower() == field.replace(" ", "").lower():
                    value = result["tracking_data"][key]
                    message += f"*{key}*: {value}\n"
        
        # Then show remaining fields
        for key, value in result["tracking_data"].items():
            if not any(key.lower() == field.lower() or key.replace(" ", "").lower() == field.replace(" ", "").lower() for field in priority_fields):
                message += f"*{key}*: {value}\n"
        
        return message
    
    elif "raw_text" in result and result["raw_text"]:
        # Format raw text data
        text = result["raw_text"]
        
        # Try to clean up the raw text output and organize it better
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line:
                # Try to detect and format key-value pairs
                if ':' in line:
                    parts = line.split(':', 1)
                    if len(parts) == 2 and parts[0].strip() and parts[1].strip():
                        key = parts[0].strip()
                        value = parts[1].strip()
                        cleaned_lines.append(f"*{key}*: {value}")
                    else:
                        cleaned_lines.append(line)
                else:
                    cleaned_lines.append(line)
        
        message = "📦 *ACPL Cargo Tracking Information*\n\n"
        
        # Join the lines, but limit total length
        full_message = '\n'.join(cleaned_lines)
        if len(full_message) > 3000:  # WhatsApp has message length limits
            full_message = full_message[:3000] + "...\n\n(Message truncated due to length)"
            
        message += full_message
        
        return message
    
    return "⚠️ No tracking details found in the response"