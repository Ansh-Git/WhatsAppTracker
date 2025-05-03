import logging
import requests
from bs4 import BeautifulSoup
import trafilatura
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
        
        # Find the tracking information table
        tracking_info = {}
        
        # Try to find the specific form with tracking results
        search_form = soup.find('form', {'name': 'form_etranschk'})
        if search_form and hasattr(search_form, 'find_all'):
            # Extract information from the form
            input_fields = search_form.find_all('input')
            for field in input_fields:
                field_name = field.get('name')
                field_value = field.get('value')
                if field_name and field_value and field_name != 'submit':
                    tracking_info[field_name] = field_value
        
        # Try to extract tracking information from tables
        tables = soup.find_all('table')
        if tables:
            # Process the main tracking information table
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
        
        # If we couldn't extract structured data, use trafilatura to get clean text
        if not tracking_info:
            # Extract clean text from the page
            clean_text = trafilatura.extract(response.text)
            
            if clean_text:
                # Try to parse the clean text into structured data
                lines = clean_text.strip().split('\n')
                
                # Look for patterns like "Field: Value"
                for line in lines:
                    if ':' in line:
                        parts = line.split(':', 1)
                        key = parts[0].strip()
                        value = parts[1].strip()
                        if key and value:
                            tracking_info[key] = value
                
                if tracking_info:
                    return {
                        "success": True,
                        "message": "Tracking information retrieved",
                        "tracking_data": tracking_info
                    }
                else:
                    return {
                        "success": True,
                        "message": "Tracking information retrieved",
                        "raw_text": clean_text.strip()
                    }
            else:
                # As a last resort, grab any visible text
                all_text = soup.get_text(separator='\n', strip=True)
                if all_text:
                    return {
                        "success": True,
                        "message": "Tracking information retrieved (raw format)",
                        "raw_text": all_text
                    }
                else:
                    return {
                        "success": False,
                        "message": "Could not extract tracking information from the response"
                    }
        
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