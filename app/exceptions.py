class TaskError(Exception):
    """Görev iş kurallarından çıkan hataların tabanı."""


class InvalidTaskError(TaskError):
    """Başlık boş veya izin verilen uzunluğun dışında."""


class DuplicateTaskError(TaskError):
    """Aynı başlıkla görev zaten kayıtlı."""


class TaskNotFoundError(TaskError):
    """İstenen görev kimliği yok."""


class TaskAlreadyCompletedError(TaskError):
    """Görev daha önce tamamlanmış."""
