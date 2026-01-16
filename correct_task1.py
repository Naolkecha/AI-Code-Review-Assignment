def calculate_average_order_value(orders):
    """
    Calculate the average order value for non-cancelled orders.
    
    Args:
        orders: List of order dictionaries with 'status' and 'amount' keys
        
    Returns:
        Average order value for non-cancelled orders, or 0 if no valid orders
    """
    if not orders:
        return 0
    
    total = 0
    count = 0
    
    for order in orders:
        # Check if order has required keys
        if not isinstance(order, dict):
            continue
            
        status = order.get("status")
        amount = order.get("amount")
        
        # Only include non-cancelled orders with valid amounts
        if status != "cancelled" and amount is not None:
            try:
                total += float(amount)
                count += 1
            except (ValueError, TypeError):
                # Skip orders with invalid amount values
                continue
    
    # Avoid division by zero
    if count == 0:
        return 0
    
    return total / count
