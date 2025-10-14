from boolia import evaluate


def test_and_or():
    assert evaluate("true and false or true") is True


def test_dotted_and_tags():
    ctx = {"house": {"light": {"on": False}}}
    assert evaluate("(car and elephant) or house.light.on", context=ctx, tags={"car"}) is False
    ctx["house"]["light"]["on"] = True
    assert evaluate("(car and elephant) or house.light.on", context=ctx, tags={"car"}) is True


def test_comparisons_in():
    ctx = {"user": {"age": 21, "roles": ["admin", "ops"]}}
    assert evaluate("user.age >= 18 and 'admin' in user.roles", context=ctx)
