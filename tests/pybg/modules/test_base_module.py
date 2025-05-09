# test_base_module.py

import pytest

from pybg.modules.base_module import BaseModule  # adjust the import path as needed

pytestmark = pytest.mark.unit


def test_base_module_has_category():
    assert hasattr(
        BaseModule, "category"
    ), "BaseModule should have a 'category' attribute"


def test_base_module_category_value():
    assert BaseModule.category == "General", "BaseModule 'category' should be 'General'"
