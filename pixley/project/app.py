# Import flask and pandas
from flask import Flask, render_template
import pandas as pd

# Import pyxley stuff
from pyxley import UILayout
from pyxley.filters import SelectButton
from pyxley.charts.mg import LineChart, Figure

# Read in the data and stack it, so that we can filter on columns
df = pd.read_csv("fitbit_data.csv")
sf = df.set_index("Date").stack().reset_index()
sf = sf.rename(columns={"level_1": "Data", 0: "value"})

# Make a UI
ui = UILayout(
    "FilterChart",
    "./static/bower_components/pyxley/build/pyxley.js",
    "component_id")

# Create the flask app
app = Flask(__name__)