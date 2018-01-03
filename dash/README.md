# Kickstarter Dashboard in Dash

This dashboard contains three widgets:

- A multi selection box to pick the category of the kickstarter projects
- A graph showing the states of the projects and the money invested in them relative to time
- A breakdown of these projects grouped by category

The events linking those widgets are:

- Multi selection box -> scatter plot
- Multi selection box -> bar graph
- Selection on the scatter plot -> bar graph

Run the example locally using `python app.py` (Python 3).
