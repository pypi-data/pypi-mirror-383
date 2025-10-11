"""
Tests for core utils
"""

import pytest

from sim_sci_test_monorepo.core.utils import CoreUtility, hello_core


def test_hello_core():
    """Test the hello_core function."""
    result = hello_core()
    assert result == "Hello from sim_sci_test_monorepo.core! This is a new version!"


def test_core_utility():
    """Test the CoreUtility class."""
    utility = CoreUtility("test")
    assert utility.name == "test"
    assert utility.greet() == "Core utility test is ready!"
