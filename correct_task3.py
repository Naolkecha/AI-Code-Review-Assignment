def average_valid_measurements(values):
    """
    Calculate the average of valid measurements, ignoring None values.
    
    Args:
        values: List of measurement values (can include None, numbers, or strings)
        
    Returns:
        Average of valid measurements, or 0 if no valid values
    """
    if not values:
        return 0
    
    total = 0
    count = 0
    
    for v in values:
        # Skip None values
        if v is None:
            continue
        
        try:
            # Convert to float and add to total
            numeric_value = float(v)
            total += numeric_value
            count += 1
        except (ValueError, TypeError):
            # Skip values that cannot be converted to float
            continue
    
    # Avoid division by zero - return 0 if no valid measurements
    if count == 0:
        return 0
    
    return total / count
