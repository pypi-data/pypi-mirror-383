import win32com.client

from dateutil.parser import ParserError, parse
from datetime import timedelta, datetime
import sys

OUTLOOK_APPOINTMENT_ITEM = 1
OUTLOOK_MEETING = 1
OUTLOOK_ORGANIZER = 0
OUTLOOK_OPTIONAL_ATTENDEE = 2

ONE_HOUR = 60
THIRTY_MINUTES = 30
FIFTEEN_MINUTES = 15

MEETING_TEXT = """
Meeting type
~~~~~~~~~~~~~

‍Check all that apply.

Update
Discussion
Decision


Goal
~~~~~
{goal}

Agenda
~~~~~~

Item one
Item two
Item three

Next Steps
~~~~~~~~~~
@name task by Due-Date

"""


# OUTLOOK_FORMAT = "%m/%d/%Y %H:%M"
OUTLOOK_FORMAT = "%Y-%m-%d %H:%M"


def outlook_date(dt):
    return dt.strftime(OUTLOOK_FORMAT)


class Meeting:
    def __init__(self):
        self._outlook = None
        self._subject = None
        self._start = None
        self._duration = THIRTY_MINUTES
        self._reminderminuesbeforestart = FIFTEEN_MINUTES
        self._response_requested = False
        self._body = None
        self._recipients = []
        self._location = "Online"
        self._end = None
        self._dontsend = False
        self._allday = False

    def subject(self, msg):
        assert isinstance(msg, str)
        self._subject = msg
        return self

    def start(self, datestr):
        ondate = datestr
        if isinstance(datestr, str):
            ondate = parse(datestr, fuzzy=True)
        self._start = outlook_date(ondate)
        end_date = ondate + timedelta(minutes=self._duration)
        self._end = outlook_date(end_date)
        return self

    def duration(self, duration_in_mins=5):
        assert duration_in_mins >= 5
        self._duration = duration_in_mins
        end_date = parse(self._start) + timedelta(minutes=self._duration)
        self._end = outlook_date(end_date)
        return self

    def remindbefore(self, remind_in_minues=15):
        assert remind_in_minues in [5, 15, 30, 45, 60]
        self._reminderminuesbeforestart = remind_in_minues
        return self

    def request_response(self):
        self._response_requested = not self._response_requested
        return self

    def body(self, msg):
        assert isinstance(msg, str)
        self._body = msg
        return self

    def add_recipient(self, recipient_email):
        assert "@" in recipient_email
        if recipient_email not in self._recipients:
            self._recipients.append(recipient_email)
        return self

    def at(self, place: str):
        assert isinstance(place, str)
        self._location = place
        return self

    def dontsend(self):
        self._dontsend = not self._dontsend
        return self

    def allday(self):
        today = parse(self._start)
        ondate = datetime(today.year, today.month, today.day, 0, 0, 0)
        self._duration = 23 * 60 + 59
        self._start = outlook_date(ondate)
        end_date = ondate + timedelta(minutes=self._duration)
        self._end = outlook_date(end_date)
        self._allday = not self._allday
        return self

    def post(self):
        self._outlook = win32com.client.Dispatch("Outlook.Application")
        mtg = self._outlook.CreateItem(OUTLOOK_APPOINTMENT_ITEM)
        mtg.MeetingStatus = OUTLOOK_MEETING
        mtg.Location = self._location

        for recipient in self._recipients:
            invitee = mtg.Recipients.Add(recipient)
            invitee.Type = OUTLOOK_OPTIONAL_ATTENDEE

        mtg.Subject = self._subject
        mtg.Start = self._start
        mtg.Duration = self._duration
        mtg.ReminderMinutesBeforeStart = self._reminderminuesbeforestart
        mtg.ResponseRequested = self._response_requested
        if self._body is None:
            self._body = "Meeting for {} with {} on {} at {}".format(
                self._subject, ",".join(self._recipients), self._start, self._location
            )

        if self._allday:
            mtg.AllDayEvent = True

        mtg.Body = self._body
        if self._dontsend:
            mtg.Display()
        else:
            mtg.Send()


def maincall(args):
    """
    example

    meet Infy Results 5th aug 4pm -i sukh2010@yahoo.com -w Online
    """

    # parser = create_parser()
    # args = parser.parse_args()

    try:
        msg = " ".join(args.message)
        date, text = parse(msg, fuzzy_with_tokens=True)
    except ParserError:
        raise

    subject = " ".join(text)
    meeting = Meeting().subject(subject).start(date)

    if args.invite:
        meeting = meeting.add_recipient(args.invite)

    if args.on:
        meeting = meeting.start(args.on)

    if args.where:
        meeting = meeting.at(args.where)

    if args.duration:
        meeting = meeting.duration(int(args.duration))

    if args.body:
        if "-" in args.body[0]:
            msg = sys.stdin.read()
            meeting = meeting.body(msg)

    if args.dont_send:
        meeting = meeting.dontsend()

    if args.all_day:
        meeting = meeting.allday()

    meeting.post()

    print(
        "Meeting with subject {} created for {} till {}".format(
            meeting._subject, meeting._start, meeting._end
        )
    )
