# -*- coding: utf-8 -*-

import os

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


CATEGORIES = kickstarter_df['broader_category'].unique()
COLUMNS = ['launched_at', 'deadline', 'blurb', 'usd_pledged', 'state', 'spotlight', 'staff_pick', 'category_slug', 'backers_count', 'country']
# Picked with http://tristen.ca/hcl-picker/#/hlc/6/1.05/251C2A/E98F55
COLORS = ['#7DFB6D', '#C7B815', '#D4752E', '#C7583F']
STATES = ['successful', 'suspended', 'failed', 'canceled']

title = Div(text='<h1 style="text-align: center">Kickstarter Dashboard</h1>')

# This looks better than the multiselect widget
select = CheckboxButtonGroup(labels=CATEGORIES.tolist())


def get_scatterplot():
    hover = HoverTool(tooltips=[
        ("Name", "@name"),
        ("State", "@state"),
    ])

    p = figure(plot_height=200, y_axis_type='log', x_axis_type='datetime', tools=[hover])

    for color, state in zip(COLORS, STATES):
        df_by_state = kickstarter_df_sub[kickstarter_df_sub.state == state]
        data = {
            'x': df_by_state['created_at'],
            'y': df_by_state['usd_pledged'],
            'name': df_by_state['name'],
            'state': [state] * len(df_by_state),
        }
        source = ColumnDataSource(data=data)
        p.circle(x='x', y='y', line_color='white', fill_color=color, alpha=0.7, size=15, legend=state, source=source)
    p.xaxis.axis_label = 'Date'
    p.yaxis.axis_label = 'USD pledged'
    # See http://bokeh.pydata.org/en/latest/docs/reference/models/formatters.html for all formatters
    p.yaxis.formatter = NumeralTickFormatter(format='0a')
    p.legend.click_policy = 'hide'
    p.legend.location = "top_left"
    return p


stacked_barchart_df = (
    kickstarter_df['state'].groupby(kickstarter_df['broader_category'])
    .value_counts(normalize=False)
    .rename('count')
)


def get_barchart():
    data = {
        'categories': CATEGORIES,
    }

    # Sadly, I could not find a more efficient method to prepare a pandas array for a stacked bar chart
    for state in STATES[::-1]:
        data[state] = [stacked_barchart_df.loc[category, state] for category in CATEGORIES]

    source = ColumnDataSource(data=data)
    p = figure(x_range=CATEGORIES, plot_height=200)
    p.vbar_stack(STATES, x='categories', width=0.9, color=COLORS, source=source)
    return p


layout = column(title, select, get_scatterplot(), get_barchart(), sizing_mode='scale_width')

curdoc().add_root(layout)
