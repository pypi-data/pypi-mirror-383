import pytest

from geqo.visualization.common import valid_angle, valid_name


class TestCommon:
    def test_valid_name(self):
        with pytest.raises(
            TypeError,
            match="Gate/Sequence name must be a string.",
        ):
            valid_name(1)

        assert not valid_name("abcde")
        assert not valid_name("ABcd")
        assert valid_name("abcd")

    def test_valid_angle(self):
        with pytest.raises(
            TypeError,
            match="Phase placeholder must be a string.",
        ):
            valid_angle(1)

        valid_angle("a", non_pccm=False)
