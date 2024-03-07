# Standard packages
import datetime

# Third-party packages
from ipywidgets import widgets
from IPython.display import display, HTML, FileLink

# Project packages
import config


user_label = widgets.Label('Username:', layout=widgets.Layout(width='75px'))
user_field = widgets.Text(layout=widgets.Layout(width='175px'))
pw_field = widgets.Password(layout=widgets.Layout(width='175px'))
pw_submit_button = widgets.Button(description='Login',layout=widgets.Layout(width='75px'))
pw_status = widgets.Label('', layout=widgets.Layout(width='150px'))
pw_label = widgets.Label('Password:', layout=widgets.Layout(width='75px'))

pw_login_box = widgets.VBox([
    widgets.HBox([user_label, user_field],
                layout=widgets.Layout(width='100%',display='inline-flex',flex_flow='row wrap')),
    widgets.HBox([pw_label,pw_field],
                 layout=widgets.Layout(width='100%',display='inline-flex',flex_flow='row wrap')),
    widgets.HBox([ pw_submit_button, pw_status])
])

login_output = widgets.Output()

browse_date_picker = widgets.DatePicker()
browse_select_date_button = widgets.Button(description="Select")

browse_date_box = widgets.HBox([browse_date_picker,browse_select_date_button])

browse_output = widgets.Output(layout={'border': '1px solid black'})

group_search_field = widgets.Text(placeholder='Group name')

group_search_button = widgets.Button(description="Search")

group_search_box = widgets.HBox([group_search_field, group_search_button])

group_search_output = widgets.Output(layout={'border': '1px solid black'})

find_start_date_picker = widgets.DatePicker(description="Start date")
find_end_date_picker = widgets.DatePicker(description="End date")
find_date_box = widgets.HBox([find_start_date_picker,find_end_date_picker])
find_start_time_picker = widgets.Dropdown(
    options=[
        ('9 AM', datetime.time(9, 0)),
        ('9:30 AM', datetime.time(9, 30)),
        ('10:00 AM', datetime.time(10, 0)),
        ('10:30 AM', datetime.time(10, 30)),
        ('11:00 AM', datetime.time(11, 0)),
        ('11:30 AM', datetime.time(11, 30)),
        ('12:00 PM', datetime.time(12, 0)),
        ('12:30 PM', datetime.time(12, 30)),
        ('1:00 PM', datetime.time(13, 0)),
        ('1:30 PM', datetime.time(13, 30)),
        ('2:00 PM', datetime.time(14, 0)),
        ('2:30 PM', datetime.time(14, 30))
             ],
    value=datetime.time(9, 30),
    description='Arrival',
)
find_end_time_picker = widgets.Dropdown(
    options=[
        ('10:00 AM', datetime.time(10, 0)),
        ('10:30 AM', datetime.time(10, 30)),
        ('11:00 AM', datetime.time(11, 0)),
        ('11:30 AM', datetime.time(11, 30)),
        ('12:00 PM', datetime.time(12, 0)),
        ('12:30 PM', datetime.time(12, 30)),
        ('1:00 PM', datetime.time(13, 0)),
        ('1:30 PM', datetime.time(13, 30)),
        ('2:00 PM', datetime.time(14, 0)),
        ('2:30 PM', datetime.time(14, 30)),
        ('3:00 PM', datetime.time(15, 0))
             ],
    value=datetime.time(13, 0),
    description='Departure',
)
find_time_box = widgets.HBox([find_start_time_picker,find_end_time_picker])
find_datetime_box = widgets.VBox([find_date_box, find_time_box])

find_programs_demo = widgets.Dropdown(
    options=[('No', 0), ('Short', 0.5), ('Long', 1)],
    value=0,
    description='Demo',
)
find_programs_lab = widgets.Dropdown(
    options=[('No', 0), ('Short', 0.5), ('Long', 1)],
    value=0,
    description='Lab',
)
find_programs_planet = widgets.Dropdown(
    options=[('No', 0), ('Yes', 0.5)],
    value=0,
    description='Planetarium',
)
find_programs_box = widgets.HBox([find_programs_demo, find_programs_lab, find_programs_planet])

find_misc_lunch = widgets.Dropdown(
    options=[('No', 0), ('Yes', 0.5)],
    value=0,
    description='Lunch',
)
find_misc_visitors = widgets.IntText(description="Visitors")
find_misc_box = widgets.HBox([find_misc_lunch, find_misc_visitors])

find_search = widgets.Button(description="Search")

find_output = widgets.Output(layout={'border': '1px solid black'})


interface = widgets.Tab(layout=widgets.Layout(width="500px"))
interface.children = [
     widgets.VBox([browse_date_box, browse_output]),
     widgets.VBox([group_search_box, group_search_output]),
     widgets.VBox([find_datetime_box, find_programs_box, find_misc_box, find_search, find_output])
]
interface.titles = ["Schedule browser", "Group finder", "Booking helper"]

main_output = widgets.Output()
