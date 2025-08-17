import re
from email import policy
from email.parser import BytesParser, Parser

def extract_email_content(msg):
    """Enhanced extraction of content from an email message object with all headers"""
    # Extract all headers
    headers = ""
    for header, value in msg.items():
        headers += f"{header}: {value}\n"
    headers += "\n"

    # Extract body
    body = ""

    # Get plain text content
    if msg.is_multipart():
        for part in msg.iter_parts():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition", ""))

            # Skip attachments
            if "attachment" in content_disposition:
                continue

            if content_type == "text/plain":
                try:
                    body += part.get_content()
                except:
                    body += "Error extracting plain text content"
                break
    else:
        # Not multipart - get content directly
        content_type = msg.get_content_type()
        if content_type == "text/plain":
            try:
                body = msg.get_content()
            except:
                body = "Error extracting plain text content"

    # If we couldn't get plain text, try to get HTML and strip tags
    if not body and msg.is_multipart():
        for part in msg.iter_parts():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition", ""))

            # Skip attachments
            if "attachment" in content_disposition:
                continue

            if content_type == "text/html":
                try:
                    # Extract HTML and do basic tag stripping
                    html_content = part.get_content()
                    # Very basic HTML tag removal
                    body = re.sub(r'<[^>]+>', ' ', html_content)
                    body = re.sub(r'\s+', ' ', body).strip()
                except:
                    body = "Error extracting HTML content"
                break

    return headers + body

def extract_email_features(email_data):
    """Extract features from email for analysis"""
    features = {}

    # Check if we have a parsed email or raw text
    if 'msg' in email_data and hasattr(email_data['msg'], 'get'):
        msg = email_data['msg']

        # Basic email fields
        features['from'] = str(msg.get('From', ''))
        features['to'] = str(msg.get('To', ''))
        features['subject'] = str(msg.get('Subject', ''))
        features['date'] = str(msg.get('Date', ''))
        features['return_path'] = str(msg.get('Return-Path', ''))
        features['reply_to'] = str(msg.get('Reply-To', ''))

        # Extract all headers for comprehensive analysis
        features['headers'] = {}
        for header, value in msg.items():
            features['headers'][header] = str(value)

        # Extract body
        body = ""
        if msg.is_multipart():
            for part in msg.iter_parts():
                if part.get_content_type() == "text/plain":
                    try:
                        body += part.get_content()
                    except:
                        pass
        else:
            try:
                if msg.get_content_type() == "text/plain":
                    body = msg.get_content()
            except:
                pass

        features['body'] = body

        # Check for HTML content
        has_html = False
        if msg.is_multipart():
            for part in msg.iter_parts():
                if part.get_content_type() == "text/html":
                    has_html = True
                    break
        else:
            has_html = msg.get_content_type() == "text/html"

        features['has_html'] = has_html

        # Check for attachments
        has_attachments = False
        attachment_count = 0
        if msg.is_multipart():
            for part in msg.iter_parts():
                content_disposition = str(part.get("Content-Disposition", ""))
                if "attachment" in content_disposition:
                    has_attachments = True
                    attachment_count += 1

        features['has_attachments'] = has_attachments
        features['attachment_count'] = attachment_count

    else:
        # We have raw text, not a parsed email
        # Try to extract basic features from text
        raw_text = str(email_data.get('msg', ''))

        # Try to extract headers
        headers_body = raw_text.split('\n\n', 1)
        headers_text = headers_body[0] if len(headers_body) > 0 else ""
        body = headers_body[1] if len(headers_body) > 1 else raw_text

        # Extract from header if present
        from_match = re.search(r'From:\s*(.*)', headers_text, re.IGNORECASE)
        features['from'] = from_match.group(1).strip() if from_match else ""

        # Extract to header if present
        to_match = re.search(r'To:\s*(.*)', headers_text, re.IGNORECASE)
        features['to'] = to_match.group(1).strip() if to_match else ""

        # Extract subject header if present
        subject_match = re.search(r'Subject:\s*(.*)', headers_text, re.IGNORECASE)
        features['subject'] = subject_match.group(1).strip() if subject_match else ""

        # Extract date header if present
        date_match = re.search(r'Date:\s*(.*)', headers_text, re.IGNORECASE)
        features['date'] = date_match.group(1).strip() if date_match else ""

        # Extract all headers
        features['headers'] = {}
        header_pattern = re.compile(r'^([^:]+):\s*(.*)$', re.MULTILINE)
        for match in header_pattern.finditer(headers_text):
            header_name = match.group(1).strip()
            header_value = match.group(2).strip()
            features['headers'][header_name] = header_value

        features['body'] = body
        features['has_html'] = '<html' in raw_text.lower() or '<body' in raw_text.lower()
        features['has_attachments'] = False
        features['attachment_count'] = 0

    return features