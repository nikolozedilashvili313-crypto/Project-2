"""დეკორატორები: შეცდომების დამუშავება და ოპერაციების შეტყობინებები."""
import functools

from exceptions import TaskError


def handle_errors(func):
    """იჭერს აპლიკაციის შეცდომებს და მომხმარებელს გასაგებად აჩვენებს."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except TaskError as e:
            print(f"შეცდომა: {e}")

    return wrapper


def log_action(message):
    """ოპერაციის წარმატებით დასრულების შემდეგ ბეჭდავს შეტყობინებას.

    თუ ფუნქციამ შეცდომა ასროლა, შეტყობინება არ დაიბეჭდება.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            print(message)
            return result

        return wrapper

    return decorator