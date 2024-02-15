from pytest_bdd import scenarios, given, when, then, parsers

scenarios("bybit_order_execute.feature")


@given(parsers.parse("there are {start:d} cucumbers"), target_fixture="cucumbers")
def given_cucumbers(start):
    print("step 1")
    return {"start": start, "eat": 0}


@when(parsers.parse("I eat {eat:d} cucumbers"))
def eat_cucumbers(cucumbers, eat):
    print("step 2")
    cucumbers["eat"] += eat


@then(parsers.parse("I should have {left:d} cucumbers"))
def should_have_left_cucumbers(cucumbers, left):
    print("step 3")
    assert cucumbers["start"] - cucumbers["eat"] == left
