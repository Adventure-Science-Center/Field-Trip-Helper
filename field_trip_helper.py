# Standard packages
import datetime
import itertools

# Third-party packages
from IPython.display import display, HTML, FileLink
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import requests
import seaborn as sb

# Project packages
import config
import interface as fth_interface


def initialize():
    """Configure the interface and show it."""

    fth_interface.pw_submit_button.on_click(login)
    fth_interface.browse_select_date_button.on_click(generate_schedule_from_browser)
    fth_interface.find_search.on_click(search_from_browser)
    display(HTML("<H1>ASC Field Trip Helper</H1>"))
    display(fth_interface.login_output)
    display(fth_interface.main_output)
    with fth_interface.login_output:
        display(fth_interface.pw_login_box)


def login(*args):
    """Get the username and password from the login fields and retrieve the data."""

    config.username = fth_interface.user_field.value
    config.password = fth_interface.pw_field.value

    fth_interface.pw_status.value = "Loading..."

    retrieve_data()
    with fth_interface.main_output:
        display(fth_interface.interface)


def retrieve_data():
    """Retrieve the latest data from the server"""

    url = "https://s20aalt05web01.sky.blackbaud.com/2532Altru/ODataQuery.ashx?databasename=d32a1a5b-211a-4f58-bab1-36132004843f&AdHocQueryID=379fdd07-ded0-4a38-b183-7c0e49118619"

    session = requests.Session()
    session.auth = (config.username, config.password)

    r = session.get(url)

    config.data = pd.DataFrame(r.json()['value'])

    config.data["Arrival"] = pd.to_datetime(config.data["Arrival"])
    config.data["Departure"] = pd.to_datetime(config.data["Departure"])

    config.data["Start time"] = config.data.apply(create_start_time, axis=1)
    config.data["End time"] = config.data.apply(create_end_time, axis=1)
    config.data["Ticket type"] = config.data["Tickettype"]

    config.data = config.data[
        ["Name", "Arrival", "Departure", "Program", "Category", "Location", "Ticket type", "Quantity", "Capacity",
         "Start time", "End time", "Address"]]

    build_search_schedule()
    fth_interface.login_output.clear_output()


def create_start_time(row: pd.Series) -> pd.Timestamp | None:
    date = row["Arrival"]
    if row.Starttime is None:
        return None

    return pd.Timestamp(date.year, date.month, date.day, int(row.Starttime[0:2]), int(row.Starttime[2:]))


def create_end_time(row: pd.Series) -> pd.Timestamp | None:
    date = row["Arrival"]
    if row.Endtime is None:
        return None

    return pd.Timestamp(date.year, date.month, date.day, int(row.Endtime[0:2]), int(row.Endtime[2:]))


def get_date(df: pd.DataFrame, date) -> pd.DataFrame:
    """Return the field trip entries for the given date."""

    if isinstance(date, str):
        split = date.split('-')
        date = datetime.datetime(int(split[0]), int(split[1]), int(split[2])).date()

    return df[df.Arrival.dt.date == pd.Timestamp(date).date()]


def get_date_range(df: pd.DataFrame, start, end) -> pd.DataFrame:
    """Return a DateFrame containing entries between start and end (inclusive)"""

    if isinstance(start, str):
        split = start.split('-')
        start = datetime.datetime(int(split[0]), int(split[1]), int(split[2])).date()
    if isinstance(end, str):
        split = end.split('-')
        end = datetime.datetime(int(split[0]), int(split[1]), int(split[2])).date()

    return df[(df.Arrival.dt.date >= pd.Timestamp(start).date()) & (df.Arrival.dt.date <= pd.Timestamp(end).date())]


def get_admission(df: pd.DataFrame, date) -> tuple[int, int]:
    """Return a tuple containing the number of schools and visitors for the day."""

    day = get_date(df, date)
    admission = day[day.Category == 'Admission']

    by_school = admission.groupby('Address').sum(numeric_only=True).reset_index()

    return len(by_school), admission.sum(numeric_only=True).Quantity


def get_location(df: pd.DataFrame, location: str) -> pd.DataFrame:
    """Return the field trip entries for the given location."""

    return df[df.Location == location]


def decimal_time(date) -> float:
    """Return the time as a decimal number of hours"""

    return date.hour + date.minute / 60


def format_name(name: str) -> str:
    """Format the name of a given program."""

    if name == 'SCH - L - Amusement Park Physics STEM Lab':
        return "Amusement\nPark Physics"
    if name == 'SCH - L - Squid Dissection STEM Lab':
        return "Squid\nDissection"
    if name == 'SCH - D - Matter Matters':
        return "Matter Matters"
    if name == 'PS - School Shows':
        return "School Show"
    if name == 'SCH - D - Cooking Up a Storm':
        return "Cooking Up\na Storm"
    if name == 'SCH - L - Cow Eye Dissection STEM Lab':
        return "Cow Eye\nDissection"
    if name == 'SCH - D - Get Energized!':
        return 'Get Energized!'
    if name == 'PS - To Worlds Beyond':
        return 'To Worlds\nBeyond'
    if name == 'SCH - L - Splitting Molecules STEM Lab':
        return 'Splitting\nMolecules'
    if name == 'SCH - D - Space Exploration':
        return 'Space\nExploration'
    if name == 'SCH - L - Fetal Pig STEM Lab':
        return 'Fetal Pig\nDissection'
    if name == 'PS - Nightwatch':
        return 'Nightwatch'
    if name == 'SCH - D - Chemistry is a Blast!':
        return 'Chemistry\nis a Blast'
    if name == "SCH - D - Shocking, It's Science!":
        return "Shocking,\nIt's Science!"
    if name == "SCH - D - Get Fired Up!":
        return 'Get Fired Up!'

    return name


def get_color(name_colors: dict, name: str):
    """Return a color for each unique school name"""

    if name not in name_colors:
        name_colors[name] = sb.color_palette("pastel", n_colors=10)[len(name_colors)]

    return name_colors[name]


def check_legend(legend_names: dict[str, bool], name: str) -> str | None:
    """Check if the given name has been added to the legend."""

    if name in legend_names:
        return None

    legend_names[name] = True
    return name


def generate_schedule_image(date):
    """Generate a schedule image and return it."""

    locations = {
        "Jack Wood Hall": 1,
        "Eureka Theater": 2,
        "Learning Lab": 3,
        "Green Classroom": 4,
        "Yellow Classroom": 5,
        "Sudekum Planetarium": 6
    }

    day = get_date(config.data, date)

    if len(day) == 0:
        return

    name_colors = {}
    legend_names = {}

    plt.clf()
    combo = day.groupby(["Name", "Program", "Location", "Start time", "End time", "Capacity"]).sum(
        numeric_only=True).reset_index()
    n_groups, n_visitors = get_admission(day, date)

    for i, row in combo.iterrows():
        if row.Location is None:
            continue

        start = decimal_time(row["Start time"])
        end = decimal_time(row["End time"])
        duration = end - start
        plt.bar(locations[row.Location], duration, bottom=start, label=check_legend(legend_names, row.Name),
                color=get_color(name_colors, row.Name), zorder=10)
        plt.text(locations[row.Location], (start + end) / 2,
                 format_name(row.Program) + "\n(" + str(row.Quantity) + "/" + str(row.Capacity) + ")", ha='center',
                 va='center', zorder=20)

    # Add public shows
    plt.bar(2, .5, bottom=12.5, color=(0.5, 0.5, 0.5), zorder=10)
    plt.text(2, 12.75, "Live Science", ha='center', va='center', wrap=True, color='white', zorder=20)

    plt.bar(6, .5, bottom=11.5, color=(0.5, 0.5, 0.5), zorder=10)
    plt.text(6, 11.75, "Public Show", ha='center', va='center', wrap=True, color='white', zorder=20)

    plt.bar(6, .5, bottom=13.25, color=(0.5, 0.5, 0.5), zorder=10)
    plt.text(6, 13.5, "Public Show", ha='center', va='center', wrap=True, color='white', zorder=20)

    plt.bar(6, .5, bottom=14.25, color=(0.5, 0.5, 0.5), zorder=10)
    plt.text(6, 14.5, "Public Show", ha='center', va='center', wrap=True, color='white', zorder=20)

    plt.legend(bbox_to_anchor=(0.5, -0.2), loc='lower center', ncol=2)

    plt.title(str(np.min(day.Arrival.dt.date)) + f" (Groups: {n_groups}, Visitors: {n_visitors})", fontsize=20)
    plt.gca().invert_yaxis()
    plt.yticks([9, 9.5, 10, 10.5, 11, 11.5, 12, 12.5, 13, 13.5, 14, 14.5, 15],
               ["9 AM", "9:30 AM", "10 AM", "10:30 AM", "11 AM", "11:30 AM", "12 PM", "12:30 PM", "1 PM", "1:30 PM",
                "2 PM", "2:30 PM", "3 PM"])
    plt.xticks([1, 2, 3, 4, 5, 6],
               ["Jack Wood\nHall", "Eureka\nTheater", "Learning\nLab", "Green\nClassroom", "Yellow\nClassroom",
                "Sudekum\nPlanetarium"])
    plt.grid(which='major', axis='y', zorder=1)
    plt.gca().tick_params(right=True, top=True, labelright=True, labeltop=True, rotation=0)

    fig = plt.gcf()
    fig.set_size_inches(10, 8)
    plt.tight_layout()

    return plt.gcf()
    # plt.savefig('schedules/' + str(date) + '.pdf', dpi=300)


def reset_search_schedule():
    """Rebuild the base schedule with no entries"""

    config.schedule_dict = {}

    today = datetime.datetime.now().date()
    next_year = today + pd.Timedelta('365 d')

    day_dict = {9: False, 9.25: False, 9.5: False, 9.75: False,
                10: False, 10.25: False, 10.5: False, 10.75: False,
                11: False, 11.25: False, 11.5: False, 11.75: False,
                12: False, 12.25: False, 12.5: False, 12.75: False,
                13: False, 13.25: False, 13.5: False, 13.75: False,
                14: False, 14.25: False, 14.5: False, 14.75: False}
    jwh_dict = {9: True, 9.25: True, 9.5: True, 9.75: True,
                10: False, 10.25: False, 10.5: False, 10.75: False,
                11: False, 11.25: False, 11.5: False, 11.75: False,
                12: False, 12.25: False, 12.5: False, 12.75: False,
                13: False, 13.25: False, 13.5: False, 13.75: False,
                14: True, 14.25: True, 14.5: True, 14.75: True}
    eureka_dict = {9: False, 9.25: False, 9.5: False, 9.75: False,
                   10: False, 10.25: False, 10.5: False, 10.75: False,
                   11: False, 11.25: False, 11.5: False, 11.75: False,
                   12: False, 12.25: True, 12.5: True, 12.75: True,
                   13: False, 13.25: False, 13.5: False, 13.75: False,
                   14: False, 14.25: False, 14.5: False, 14.75: False}
    planet_dict = {9: False, 9.25: False, 9.5: False, 9.75: False,
                   10: False, 10.25: False, 10.5: False, 10.75: False,
                   11: False, 11.25: False, 11.5: True, 11.75: True,
                   12: True, 12.25: True, 12.5: False, 12.75: False,
                   13: True, 13.25: True, 13.5: True, 13.75: True,
                   14: True, 14.25: True, 14.5: True, 14.75: True}

    for date in pd.date_range(today, next_year):
        if date.weekday() not in [0, 3, 4]:
            # Select Mon, Th, Fri
            continue
        if date.date().month in [6, 7, 8]:
            # Ignore summer
            continue

        date_str = str(date.date())
        admission = get_admission(config.data, date.date())
        config.schedule_dict[date_str] = {
            'Admission': {'groups': admission[0], 'quantity': admission[1]},
            'Jack Wood Hall': jwh_dict.copy(),
            "Eureka Theater": eureka_dict.copy(),
            "Learning Lab": day_dict.copy(),
            "Green Classroom": day_dict.copy(),
            "Yellow Classroom": day_dict.copy(),
            "Sudekum Planetarium": planet_dict.copy()
        }


def build_search_schedule():
    """From the data, build a dict representing the daily schedule"""

    reset_search_schedule()

    for i, row in config.data.iterrows():
        if row.Location is None or row.Location == 'Admission':
            continue

        date = str(row.Arrival.date())
        if date not in config.schedule_dict:
            continue

        start_time = decimal_time(row['Start time'].time())
        end_time = decimal_time(row['End time'].time())
        # Iterate the schedule in the given date/location and block matching times
        for slot in config.schedule_dict[date][row.Location]:
            if start_time <= slot < end_time:
                config.schedule_dict[date][row.Location][slot] = True


def search_admission(number: int) -> dict:
    """Search the schedule for dates that have capacity for the given number."""

    results = {}

    for date in config.schedule_dict:
        admission = config.schedule_dict[date]['Admission']

        if (6 - admission['groups']) > 0 and (600 - admission['quantity']) >= number:
            results[date] = True

    return results


def search_schedule(location: str, duration: float, start_time: float = 9, end_time: float = 14) -> dict:
    """Search the schedule for gaps matching the given location and duration."""
    results = {}

    for date in config.schedule_dict:
        loc_schedule = config.schedule_dict[date][location]
        # Find the available gaps
        for slot in loc_schedule:
            if loc_schedule[slot] is True:
                # This slot is full
                continue
            if slot < start_time or slot >= end_time:
                # This time is outside their visit
                continue
            i = 0
            gap = 0
            while slot + i * 0.25 in loc_schedule and loc_schedule[
                slot + i * 0.25] is False and slot + i * 0.25 < end_time:
                gap += 0.25
                i += 1
            if gap >= duration:
                if date not in results:
                    results[date] = {location: {}}
                results[date][location][slot] = gap
    return results


def combo_search(criteria: list[tuple[str, float]],
                 number: int = 365,
                 start_date=None,
                 end_date=None,
                 start_time: float = 9,
                 end_time: float = 14) -> dict:
    """Search the schedule for multiple criteria, given by (location, duration)."""

    if isinstance(start_date, str):
        split = start_date.split('-')
        start_date = datetime.datetime(int(split[0]), int(split[1]), int(split[2])).date()
    if isinstance(end_date, str):
        split = end_date.split('-')
        end_date = datetime.datetime(int(split[0]), int(split[1]), int(split[2])).date()

    combo_results = {}

    i = 0
    group_size = 0
    criteria_dict = {}
    for criterion in criteria:
        if criterion[0] != 'Admission':
            criteria_dict[criterion[0]] = criterion[1]
            combo_results[i] = search_schedule(criterion[0], criterion[1], start_time=start_time, end_time=end_time)
            i += 1
        else:
            group_size = criterion[1]
    admission_match = search_admission(group_size)

    if len(combo_results) == 0:
        # Bail out without anything to match
        output_dict = admission_match

        # Cut down the dictionary to the given number of elements.
        return {k: output_dict[k] for k, _ in zip(output_dict, range(number))}

    match_dict = {}
    # Throw out dates that are not in all result sets and match the date constraints
    for date in combo_results[0]:
        bad_match = False
        for key in combo_results:
            results_dict = combo_results[key]
            if date not in results_dict:
                bad_match = True
        if date not in admission_match:
            bad_match = True
        if start_date is not None and pd.to_datetime(date).date() < start_date:
            bad_match = True
        if end_date is not None and pd.to_datetime(date).date() > end_date:
            bad_match = True
        if bad_match is False:
            match_dict[date] = True

    # Brute force the various options to find a schedule that match all criteria at different times.
    jigsaw_dict = {}
    for date in match_dict:
        subdict = {}
        for index in combo_results:
            result_dict = combo_results[index][date]
            location = list(result_dict.keys())[0]
            options = list(result_dict[location].keys())
            subdict[location] = {'duration': criteria_dict[location], 'options': options}
        jigsaw_dict[date] = subdict

    output_dict = jigsaw_schedule(jigsaw_dict)

    # Cut down the dictionary to the given number of elements.
    return {k: output_dict[k] for k, _ in zip(output_dict, range(number))}


def jigsaw_schedule(options_dict: dict) -> dict:
    """Brute force a series of schedule options to find a set that matches."""

    result_dict = {}
    slots_template = {9: False, 9.25: False, 9.5: False, 9.75: False,
                      10: False, 10.25: False, 10.5: False, 10.75: False,
                      11: False, 11.25: False, 11.5: False, 11.75: False,
                      12: False, 12.25: False, 12.5: False, 12.75: False,
                      13: False, 13.25: False, 13.5: False, 13.75: False,
                      14: False, 14.25: False, 14.5: False, 14.75: False}

    for date in options_dict:
        locations = options_dict[date]
        option_lists = []
        for location in locations:
            location_options = []
            duration = locations[location]["duration"]
            options = locations[location]["options"]
            for option in options:
                location_options.append((location, option, duration))
            option_lists.append(location_options)
        permutations = list(itertools.product(*option_lists))
        match = None
        for perm in permutations:
            slots = slots_template.copy()
            error = False
            for item in perm:
                location, start, duration = item
                for slot in slots:
                    if slot >= start and slot < start + duration:
                        if slots[slot] is True:
                            error = True
                        else:
                            slots[slot] = True
            if error is False:
                match = perm
                break
        if match is not None:
            result_dict[date] = match
    return result_dict


def visualize_search_schedule(date, overlays: list[tuple] = []):
    """Create a schedule graphic that shows the time slots available on a given day."""

    locations = {
        "Jack Wood Hall": 1,
        "Eureka Theater": 2,
        "Learning Lab": 3,
        "Green Classroom": 4,
        "Yellow Classroom": 5,
        "Sudekum Planetarium": 6
    }

    day = config.schedule_dict[date]

    if len(day) == 0:
        return

    plt.clf()

    for location in day:
        for slot in day[location]:
            if day[location][slot] is True:
                plt.bar(locations[location], 0.25, bottom=slot, color=(0.5, 0.5, 0.5), zorder=10)

    # Add overlays
    for overlay in overlays:
        location, start, duration = overlay
        plt.bar(locations[location], duration, bottom=start, zorder=10)

    plt.title("Field Trip Availability: " + date, fontsize=20)
    plt.gca().invert_yaxis()
    plt.yticks([9, 9.5, 10, 10.5, 11, 11.5, 12, 12.5, 13, 13.5, 14, 14.5, 15],
               ["9 AM", "9:30 AM", "10 AM", "10:30 AM", "11 AM", "11:30 AM", "12 PM", "12:30 PM", "1 PM", "1:30 PM",
                "2 PM", "2:30 PM", "3 PM"])
    plt.xticks([1, 2, 3, 4, 5, 6],
               ["Jack Wood\nHall", "Eureka\nTheater", "Learning\nLab", "Green\nClassroom", "Yellow\nClassroom",
                "Sudekum\nPlanetarium"])
    plt.grid(which='major', axis='y', zorder=1)
    plt.gca().tick_params(right=True, top=True, labelright=True, labeltop=True, rotation=0)


    fig = plt.gcf()
    fig.set_size_inches(10, 8)
    plt.tight_layout()

    return plt.gcf()


def generate_schedule_from_browser(*args):
    """Use the date from the date picker to create a schedule"""
    display(fth_interface.browse_date_picker.value)

    fth_interface.browse_output.clear_output()
    with fth_interface.browse_output:
        display(generate_schedule_image(fth_interface.browse_date_picker.value))


def search_from_browser(*args):
    """Collect inputs from the find tab and search for a matching schedule slot."""

    if fth_interface.find_start_date_picker.value is not None:
        start_date = fth_interface.find_start_date_picker.value
    else:
        start_date = datetime.datetime.now().date()
    if fth_interface.find_end_date_picker.value is not None:
        end_date = fth_interface.find_end_date_picker.value
    else:
        end_date = (datetime.datetime.now() + pd.Timedelta('90 d')).date()
    if fth_interface.find_start_time_picker.value is not None:
        start_time = decimal_time(fth_interface.find_start_time_picker.value)
    else:
        start_time = 9.5
    if fth_interface.find_end_time_picker.value is not None:
        end_time = decimal_time(fth_interface.find_end_time_picker.value)
    else:
        end_time = 13.5

    criteria = []
    if fth_interface.find_programs_demo.value > 0:
        criteria.append(('Eureka Theater', fth_interface.find_programs_demo.value))
    if fth_interface.find_programs_lab.value > 0:
        criteria.append(('Learning Lab', fth_interface.find_programs_lab.value))
    if fth_interface.find_programs_planet.value > 0:
        criteria.append(('Sudekum Planetarium', fth_interface.find_programs_planet.value))
    if fth_interface.find_misc_lunch.value > 0:
        criteria.append(('Jack Wood Hall', fth_interface.find_misc_lunch.value))
    if fth_interface.find_misc_visitors.value > 0:
        criteria.append(('Admission', fth_interface.find_misc_visitors.value))

    results = combo_search(criteria,
                           start_date=start_date,
                           end_date=end_date,
                           start_time=start_time, end_time=end_time,
                           number=1)
    fth_interface.find_output.clear_output()
    with fth_interface.find_output:
        for date in results:
            overlays = results[date]
            if not isinstance(overlays, tuple):
                overlays = []
            display(visualize_search_schedule(date, overlays))

