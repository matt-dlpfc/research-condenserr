from enum import Enum, auto

class TaskType(Enum):
    CLINICAL = "clinical"
    GENERAL = "general"
    
    @classmethod
    def from_string(cls, value: str) -> "TaskType":
        try:
            return cls(value.lower())
        except ValueError:
            raise ValueError(f"Invalid task type. Available types: {[t.value for t in cls]}")

class DataSource(Enum):
    HTML = "html"
    URL = "url"
    API = "api"
    
    @classmethod
    def get_sources_for_task(cls, task_type: TaskType) -> list["DataSource"]:
        if task_type == TaskType.CLINICAL:
            return [cls.HTML, cls.URL, cls.API]
        return [cls.HTML, cls.URL]
