import pytest


class TestDummy:
    def test_pass(self):
        x = 1
        y = 2
        if x != y:
            pytest.xfail("Known issue: x is not equal to y")
        assert True

    @pytest.mark.xfail(reason="Known issue: x is not equal to y")
    def test_pass2(self):
        x = 1
        y = 2
        assert x == y


print("test_dummy_regular.py")
