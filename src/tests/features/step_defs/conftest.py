import pytest


@pytest.hookimpl
def pytest_bdd_before_scenario(request, feature, scenario):
    print("Before scenario:", scenario.name)
    # Perform setup actions
    # Access scenario-specific information via the 'scenario' argument


@pytest.hookimpl
def pytest_bdd_after_scenario(request, feature, scenario):
    print("After scenario:", scenario.name)
    # Perform cleanup actions
    # Access scenario-specific information via the 'scenario' argument
