# Flask-ChartJS-Manager

Flask-ChartJS-Manager _(from now on **FCM**)_ provides a simple interface to use ChartJS javascript library with Flask.

```{warning}
🚧 This package is under heavy development..
```

## Installation

Install the extension with pip:

```bash
pip install flask-chartjs-manager
```

Install with poetry:

```bash
uv add flask-chartjs-manager
```

## Usage

Once installed the **FCM** is easy to use. Let's walk through setting up a basic application. Also please note that this is a very basic guide: we will be taking shortcuts here that you should never take in a real application.

To begin we'll set up a Flask app:

```python
from flask import Flask

app = Flask(__name__)
```

### Setting up extension

**FCM** works via a ChartJS object. To kick things off, we'll set up the `chartjs` by instantiating it and telling it about our Flask app:

```python
from flask_chartjs import ChartJS

chartjs = ChartJSManager()
chartjs.init_app(app)
```

This will make available the `chartjs` object into the templates context so you could load the javascript package easily.
You can configure a `CHARTJS_LOCAL_PATH` to add a custom location for the package

```html
<head>
  {{ chartjs.load() }}
</head>
```

### Creating a chart

Now we will construct a basic chart. For this you have to import `Chart` and `DataSet` objects in order to create a new chart.

```python
from flask_chartjs import Chart, DataSet
from flask import render_template

@app.get('/chart-example')
def chart_example():

    chart = Chart('income-outcome', 'bar') # Requires at least an ID and a chart type.

    dataset_income = DataSet('Income', [100,200,300])
    dataset_outcome = DataSet('OutCome', [50,100,150])

    chart.data.add_labels('jan', 'feb', 'mar')
    chart.data.add_dataset(dataset_income)
    chart.data.add_dataset(dataset_outcome)

    return render_template('path/to/template.html', my_chart=chart)

```

### Rendering the chart

Once created you can pass the `Chart` object to render_template and use it likewise.

```html
<!-- chartjs.load() must be called before this line -->
<div class="my-classes">{{ chartjs.render(my_chart) }}</div>
```

## Changelog 0.1.11

Added new options to personalize using the full power of the ChartJS library. Now you can limit the python code to add the dataset itself and let
the configuration and further customization to the actual template level. See the next example.
If you add a `%` in front of a value its assumed to be a javascript variable.
You have the especial kwarg `datasets` to access directly to the datasets options, as you can observe in the next example. The key is the dataset index.

```html
<!-- load_chartjs() must be called before this line -->
<script>
  function addDollarSign(value, index, ticks) {
    return "$" + value.toLocaleString();
  }
</script>
<div class="my-classes">
  {{ chartjs.render(chart, options={ 'datasets': { 'line': { 'tension': 0.4,
  'fill': true, } }, 'elements': { 'point': { 'pointStyle': 'circle', 'radius':
  5, 'hitRadius': 5, 'hoverRadius': 5, 'borderWidth': 5, } }, 'scales': { 'y': {
  'ticks': { 'callback': '%addDollarSign' } } } }, datasets={ 0: {
  'borderColor': 'rgba(20, 184, 166, 0.8)', 'backgroundColor': 'rgba(20, 184,
  166, 0.4)', }, 1: { 'borderColor': 'rgba(239, 68, 68, 0.8)',
  'backgroundColor': 'rgba(239, 68, 68, 0.4)', }, }) }}
</div>
```
