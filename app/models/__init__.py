# Import all models to make them available at package level
from .base import TimeStampedModel, ActiveModel
from .election import Election
from .party import Party
from .candidate import Candidate
from .vote import Vote

# For backwards compatibility, make models available at the package level
__all__ = [
    # Base models and mixins
    'TimeStampedModel',
    'ActiveModel',
    # Main models
    'Election',
    'Party', 
    'Candidate',
    'Vote'
]