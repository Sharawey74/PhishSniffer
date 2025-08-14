import re
import urllib.parse
import numpy as np

def analyze_sender(email_features):
    """Analyze sender information for suspicious indicators"""
    sender_features = {}

    from_address = email_features.get('from', '')
    reply_to = email_features.get('reply_to', '')
    return_path = email_features.get('return_path', '')

    # Extract email addresses with regex
    from_email = extract_email_address(from_address)
    reply_to_email = extract_email_address(reply_to)
    return_path_email = extract_email_address(return_path)

    # Check for suspicious sender patterns
    sender_features['sender_domain_mismatch'] = check_domain_mismatch(from_email, reply_to_email,
                                                                   return_path_email)
    sender_features['sender_has_numbers'] = bool(re.search(r'\d{3,}', from_email))
    sender_features['sender_free_email'] = is_free_email_provider(from_email)
    sender_features['sender_suspicious_tld'] = has_suspicious_tld(from_email)
    sender_features['sender_has_suspicious_words'] = has_suspicious_sender_words(from_address)

    # Check display name vs email address
    display_name = extract_display_name(from_address)
    sender_features['sender_display_name_mismatch'] = check_display_name_mismatch(display_name, from_email)

    # Store raw values
    sender_features['sender_email'] = from_email
    sender_features['sender_display_name'] = display_name
    sender_features['sender_domain'] = extract_domain(from_email)

    return sender_features

def extract_email_address(text):
    """Extract email address from a string"""
    if not text:
        return ""

    # Simple regex to extract email
    match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    return match.group(0) if match else ""

def extract_display_name(from_string):
    """Extract display name from From header"""
    if not from_string:
        return ""

    # Check for format "Display Name <email@example.com>"
    match = re.search(r'^([^<]+)<', from_string)
    if match:
        return match.group(1).strip()
    return ""

def extract_domain(email):
    """Extract domain from email address"""
    if '@' in email:
        return email.split('@')[1].lower()
    return ""

def check_domain_mismatch(from_email, reply_to_email, return_path_email):
    """Check if email domains don't match between headers"""
    if not from_email:
        return False

    from_domain = extract_domain(from_email)

    # Check reply-to if it exists
    if reply_to_email and from_domain:
        reply_domain = extract_domain(reply_to_email)
        if reply_domain and reply_domain != from_domain:
            return True

    # Check return-path if it exists
    if return_path_email and from_domain:
        return_domain = extract_domain(return_path_email)
        if return_domain and return_domain != from_domain:
            return True

    return False

def check_display_name_mismatch(display_name, email):
    """Check if display name tries to impersonate a different domain"""
    if not display_name or not email:
        return False

    # Convert to lowercase
    display_name = display_name.lower()
    email_domain = extract_domain(email).lower()

    # Check if display name contains a different domain than the email
    domain_pattern = r'\b([a-z0-9-]+\.[a-z0-9-]+(?:\.[a-z0-9-]+)*)\b'
    domains_in_display = re.findall(domain_pattern, display_name)

    for domain in domains_in_display:
        # If display name has a domain that's not the email domain
        if domain and len(domain.split('.')) > 1 and domain != email_domain:
            if not (domain in email_domain or email_domain in domain):
                return True

    # Check for company names
    common_companies = ['paypal', 'amazon', 'apple', 'microsoft', 'google', 'facebook',
                        'netflix', 'bank', 'chase', 'wells fargo', 'citibank', 'amex',
                        'american express']

    for company in common_companies:
        if company in display_name and company not in email_domain:
            return True

    return False

def is_free_email_provider(email):
    """Check if the email is from a free provider"""
    if not email:
        return False

    domain = extract_domain(email)

    free_providers = [
        'gmail.com', 'yahoo.com', 'hotmail.com', 'aol.com', 'outlook.com',
        'mail.com', 'zoho.com', 'protonmail.com', 'icloud.com', 'yandex.com',
        'gmx.com', 'tutanota.com'
    ]

    return domain in free_providers

def has_suspicious_tld(email):
    """Check if the email has a suspicious TLD"""
    if not email:
        return False

    domain = extract_domain(email)
    if not domain:
        return False

    tld = domain.split('.')[-1].lower() if '.' in domain else ''

    suspicious_tlds = [
        'xyz', 'top', 'club', 'online', 'site', 'cyou', 'icu',
        'work', 'live', 'click', 'link', 'bid', 'party'
    ]

    return tld in suspicious_tlds

def has_suspicious_sender_words(sender_string):
    """Check if sender has suspicious words"""
    if not sender_string:
        return False

    sender_string = sender_string.lower()

    suspicious_words = [
        'security', 'verify', 'update', 'support', 'team', 'alert',
        'notification', 'account', 'confirm', 'secure', 'service',
        'admin', 'billing', 'payment', 'official', 'helpdesk'
    ]

    for word in suspicious_words:
        if word in sender_string:
            return True

    return False

def extract_urls(email_features):
    """Extract and analyze URLs from email"""
    url_features = {}
    extracted_urls = []

    body = email_features.get('body', '')
    subject = email_features.get('subject', '')

    # Extract URLs from body and subject
    body_urls = find_urls(body)
    subject_urls = find_urls(subject)

    all_urls = body_urls + subject_urls
    extracted_urls = all_urls

    # URL analysis
    url_features['has_urls'] = len(all_urls) > 0
    url_features['url_count'] = len(all_urls)
    url_features['has_shortened_urls'] = has_shortened_urls(all_urls)
    url_features['has_ip_urls'] = has_ip_urls(all_urls)
    url_features['has_suspicious_tlds'] = has_urls_with_suspicious_tlds(all_urls)
    url_features['has_url_mismatch'] = has_url_text_mismatch(body)
    url_features['urls'] = all_urls

    return url_features, extracted_urls

def find_urls(text):
    """Find URLs in text"""
    if not text:
        return []

    # URL regex pattern
    url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[/\w\.-]*(?:\?[/\w\.-=%&+]*)?'

    # Find all URLs
    urls = re.findall(url_pattern, text)

    # Remove duplicates while preserving order
    unique_urls = []
    for url in urls:
        if url not in unique_urls:
            unique_urls.append(url)

    return unique_urls

def has_shortened_urls(urls):
    """Check if any URLs are shortened"""
    if not urls:
        return False

    shortening_services = [
        'bit.ly', 'tinyurl.com', 'goo.gl', 't.co', 'ow.ly',
        'tiny.cc', 'is.gd', 'buff.ly', 'rebrand.ly', 'cutt.ly',
        'shorturl.at', 'clck.ru', 'bitly.com'
    ]

    for url in urls:
        parsed = urllib.parse.urlparse(url)
        domain = parsed.netloc.lower()

        if domain in shortening_services:
            return True

    return False

def has_ip_urls(urls):
    """Check if any URLs use IP addresses"""
    if not urls:
        return False

    # IP address pattern
    ip_pattern = r'https?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'

    for url in urls:
        if re.match(ip_pattern, url):
            return True

    return False

def has_urls_with_suspicious_tlds(urls):
    """Check if URLs have suspicious TLDs"""
    if not urls:
        return False

    suspicious_tlds = [
        'xyz', 'top', 'club', 'online', 'site', 'cyou', 'icu',
        'work', 'live', 'click', 'link', 'bid', 'party', 'tk',
        'ml', 'ga', 'cf', 'gq', 'pw'
    ]

    for url in urls:
        parsed = urllib.parse.urlparse(url)
        domain = parsed.netloc.lower()

        if '.' in domain:
            tld = domain.split('.')[-1]
            if tld in suspicious_tlds:
                return True

    return False

def has_url_text_mismatch(body):
    """Check for URL text mismatch (e.g., <a href="evil.com">bank.com</a>)"""
    if not body:
        return False

    # This is a simple implementation - in HTML emails we would need more sophisticated parsing
    href_pattern = r'<a\s+(?:[^>]*?\s+)?href=(["\'])(.*?)\1[^>]*>(.*?)</a>'

    matches = re.findall(href_pattern, body, re.IGNORECASE)

    for match in matches:
        href_url = match[1]
        link_text = match[2]

        # Remove tags from link text
        link_text = re.sub(r'<[^>]+>', '', link_text)

        # Extract domains to compare
        href_domain = extract_domain_from_url(href_url)

        # Check if link text contains a URL
        text_urls = find_urls(link_text)
        if text_urls:
            text_domain = extract_domain_from_url(text_urls[0])
            if href_domain and text_domain and href_domain != text_domain:
                return True

        # Check if link text contains domain-like text
        domain_pattern = r'[\w-]+\.[\w-]+(?:\.[\w-]+)*'
        domain_matches = re.findall(domain_pattern, link_text)

        for domain in domain_matches:
            if href_domain and domain != href_domain and '.' in domain:
                return True

    return False

def extract_domain_from_url(url):
    """Extract domain from URL"""
    try:
        parsed = urllib.parse.urlparse(url)
        domain = parsed.netloc.lower()
        return domain
    except:
        return ""

def scan_phishing_patterns(email_features):
    """Scan for common phishing patterns in the email"""
    pattern_features = {}

    subject = email_features.get('subject', '').lower()
    body = email_features.get('body', '').lower()

    # Check subject for suspicious words
    suspicious_subject_words = [
        'urgent', 'alert', 'verify', 'update', 'security', 'account',
        'suspended', 'unusual', 'confirm', 'verify', 'important',
        'password', 'login', 'immediately', 'attention', 'required'
    ]

    pattern_features['subject_has_urgency'] = any(word in subject for word in suspicious_subject_words)

    # Check for urgency phrases in body
    urgency_phrases = [
        'act now', 'urgent action', 'immediate action', 'expires soon',
        'limited time', '24 hours', 'immediately', 'as soon as possible',
        'failure to comply', 'account will be', 'before it\'s too late',
        'right away', 'time sensitive'
    ]

    pattern_features['body_has_urgency'] = any(phrase in body for phrase in urgency_phrases)

    # Check for sensitive data requests
    sensitive_requests = [
        'password', 'credit card', 'account number', 'credentials',
        'social security', 'ssn', 'banking details', 'personal details',
        'pin', 'security question', 'mother\'s maiden name', 'login',
        'username and password'
    ]

    pattern_features['requests_sensitive_data'] = any(phrase in body for phrase in sensitive_requests)

    # Check for suspicious claims
    suspicious_claims = [
        'won', 'winner', 'lottery', 'selected', 'prize', 'million',
        'reward', 'inheritance', 'claim your', 'you have been chosen',
        'congratulations', 'exclusive offer', 'free gift', 'jackpot'
    ]

    pattern_features['has_suspicious_claims'] = any(phrase in body for phrase in suspicious_claims)

    # Check for poor grammar/spelling
    grammar_indicators = [
        'kindly', 'dear valued', 'dear costumer', 'dear customer',
        'your account will closed', 'verify you account', 'your are',
        'we detected unusual', 'we detected suspicious'
    ]

    pattern_features['has_poor_grammar'] = any(phrase in body for phrase in grammar_indicators)

    # Check for threatening language
    threatening_phrases = [
        'suspended', 'terminated', 'closed', 'deleted', 'unauthorized',
        'suspicious activity', 'unusual activity', 'breach',
        'compromised', 'locked', 'restricted', 'limitation'
    ]

    pattern_features['has_threatening_language'] = any(phrase in body for phrase in threatening_phrases)

    return pattern_features

def prepare_features_for_model(all_features, model_feature_count=10):
    """Extract model features from email features dictionary"""
    try:
        # Extract email content
        email_text = ""

        # Extract body text
        if 'body' in all_features:
            email_text += all_features['body'] + " "

        # Include subject
        if 'subject' in all_features:
            email_text += all_features['subject'] + " "

        # Include from field
        if 'from' in all_features:
            email_text += all_features['from'] + " "

        # Extract standardized features from text
        features = extract_features_from_text(email_text)

        # Ensure we have a valid feature array
        if features is None or len(features) != model_feature_count:
            # Create a default feature array of the right size if needed
            features = np.zeros(model_feature_count)

        # Reshape for model prediction
        return features.reshape(1, -1)

    except Exception as e:
        print(f"Error preparing features: {e}")
        # Return safe default
        return np.zeros((1, model_feature_count))

def extract_features_from_text(text):
    """Extract standardized features from email text for model training"""
    try:
        # Initialize features array
        features = np.zeros(10)  # Using 10 features for comprehensive analysis

        # Convert text to lowercase for case-insensitive matching
        text = str(text).lower()

        # Feature 1: Contains suspicious sender patterns (from, paypal, bank, etc.)
        suspicious_senders = ['paypal', 'bank', 'account', 'security', 'update', 'verify', 'amazon']
        features[0] = int(any(sender in text[:500] for sender in suspicious_senders))

        # Feature 2: Contains URLs
        features[1] = int(bool(re.search(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', text)))

        # Feature 3: Contains shortened URLs (CRITICAL INDICATOR)
        short_domains = ['bit.ly', 'tinyurl.com', 'goo.gl', 't.co', 'ow.ly', 'is.gd']
        features[2] = int(any(domain in text for domain in short_domains)) * 2  # Double weight

        # Feature 4: Contains IP-based URLs (CRITICAL INDICATOR)
        features[3] = int(bool(re.search(r'https?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', text))) * 2  # Double weight

        # Feature 5: Contains urgency words
        urgency_words = ['urgent', 'immediately', 'alert', 'verify', 'suspend', 'restrict',
                         'limited', 'expires', 'validate', 'confirm', 'act now', 'before', 'offer expires']
        features[4] = int(any(word in text for word in urgency_words))

        # Feature 6: Contains sensitive data requests (CRITICAL INDICATOR)
        sensitive_requests = ['password', 'credit card', 'ssn', 'social security', 'credentials',
                              'login', 'username', 'pin', 'bank account', 'billing']
        features[5] = int(any(req in text for req in sensitive_requests)) * 1.5  # Increased weight

        # Feature 7: Contains suspicious attachment mentions
        attachment_words = ['attach', 'document', 'file', 'pdf', 'doc', 'invoice', 'receipt', 'statement']
        features[6] = int(any(word in text for word in attachment_words))

        # Feature 8: Contains financial/money terms
        money_terms = ['$', 'dollar', 'payment', 'transfer', 'transaction', 'wire', 'money',
                       'credit', 'debit', 'cash', 'fund', 'tax', 'refund', 'gift card']
        features[7] = int(any(term in text for term in money_terms))

        # Feature 9: Contains threatening language
        threat_terms = ['suspended', 'terminated', 'unauthorized', 'closed', 'limited',
                        'suspicious activity', 'unusual', 'breach', 'compromised', 'fraud']
        features[8] = int(any(term in text for term in threat_terms))

        # Feature 10: Contains suspicious offers/claims (CRITICAL INDICATOR)
        offer_terms = ['won', 'winner', 'prize', 'million', 'free', 'discount', 'offer',
                       'reward', 'gift', 'claim', 'congratulations', 'selected', 'amazon gift card']
        features[9] = int(any(term in text for term in offer_terms)) * 2  # Double weight

        # Feature 11 (bonus): Check for domain mismatches
        if '@' in text:
            email_parts = re.findall(r'[\w\.-]+@[\w\.-]+', text)
            domains = [email.split('@')[1].lower() for email in email_parts if '@' in email]
            if len(set(domains)) > 1:  # Multiple different domains in email addresses
                # Increase feature 0 (suspicious sender) as this is a critical indicator
                features[0] = 2

        return features
    except Exception as e:
        print(f"Error extracting features: {e}")
        # Return zeros if extraction fails to maintain consistency
        return np.zeros(10)
    
def check_special_patterns(email_features):
    """Check email against special known phishing patterns"""
    import json
    import os
    
    # Default path for special patterns file
    config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config")
    patterns_file = os.path.join(config_dir, "special_patterns.json")
    
    # If file doesn't exist, return no match
    if not os.path.exists(patterns_file):
        return False
    
    try:
        # Load patterns
        with open(patterns_file, 'r') as file:
            patterns_data = json.load(file)
        
        if not patterns_data or "patterns" not in patterns_data:
            return False
        
        # Get email data
        subject = email_features.get("subject", "").lower()
        from_address = email_features.get("from", "").lower()
        body = email_features.get("body", "").lower()
        
        # Extract URLs from body
        urls = []
        if "url_features" in email_features:
            urls = email_features["url_features"].get("urls", [])
        
        # Check each pattern
        for pattern in patterns_data["patterns"]:
            # Match subject keywords
            if "subject_keywords" in pattern:
                if not any(keyword.lower() in subject for keyword in pattern["subject_keywords"]):
                    continue  # Skip if subject doesn't match
            
            # Match domains
            if "domains" in pattern:
                if not any(domain.lower() in from_address or 
                           domain.lower() in body for domain in pattern["domains"]):
                    continue  # Skip if domains don't match
            
            # Match URLs
            if "urls" in pattern and urls:
                if not any(pattern_url.lower() in url.lower() for pattern_url in pattern["urls"] 
                                                             for url in urls):
                    continue  # Skip if URLs don't match
            
            # If we got here, pattern matches
            return True
    
    except Exception as e:
        print(f"Error checking special patterns: {e}")
    
    return False