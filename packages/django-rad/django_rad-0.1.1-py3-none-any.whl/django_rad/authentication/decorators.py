def skip_auth(func):
    """Mark a method to skip authentication"""
    func.skip_auth = True
    return func
