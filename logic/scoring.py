from datetime import datetime

def calculate_coordinates(factors, target_date_str):
    # Calculate Days to Deadline
    target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
    days_to_deadline = (target_date - datetime.now().date()).days
    
    # Scientific Urgency (X): 0 days = 100 score, 30+ days = 0 score
    deadline_score = max(0, min(100, 100 - (days_to_deadline * 3.33)))
    
    # Aggregated Urgency (X): Deadline 40%, Security 30%, SLA 30%
    x = (deadline_score * 0.40) + \
        (factors['security_pressure'] * 0.30) + \
        (factors['contractual_clock'] * 0.30)
    
    # Aggregated Importance (Y): Fintech Weights
    y = (factors['financial_integrity'] * 0.35) + \
        (factors['service_criticality'] * 0.25) + \
        (factors['blast_radius'] * 0.15) + \
        (factors['regulatory_weight'] * 0.15) + \
        (factors['strategic_priority'] * 0.10)
    
    if x >= 50:
        quadrant = "P1: DO" if y >= 50 else "P3: DELEGATE"
    else:
        quadrant = "P2: SCHEDULE" if y >= 50 else "P4: ELIMINATE"
        
    return round(x, 2), round(y, 2), quadrant, days_to_deadline