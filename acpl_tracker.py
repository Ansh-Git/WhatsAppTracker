import logging
import requests
from bs4 import BeautifulSoup
import trafilatura

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
                            tracking_info[key] = value
        
        # If we couldn't extract structured data, use trafilatura to get clean text
        if not tracking_info:
            # Extract clean text from the page
            clean_text = trafilatura.extract(response.text)
            
            if clean_text:
                return {
                    "success": True,
                    "message": "Tracking information retrieved",
                    "raw_text": clean_text.strip()
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
    
    if "tracking_data" in result:
        # Format structured data
        message = "📦 *ACPL Cargo Tracking Information*\n\n"
        
        for key, value in result["tracking_data"].items():
            message += f"*{key}*: {value}\n"
            
        return message
    
    elif "raw_text" in result:
        # Format raw text data
        text = result["raw_text"]
        
        # Try to clean up the raw text output
        lines = text.split('\n')
        cleaned_lines = [line.strip() for line in lines if line.strip()]
        
        message = "📦 *ACPL Cargo Tracking Information*\n\n"
        message += '\n'.join(cleaned_lines)
        
        return message
    
    return "⚠️ No tracking details found in the response"