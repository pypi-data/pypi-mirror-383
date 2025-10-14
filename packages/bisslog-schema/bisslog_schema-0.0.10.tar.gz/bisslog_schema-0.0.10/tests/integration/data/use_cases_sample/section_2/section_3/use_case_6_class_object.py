"""Use case 6 sample async class definition"""
from bisslog import BasicUseCase, use_case


class UseCase6ClassObject(BasicUseCase):
    """Use case 6 sample async class"""

    @use_case
    def something(self, something: str, something_else: int):
        """Use case 6 sample async method"""
        self.log.info("Use Case 6 did something")

        return f"Use Case 6 {something} -> {something_else}"


use_case_6_class_object = UseCase6ClassObject()
