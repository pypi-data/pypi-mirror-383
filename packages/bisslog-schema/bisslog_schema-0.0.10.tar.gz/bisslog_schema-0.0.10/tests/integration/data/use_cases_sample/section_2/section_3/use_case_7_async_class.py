"""Use Case 7 async"""
from bisslog import AsyncBasicUseCase, use_case


class UseCase7AsyncClass(AsyncBasicUseCase):
    """Use Case 7 async"""

    @use_case
    async def something(self, something: str, something_else: int):
        """Use Case 7 async method"""
        self.log.info("Use Case 7 did something")
        return f"Use Case 7 {something} -> {something_else}"
