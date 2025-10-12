"""
first_dance top-level package.

Expose functions so users can:
  from first_dance import func1, func2
or:
  import first_dance.greet
  import first_dance.tour
"""

from .greet import hello_world
from .tour import tour_plan
from .pdf import PDF

__all__ = ["tour_plan", "hello_world", "PDF"]
__version__ = "0.1.7"

#
# from self_pypi.src.first_dance import tour_plan
#
# __all__ = ["tour_plan"]
