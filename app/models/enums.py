from enum import Enum


class StatusEnum(str, Enum):
    confirmed = "confirmed"
    en_route = "en_route"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"
    review_needed = "review_needed"
