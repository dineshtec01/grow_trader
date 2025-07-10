# logger.py

log_storage = []  # This stores logs if needed

def log_message(message, print_to_console=True, store=True):
    """Log message by printing and/or storing."""
    if print_to_console:
        print(message)

    if store:
        log_storage.append(str(message))

def get_logs():
    """Return the list of stored logs."""
    return log_storage

def clear_logs():
    """Clear stored logs."""
    log_storage.clear()
