# -*- coding: utf-8 -*-

import os

from bokeh.core.properties import value
from bokeh.layouts import column
from bokeh.models import ColumnDataSource
from bokeh.models import HoverTool
from bokeh.models import NumeralTickFormatter
from bokeh.models.widgets import CheckboxButtonGroup
from bokeh.models.widgets import Div
from bokeh.plotting import figure
from bokeh.plotting import curdoc

import pandas as pd

##############################################################
#                                                            #
#             D  A  T  A     L  O  A  D  I  N  G             #
#                                                            #
##############################################################

kickstarter_df = pd.read_csv(os.path.join('..', 'kickstarter-cleaned.csv'), parse_dates=True)
kickstarter_df['broader_category'] = kickstarter_df['category_slug'].str.split('/').str.get(0)
kickstarter_df['created_at'] = pd.to_datetime(kickstarter_df['created_at'])

kickstarter_df_sub = kickstarter_df.sample(10000)


CATEGORIES = sorted(kickstarter_df['broader_category'].unique())
COLUMNS = ['launched_at', 'deadline', 'blurb', 'usd_pledged', 'state', 'spotlight', 'staff_pick', 'category_slug', 'backers_count', 'country']
# Picked with http://tristen.ca/hcl-picker/#/hlc/6/1.05/251C2A/E98F55
COLORS = ['#7DFB6D', '#C7B815', '#D4752E', '#C7583F'][::-1]
STATES = ['successful', 'suspended', 'failed', 'canceled'][::-1]

title = Div(text='<h1 style="text-align: center">Kickstarter Dashboard</h1>')



def filter_categories(indexes):
    if indexes == []:
        categories_filtered = CATEGORIES
    else:
        categories_filtered = [CATEGORIES[ind] for ind in indexes]
    update_num_categories_source(categories_filtered)
    update_usd_vs_date_source(categories_filtered)


# This looks better than the multiselect widget
select = CheckboxButtonGroup(labels=CATEGORIES)
select.on_click(filter_categories)


hover_usd_vs_date = HoverTool(tooltips=[
    ("Name", "@name"),
    ("State", "@state"),
])

p_usd_vs_date = figure(
    plot_height=200,
    y_axis_type='log',
    x_axis_type='datetime',
    tools=[hover_usd_vs_date, 'box_zoom', 'reset']
)

sources_usd_vs_date = {state: ColumnDataSource({
    'x': [],
    'y': [],
    'name': [],
    'state': [],
}) for state in STATES}


def update_usd_vs_date_source(categories=CATEGORIES):
    df_categories = kickstarter_df_sub[kickstarter_df_sub.broader_category.isin(categories)]
    for color, state in zip(COLORS, STATES):
        df_by_state = df_categories[df_categories.state == state]
        data = {
            'x': df_by_state['created_at'],
            'y': df_by_state['usd_pledged'],
            'name': df_by_state['name'],
            'state': [state] * len(df_by_state),
        }
        sources_usd_vs_date[state].data = data

update_usd_vs_date_source()

for color, state in zip(COLORS, STATES):
    p_usd_vs_date.circle(
        x='x',
        y='y',
        line_color='white',
        fill_color=color,
        alpha=0.7,
        size=15,
        legend=state,
        source=sources_usd_vs_date[state]
    )

p_usd_vs_date.xaxis.axis_label = 'Date'
p_usd_vs_date.yaxis.axis_label = 'USD pledged'
# See http://bokeh.pydata.org/en/latest/docs/reference/models/formatters.html for all formatters
p_usd_vs_date.yaxis.formatter = NumeralTickFormatter(format='0a')
p_usd_vs_date.legend.click_policy = 'hide'
p_usd_vs_date.legend.location = "top_left"


stacked_barchart_df = (
    kickstarter_df['state'].groupby(kickstarter_df['broader_category'])
    .value_counts(normalize=False)
    .rename('count')
)


# Can't seem to be able to put the state in there or the number of student in the tooltip though
hover_num_categories = HoverTool(tooltips=[
    ("Category", "@categories"),
])


def update_num_categories_source(categories=CATEGORIES):
    data = {
        'categories': categories,
    }

    # Sadly, I could not find a more efficient method to prepare a pandas array for a stacked bar chart
    for state in STATES:
        data[state] = [stacked_barchart_df.loc[category, state] for category in categories]
    source_num_categories.data = data


source_num_categories = ColumnDataSource()
update_num_categories_source()
p_num_categories = figure(x_range=CATEGORIES, plot_height=200, tools=[hover_num_categories])
p_num_categories.vbar_stack(
    STATES,
    x='categories',
    width=0.9,
    color=COLORS,
    source=source_num_categories,
    legend=[value(x) for x in STATES]
)
p_num_categories.yaxis.axis_label = 'Number of projects'


layout = column(title, select, p_usd_vs_date, p_num_categories, sizing_mode='scale_width')

curdoc().add_root(layout)
