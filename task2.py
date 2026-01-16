def count_valid_emails(emails):
    count = 0

    for email in emails:
        if "@" in email:
            count += 1

    return count
