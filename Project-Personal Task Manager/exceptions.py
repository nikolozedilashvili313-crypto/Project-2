"""საკუთარი exception-ების იერარქია Task Manager-ისთვის."""


class TaskError(Exception):
    """ყველა საკუთარი შეცდომის ძირითადი კლასი."""


class ValidationError(TaskError):
    """შეყვანილი მონაცემი არასწორია."""


class TaskNotFoundError(TaskError):
    """დავალება ვერ მოიძებნა."""


class StorageError(TaskError):
    """ფაილთან მუშაობის პრობლემა."""