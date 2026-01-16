import re

def count_valid_emails(emails):
    """
    Count the number of valid email addresses in the input list.
    
    Args:
        emails: List of email strings to validate
        
    Returns:
        Count of valid email addresses
    """
    if not emails:
        return 0
    
    count = 0
    
    # Basic email pattern: localpart@domain
    # Requires at least one character before @, at least one after @,
    # and at least one dot in the domain with characters after it
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    for email in emails:
        # Handle non-string inputs
        if not isinstance(email, str):
            continue
            
        # Strip whitespace
        email = email.strip()
        
        # Validate using regex pattern
        if re.match(email_pattern, email):
            count += 1
    
    return count
