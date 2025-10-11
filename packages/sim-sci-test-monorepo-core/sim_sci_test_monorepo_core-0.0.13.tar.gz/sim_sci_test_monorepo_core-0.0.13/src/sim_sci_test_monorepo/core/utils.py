"""
Example core utilities
"""


def hello_core():
    """A simple hello function from core."""
    return "Hello from sim_sci_test_monorepo.core! This is a new version!"


class CoreUtility:
    """An example core utility class."""

    def __init__(self, name: str):
        self.name = name

    def greet(self) -> str:
        return f"Core utility {self.name} is ready!"
