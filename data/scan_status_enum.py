from enum import Enum

class ScanStatusEnum(Enum):
    PENDING = "pending" # pending for to get picked up by a worker
    IN_PROGRESS = "processing" # currently being processed by a worker
    COMPLETED = "completed" # completed by a worker
    ERROR = "error" # error by a worker
