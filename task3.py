def average_valid_measurements(values):
    total = 0
    count = len(values)

    for v in values:
        if v is not None:
            total += float(v)

    return total / count
