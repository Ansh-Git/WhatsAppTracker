import logging
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

def track_acpl_cargo(tracking_number):
    """
    Track ACPL cargo using the tracking number.
    
    Args:
        tracking_number (str): The tracking number to look up
        
    Returns:
        dict: A dictionary containing the tracking information or error message
    """
    # Step 1: Go to the ACPL tracking page
    base_url = "https://acplcargo.com/GCTRACKING.php"
    api_url = "https://acplcargo.com/poc.php"  # This is the API endpoint called by searchGC() function
    
    try:
        # Create a session to maintain cookies
        session = requests.Session()
        
        # First, let's get the initial page to simulate browser behavior
        logger.info("Accessing ACPL tracking page")
        initial_response = session.get(base_url)
        initial_response.raise_for_status()
        
        # Now, submit the tracking number directly to the API endpoint that's used by searchGC()
        logger.info(f"Submitting tracking number: {tracking_number}")
        
        # The correct parameter is 'gcnumber' based on the form and JavaScript code
        payload = {
            'gcnumber': tracking_number,  # This matches the form field id="gcnumber"
            'etransGCNumber': '',         # These additional parameters are in the JavaScript
            'mode': ''
        }
        
        # Headers to simulate a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
            'Origin': 'https://acplcargo.com',
            'Referer': base_url,
            'X-Requested-With': 'XMLHttpRequest',  # This indicates it's an AJAX request
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        # Submit the tracking request to the API (simulating the searchGC() function)
        logger.info(f"Sending AJAX request to {api_url}")
        response = session.post(api_url, data=payload, headers=headers)
        response.raise_for_status()
        
        # Save the response for debugging
        with open('tracking_response.html', 'w') as f:
            f.write(response.text)
        logger.info("Saved tracking response to tracking_response.html")
        
        # Check if tracking info is found
        if "No Tracking Information available" in response.text or "No Record Found" in response.text:
            return {
                "success": False,
                "message": f"No tracking information found for number {tracking_number}"
            }
        
        # Parse the result HTML (this will be the HTML fragment returned by the API)
        logger.info("Parsing tracking results")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Initialize tracking info with the GC number
        tracking_info = {
            "GC Number": tracking_number
        }
        
        # Extract information from the tracking results
        
        # 1. First check for tables (most common format for shipping info)
        tables = soup.find_all('table')
        logger.info(f"Found {len(tables)} tables in the response")
        
        if tables:
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['th', 'td'])
                    if len(cells) >= 2:
                        key = cells[0].get_text(strip=True)
                        value = cells[1].get_text(strip=True)
                        if key and value:
                            tracking_info[key] = value
        
        # 2. Look for div elements with shipping information 
        # ACPL often uses div elements with specific classes
        info_divs = soup.find_all('div', class_=['info', 'tracking-info', 'result', 'data-row'])
        for div in info_divs:
            # Look for nested divs with key-value pairs
            label_divs = div.find_all(['div', 'span', 'label'], class_=['label', 'title', 'field-name'])
            for label_div in label_divs:
                key = label_div.get_text(strip=True)
                # Get the next sibling which might be the value
                value_elem = label_div.find_next(['div', 'span', 'p'], class_=['value', 'data', 'field-value'])
                if value_elem:
                    value = value_elem.get_text(strip=True)
                    if key and value:
                        tracking_info[key] = value
        
        # 3. Look for definition lists
        dls = soup.find_all('dl')
        for dl in dls:
            dts = dl.find_all('dt')
            dds = dl.find_all('dd')
            for i in range(min(len(dts), len(dds))):
                key = dts[i].get_text(strip=True)
                value = dds[i].get_text(strip=True)
                if key and value:
                    tracking_info[key] = value
        
        # 4. Check for structured data in paragraphs with strong/bold elements
        paragraphs = soup.find_all('p')
        for p in paragraphs:
            strongs = p.find_all(['strong', 'b'])
            for strong in strongs:
                key = strong.get_text(strip=True).rstrip(':')
                # Get the text right after the strong tag
                next_node = strong.next_sibling
                if next_node and hasattr(next_node, 'strip'):
                    value = next_node.strip()
                    if key and value:
                        tracking_info[key] = value
        
        # If we found tracking data beyond just the GC number, return it
        if len(tracking_info) > 1:
            logger.info(f"Successfully extracted tracking data: {tracking_info}")
            return {
                "success": True,
                "message": "Tracking information retrieved",
                "tracking_data": tracking_info
            }
        
        # If we couldn't find structured data, return the raw content
        logger.info("No structured tracking data found, returning raw content")
        page_content = soup.get_text(separator='\n', strip=True)
        
        # Check if the raw content actually has some useful information
        if len(page_content.strip()) > 20:  # Arbitrary length to ensure it's not just whitespace or a tiny error
            return {
                "success": True,
                "message": "Retrieved tracking information as text",
                "raw_content": page_content
            }
        else:
            return {
                "success": False,
                "message": f"No tracking information found for number {tracking_number}"
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
    
    elif "raw_content" in result and result["raw_content"]:
        # Format raw text data
        text = result["raw_content"]
        
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