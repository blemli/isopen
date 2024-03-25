import time
import datetime
from abc import ABC


class OpeningHours:
    def __init__(self, last_updated):
        self.last_updated = last_updated
        self.timeslots = []

    def add_timeslot(self, new_timeslot):
        self.timeslots.append(new_timeslot)

    def get_opening_hours(self):
        # calculate union of positive slots minus union of negative slots
        # return this as a list of intervals when place is open
        pass

    def is_open_now(self):
        timestamp_now = time.time()
        opening_hours = self.get_opening_hours()
        for timestamp_from, timestamp_to in opening_hours:
            if timestamp_from <= timestamp_now <= timestamp_to:
                return True
        return False

    def next_change(self):
        pass

    def get_remaining_time(self):
        pass
        # use method next_change() to implement this
        # i.e. next_change() - now


class OpeningTimeslot(ABC):
    # NOTE: Timeslots may only be *continuous* time intervals!
    def is_positive(self):
        pass

    def open_intervall_24h(self):
        pass


class AlwaysTimeslot(OpeningTimeslot):
    def __init__(self, is_positive):
        self.is_positive = is_positive

    def __str__(self):
        string_repr = "24/7"
        if not self.is_positive:
            string_repr += " off"
        return string_repr

    def is_positive(self):
        return self.is_positive

    def open_intervall_24h(self):
        timestamp_from = time.time()
        seconds_in_24_hours = 24 * 60 * 60
        timestamp_to = int(timestamp_from + seconds_in_24_hours)
        return timestamp_from, timestamp_to


class SunriseSunsetTimeslot(OpeningTimeslot):
    def __init__(self, is_positive):
        self.is_positive = is_positive

    def __str__(self):
        string_repr = "sunrise-sunset"
        if not self.is_positive:
            string_repr += " off"
        return string_repr

    def is_positive(self):
        return self.is_positive

    def open_intervall_24h(self):
        """
        import astral # use version 1.10.1
        LOCATION_NAME = "Winterthur"
        a = astral.Astral()
        a.solar_depression = "civil"
        location = a[LOCATION_NAME]
        sun = location.sun(date=datetime.date.today(), local=True)
        sunrise = sun["sunrise"]
        sunset = sun["sunset"]
        print(sunrise)
        print(sunset)
        """
        pass


class SingleWeekdayTimeslot(OpeningTimeslot):
    def __init__(self, weekday, time_from, time_to, is_positive):
        self.weekday = weekday
        self.time_from = time_from
        self.time_to = time_to
        self.is_positive = is_positive

    def __str__(self):
        string_repr = self.weekday + " " + self.time_from + "-" + self.time_to
        if not self.is_positive:
            string_repr += " off"
        return string_repr

    def is_positive(self):
        return self.is_positive

    def open_intervall_24h(self):
        WEEKDAY_ABBREVIATIONS = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
        current_date = datetime.datetime.now().date()
        weekday_index = WEEKDAY_ABBREVIATIONS.index(self.weekday)
        start_of_week = current_date - datetime.timedelta(days=current_date.weekday())
        start_of_weekday = start_of_week + datetime.timedelta(days=weekday_index)
        end_of_weekday = start_of_weekday + datetime.timedelta(days=1)
        timestamp_from = int(time.mktime(start_of_weekday.timetuple()))
        timestamp_to = int(time.mktime(end_of_weekday.timetuple()))
        timestamp_now = time.time()
        seconds_in_24_hours = 24 * 60 * 60
        timestamp_max = int(timestamp_now + seconds_in_24_hours)
        if timestamp_to > timestamp_max:
            timestamp_to = timestamp_max
        return timestamp_from, timestamp_to


class SingleMonthTimeslot(OpeningTimeslot):
    def __init__(self, month, time_from, time_to, is_positive):
        self.month = month
        self.time_from = time_from
        self.time_to = time_to
        self.is_positive = is_positive

    def __str__(self):
        return self.month + " " + self.time_from + "-" + self.time_to

    def is_positive(self):
        return self.is_positive

    def open_intervall_24h(self):
        pass


class SingleMonthdayTimeslot(OpeningTimeslot):
    def __init__(self, month, monthday, time_from, time_to, is_positive):
        self.month = month
        self.monthday = monthday
        self.time_from = time_from
        self.time_to = time_to
        self.is_positive = is_positive

    def __str__(self):
        string_repr = self.month + " " + self.monthday + " " + self.time_from + "-" + self.time_to
        if not self.is_positive:
            string_repr += " off"
        return string_repr

    def is_positive(self):
        return self.is_positive

    def open_intervall_24h(self):
        time_to = self.time_to
        if time_to == "24:00":
            time_to = "23:59"
        current_year = datetime.datetime.now().year
        MONTH_ABBREVIATIONS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        month_index = OSM_Parser.MONTH_ABBREVIATIONS.index(self.month) + 1
        date_obj = datetime.datetime(current_year, month_index, int(self.monthday))
        time_obj_from = datetime.datetime.strptime(self.time_from, "%H:%M")
        time_obj_to = datetime.datetime.strptime(time_to, "%H:%M")
        start_datetime = datetime.datetime.combine(date_obj.date(), time_obj_from.time())
        end_datetime = datetime.datetime.combine(date_obj.date(), time_obj_to.time())
        timestamp_from = int(time.mktime(start_datetime.timetuple()))
        timestamp_to = int(time.mktime(end_datetime.timetuple()))
        timestamp_now = time.time()
        seconds_in_24_hours = 24 * 60 * 60
        timestamp_max = int(timestamp_now + seconds_in_24_hours)
        if timestamp_to > timestamp_max:
            timestamp_to = timestamp_max
        return timestamp_from, timestamp_to


class HolidayTimeslot(OpeningTimeslot):
    pass


class OpeningHoursParser(ABC):
    @staticmethod
    def get_timeslot(opening_hours_string):
        pass


class OSM_Parser(OpeningHoursParser):
    # TODO: use numeric definition instead of such lists outside of this parser class
    WEEKDAY_ABBREVIATIONS = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
    MONTH_ABBREVIATIONS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    HOLIDAY_INDICATOR = "PH"

    @staticmethod
    def __add_single_weekday(timeslots, weekday, time_specification, is_positive):
        weekday_timeslots = time_specification.split(",")
        for timeslot in weekday_timeslots:
            time_from = timeslot.split("-")[0]
            time_to = timeslot.split("-")[1]
            time_from_parsed = datetime.datetime.strptime(time_from, "%H:%M")
            time_from_numeric = time_from_parsed.hour + time_from_parsed.minute / 60
            time_to_parsed = datetime.datetime.strptime(time_to, "%H:%M")
            time_to_numeric = time_to_parsed.hour + time_to_parsed.minute / 60
            if time_from_numeric > time_to_numeric:
                # day overlap condition, split up in separate time slots
                timeslots.append(SingleWeekdayTimeslot(weekday, time_from, "00:00", is_positive))
                current_weekday_index = OSM_Parser.WEEKDAY_ABBREVIATIONS.index(weekday)
                next_weekday_index = (current_weekday_index + 1) % len(OSM_Parser.WEEKDAY_ABBREVIATIONS)
                next_weekday = OSM_Parser.WEEKDAY_ABBREVIATIONS[next_weekday_index]
                timeslots.append(SingleWeekdayTimeslot(next_weekday, "00:00", time_to, is_positive))
            else:
                timeslots.append(SingleWeekdayTimeslot(weekday, time_from, time_to, is_positive))

    @staticmethod
    def get_timeslot(opening_hours_string):
        timeslots = []
        schedule_parts = opening_hours_string.split("; ")
        for part in schedule_parts:
            is_positive = True
            subparts = part.split(" ")
            if subparts[-1] == "off":
                is_positive = False
            if subparts[0] == "24/7":
                timeslots.append(AlwaysTimeslot(is_positive))
            elif subparts[0] == "sunrise-sunset":
                timeslots.append(SunriseSunsetTimeslot(is_positive))
            else:
                if subparts[0] in OSM_Parser.WEEKDAY_ABBREVIATIONS:
                    weekday = subparts[0]
                    if "-" not in subparts[1]:
                        # whole weekday
                        timeslots.append(SingleWeekdayTimeslot(weekday, "00:00", "24:00", is_positive))
                    else:
                        OSM_Parser.__add_single_weekday(timeslots, weekday, subparts[1], is_positive)
                elif subparts[0] in OSM_Parser.MONTH_ABBREVIATIONS:
                    month = subparts[0]
                    if ":" not in part:
                        if "-" not in part:
                            timeslots.append(SingleMonthdayTimeslot(month, subparts[1], "00:00", "24:00", is_positive))
                        else:
                            day_from = subparts[1].split("-")[0]
                            day_to = subparts[1].split("-")[1]
                            for current_day in range(int(day_from), int(day_to) + 1):
                                timeslots.append(
                                    SingleMonthdayTimeslot(month, str(current_day), "00:00", "24:00", is_positive))
                    else:
                        subpart_count = len(subparts)
                        if subpart_count > 2:
                            day_from = subparts[1].split("-")[0]
                            day_to = subparts[1].split("-")[1]
                            time_from = subparts[2].split("-")[0]
                            time_to = subparts[2].split("-")[1]
                            for current_day in range(int(day_from), int(day_to) + 1):
                                timeslots.append(
                                    SingleMonthdayTimeslot(month, str(current_day), time_from, time_to, is_positive))
                        else:
                            time_from = subparts[1].split("-")[0]
                            time_to = subparts[1].split("-")[1]
                            timeslots.append(SingleMonthTimeslot(month, time_from, time_to, is_positive))
                elif "-" in subparts[0]:
                    # multi-day or multi-month (sunrise-sunset already excluded)
                    subsubparts = subparts[0].split("-")
                    if subsubparts[0] in OSM_Parser.WEEKDAY_ABBREVIATIONS:
                        weekday_from = subsubparts[0]
                        weekday_to = subsubparts[1]
                        weekday_from_index = OSM_Parser.WEEKDAY_ABBREVIATIONS.index(weekday_from)
                        weekday_to_index = OSM_Parser.WEEKDAY_ABBREVIATIONS.index(weekday_to)
                        if weekday_from_index > weekday_to_index:
                            weekday_from_index, weekday_to_index = weekday_to_index, weekday_from_index
                        weekdays_list = OSM_Parser.WEEKDAY_ABBREVIATIONS[weekday_from_index: weekday_to_index + 1]
                        for current_weekday in weekdays_list:
                            OSM_Parser.__add_single_weekday(timeslots, current_weekday, subparts[1], is_positive)
                    elif subsubparts[0] in OSM_Parser.MONTH_ABBREVIATIONS:
                        # TODO: handle multi-month and multi-day combinations
                        month_from = subsubparts[0]
                        month_to = subsubparts[1]
                        month_from_index = OSM_Parser.MONTH_ABBREVIATIONS.index(month_from)
                        month_to_index = OSM_Parser.MONTH_ABBREVIATIONS.index(month_to)
                        if month_from_index > month_to_index:
                            month_from_index, month_to_index = month_to_index, month_from_index
                        months_list = OSM_Parser.MONTH_ABBREVIATIONS[month_from_index: month_to_index + 1]
                        for current_month in months_list:
                            raise NotImplementedError
                    else:
                        raise NotImplementedError
                elif subparts[0] == OSM_Parser.HOLIDAY_INDICATOR:
                    # return HolidayTimeslot(...)
                    raise NotImplementedError
        return timeslots


if __name__ == "__main__":
    result = OSM_Parser.get_timeslot(
        "24/7; Mar 15:00-17:00; sunrise-sunset; Aug 31 off; Jan 17-23 09:33-17:45; Mo 10:00-20:00; We 08:00-02:00; "
        "Tu-Fr 08:00-12:00,12:30-15:00 off")
    for ts in result:
        print(ts)
        print(ts.open_intervall_24h())
