from outlook_meetings import cli
from outlook_meetings.outlookmeet import Meeting


def test_create_parser():
    parser = cli.create_parser()
    result = parser.parse_args("hello")
    assert result.message == ["h", "e", "l", "l", "o"]


def test_meeting():
    meet = Meeting()
    meet.subject("Make tea").start("6 december 2022 2pm").add_recipient(
        "sukh@singh.com"
    )
    assert meet._subject == "Make tea"
    assert meet._start == "2022-12-06 14:00"
    assert meet._end == "2022-12-06 14:30"
    assert meet._recipients == ["sukh@singh.com"]
