def classify_email(subject: str, sender: str = "") -> str:
    subject_lower = subject.lower()
    sender_lower = sender.lower()
    
    # More specific rejection patterns
    rejection_keywords = [
        'regret', 'unfortunately', 'not moving forward', 'not selected',
        'decided to move forward with other', 'rejected', 'not be moving forward',
        'will not be proceeding', 'unsuccessful', 'not the right fit',
        'not advancing', 'not proceed', 'not chosen', 'declined'
    ]
    
    # More specific offer patterns
    offer_keywords = [
        'offer', 'congratulations', 'pleased to offer', 'extend an offer',
        'job offer', 'offer letter', 'we would like to offer', 'welcome to',
        'employment offer', 'job offer letter', 'offer of employment'
    ]
    
    # More specific interview patterns
    interview_keywords = [
        'interview', 'schedule a call', 'speak with you', 'next steps',
        'phone screen', 'technical interview', 'assessment', 'coding challenge',
        'meet with', 'discussion', 'video call', 'interview invitation',
        'interview scheduled', 'interview process', 'interview next'
    ]
    
    # More specific application confirmation patterns
    application_keywords = [
        'application received', 'thank you for applying', 'received your application',
        'application for', 'submitted application', 'application confirmation',
        'application submitted', 'application processed', 'application under review'
    ]
    
    # Check for rejection first (highest priority)
    for keyword in rejection_keywords:
        if keyword in subject_lower:
            return "Rejection"
    
    # Check for offers
    for keyword in offer_keywords:
        if keyword in subject_lower:
            return "Offer"
    
    # Check for interviews
    for keyword in interview_keywords:
        if keyword in subject_lower:
            return "Interview"
    
    # Check for application confirmations
    for keyword in application_keywords:
        if keyword in subject_lower:
            return "Application Sent"
    
    # If no specific pattern matches, check if it looks like a real application response
    # vs a job alert/newsletter
    if any(word in subject_lower for word in ['application', 'apply', 'position', 'role', 'job']):
        return "Application Sent"
    
    # Default to Application Sent for any job-related email that passed the filter
    return "Application Sent"

