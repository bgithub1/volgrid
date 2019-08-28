# volgrid:
___
* Compute daily implied volatility surfaces, for common commodity contracts.
* Display those surfaces within a single page Dash web app.
___



The volgrid project contains a Plotly Dash app, that displays daily volatily surface graphs for specfic commodities contracts, for a specific sets of days.  The business logic that computes volatility surfaces resides in a module called ```create_voltables.py```.  The dash app that displays the resulting graphs as a single page web app resides in the ```__init__.py``` method of the volgrid package, in the volgrid project.

### How it works:
Option settlement data from barchart (via a $21/month subscription) allows you to obtain
implied volatilities for any options contract that trades on the CME, LME or ICE.  Then,
using standard spline interpolation libraries, daily volatilities for normalized ranges of 
strikes are computed, and displayed via Plotly graphs, and Dash html components.

Another open source project, ```barchartacs```, creates a postgres database of options/underlying settlements, after those settlements are downloaded from barchart.

Option implied volatility calculations are executed in the module option_models.py.


### Quick Start
The project comes with several an options settlement csv files that were previously extracted from the postgres database.  Thus, you don't have to start a postgres database to run the project with these settlements.

To run the Dash App that displays volatility skew graphs, run the main in ```volgrid/volgrid/__init__.py``` as follows:

```
cd volgrid/volgrid
python3 __init__.py
```

This will launch a web app that can be accessed by entering 127.0.0.1:8500 into your browser address bar.



