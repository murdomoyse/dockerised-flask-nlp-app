from src.hardrules import HardRules


def test_HardRules(
    comment="This is a test comment to test the hard rules object setup. NICE!",
    title="This is the title of the test comment.",
):
    obj = HardRules(comment=comment, title=title)
    assert isinstance(obj.apply(), dict)
