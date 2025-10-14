"""Use case 6 sample async class definition"""
from bisslog import BasicUseCase, use_case


class UseCase6AsyncClass(BasicUseCase):
    """Use case 6 sample async class"""

    @use_case
    async def custom_name(self, something: str, something_else: int):
        """Use case 6 sample async method"""
        self.log.info("Use Case 6 did something")

        return f"Use Case 6 {something} -> {something_else}"
