from typing import Optional

class KmdrError(RuntimeError):
    def __init__(self, message: str, solution: Optional[list[str]] = None, *args: object, **kwargs: object):
        super().__init__(message, *args, **kwargs)
        self.message = message

        self._solution = "" if solution is None else "\n[bold cyan]推荐解决方法:[/bold cyan] \n" + "\n".join(f"[cyan]>>> {sol}[/cyan]" for sol in solution)

class InitializationError(KmdrError):
    def __init__(self, message, solution: Optional[list[str]] = None):
        super().__init__(message, solution)

    def __str__(self):
        return f"{self.message}\n{self._solution}"

class LoginError(KmdrError):
    def __init__(self, message, solution: Optional[list[str]] = None):
        super().__init__(message, solution)

    def __str__(self):
        return f"{self.message}\n{self._solution}"

class RedirectError(KmdrError):
    def __init__(self, message, new_base_url: str):
        super().__init__(message)
        self.new_base_url = new_base_url

    def __str__(self):
        return f"{self.message} 新的地址: {self.new_base_url}"

class ResponseError(KmdrError):
    def __init__(self, message, status_code: int):
        super().__init__(message)
        self.status_code = status_code

    def __str__(self):
        return f"{self.message} (状态码: {self.status_code})"