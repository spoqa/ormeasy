from ormeasy.sqlalchemy import repr_entity


class Music:

    __repr_columns__ = 'name', 'track_number'

    name = 'The box'

    track_number = 6


def test_repr_entity():
    repr_ = repr_entity(Music())
    assert repr_ == '<sqlalchemy_test.Music name=The box, track_number=6>'
