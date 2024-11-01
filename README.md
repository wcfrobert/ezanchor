The following python package accompanies the SEAOC 2024 Convention paper: 

**"Critical Orientation of Seismic Force for Floor-Mounted Nonstructural Component Anchorage" (Wang et al, 2024)**

> The design of nonstructural component anchorage depends on both magnitude and direction of the seismic force (Fp), the latter of which is the subject of this paper. In recent years, research efforts led by ATC (2017) have greatly improved the estimation of seismic demand, resulting in a revamped Fp equation in the 2022 version of ASCE/SEI-7. As for direction, the code offers limited guidance and states that Fp shall be applied in the direction that produces the most critical load effects. Alternatively, the code permits the use of the empirical “100%-30%” directional combination like the one used in the seismic analysis of building structures. In this paper, we explore the surprisingly nuanced topic of critical load orientation for design of floor-mounted component anchorage. The study began with a rigorous definition of how the load effects – namely anchor shear and tension demand – are calculated, addressing variabilities in assumptions and methods in industry practice. The formulations were then incorporated into a standalone python package to streamline calculations. Using this program, a series of parametric studies were conducted to tackle the key question: “how does one determine the critical force direction for floor-mounted component anchorage?”. An example problem is provided at the end to illustrate the concepts discussed herein.
>

For additional details, please refer to the 2024 SEAOC Convention proceedings, accessible online.




<h1 align="center">
  <br>
  <img src="https://raw.githubusercontent.com/wcfrobert/ezanchor/master/docs/logo.png" alt="logo" style="zoom:80%;" />
  <br>
  Nonstructural Component Anchorage Calculator
  <br>
</h1>
<p align="center">
EZAnchor calculates anchorage demand of floor-mounted nonstructural components subjected to seismic forces at all possible orientations.
</p>








<div align="center">
  <img src="https://github.com/wcfrobert/ezanchor/blob/master/docs/pivot.gif?raw=true" alt="demogif2" style="width: 100%;" />
</div>


- [Introduction](#introduction)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
  * [Step 1: Initialize equipment object](#step-1--initialize-equipment-object)
  * [Step 2: Define equipment footprint](#step-2--define-equipment-footprint)
  * [Step 3: Add anchors](#step-3--add-anchors)
  * [Step 4: Solve](#step-4--solve)
  * [Step 5: Visualize](#step-5--visualize)
  * [Step 6: Export results to CSV](#step-6--export-results-to-csv)
- [Theoretical Background](#theoretical-background)
  * [Load Combination and Seismic Force (ASCE 7-16 Chapter 13)](#load-combination-and-seismic-force--asce-7-16-chapter-13-)
  * [Anchor Group Geometric Properties](#anchor-group-geometric-properties)
  * [Equipment Orientation](#equipment-orientation)
  * [Pivot Mode](#pivot-mode)
  * [Stilt Mode](#stilt-mode)
- [Notes and Assumptions](#notes-and-assumptions)
- [License](#license)



## Introduction

EZAnchor is a Python applet that performs nonstructural components seismic force (Fp) calculations per ASCE 7-16 Chapter 13, it then applies Fp in all possible directions (all 360 degrees) to determine the maximum shear and tension in the anchors holding the equipment in place.

<img src="https://raw.githubusercontent.com/wcfrobert/ezanchor/master/docs/FBD_COMBINED.png" alt="FBD" style="width:90%;" /> 


The technical background for equipment overturning calculation is quite simple. In most cases, some basic statics and free-body diagrams will get you close enough to a reasonable answer. What makes EZAnchor special are the following features.

* Can evaluate equipment with arbitrary number and arrangement of anchors
* Can evaluate equipment overturning in all possible orientations
* Can quickly calculate Ix, Iy, Ip, Ixy, principal moments of inertia of any anchor arrangement
* Can calculate effect of in-plane torsion (where anchor group centroid (COR) does not coincide with equipment COG)
* Can quickly switch between "Pivot Mode" or "Stilt Mode"

**Disclaimer:** this package is meant for <u>personal or educational purpose only</u>. I did not spent much time debugging all the edge cases and nothing is as robust as it could be. EZAnchor should not be used for commercial purpose of any kind!




## Quick Start

**Installation**

See "Installation" section below for more info. For casual users, simply use Anaconda Python, download this module, and open "main.py" in Spyder IDE.

**Using EZAnchor**

```python
# import ezanchor
import ezanchor as eza

# initialize equipment anchorage analysis
AHU4 = eza.equipment.Equipment(name="AHU4", Sds=1.85, Ip=1, h=44, z=44, ap=2.5, Rp=2, omega=2, weight=3500, CGz=64, CGx=40, CGy=85, load_combo="LRFD", use_omega=True)

# define equipment base footprint
AHU4.add_footprint(xo=0, yo=0, b=60, h=120)
AHU4.add_footprint(xo=60, yo=60, b=60, h=60)

# define anchors
AHU4.add_anchor_group(x0=5, y0=5, b=50, h=110, nx=2, ny=3, mode="p")
AHU4.add_anchor_group(x0=65, y0=65, b=50, h=50, nx=2, ny=2, mode="p")
AHU4.add_anchor(x=30, y=-5)
AHU4.add_anchor(x=30, y=125)
AHU4.add_anchor(x=90, y=55)
AHU4.add_anchor(x=90, y=125)

# solve
AHU4.solve(on_stilt=False)

# visualization options
fig1 = eza.plotter.preview(AHU4)
fig2 = eza.plotter.plot_anchor(AHU4, 2)
fig3 = eza.plotter.plot_equipment(AHU4)
fig1.show()
fig2.show()
fig3.show()

# export data
AHU4.export_data()
```



## Installation

**<u>Option 1: Anaconda Python Distribution</u>**

For the casual users, using the base Anaconda Python environment is recommened. This is by far the easiest method of installation. Users don't need to worry about dependency management and setting up virtual environments. The following open source packages are used in this project:

* Numpy
* Matplotlib

Installation procedure:

1. Download Anaconda python
2. Download this package (click the green "Code" button and download zip file)
3. Open and run "main.py" in Anaconda's Spyder IDE. Make sure working directory is correctly configured.

**<u>Option 2: Command Prompt + Plain Python</u>**

1. Download this project to a folder of your choosing
    ```
    git clone https://github.com/wcfrobert/ezanchor.git
    ```
2. Change directory into where you downloaded ezanchor
    ```
    cd ezanchor
    ```
3. Create virtual environment
    ```
    py -m venv venv
    ```
4. Activate virtual environment
    ```
    venv\Scripts\activate
    ```
5. Install requirements
    ```
    pip install -r requirements.txt
    ```
6. run ezanchor
    ```
    py main.py
    ```

Note that pip install is available.

```
pip install ezanchor
```




## Usage

### Step 1: Initialize equipment object

EZAnchor has an object-oriented design that should be quite easy to understand. Start by instantiating an "equipment" object. All your results and equipment information will be stored here. The constructor takes in the following parameters.

`Equipment.__init__(name, Sds, Ip, h, z, ap, Rp, omega, weight, CGz, CGx="auto", CGy="auto", load_combo="LRFD", use_omega=True)` creates an equipment analysis object. Parameters to pass to constructor:

* name: string
  * Provide a name to the equipment
* Sds: float
  * Short period spectra parameter (ASCE 7-16)
* Ip: float
  * Equipment importance factor (ASCE 7-16)
* h: float
  * Building height
* z: float
  * Height where equipment is attached to the building
* ap: float
  * Component amplification factor (ASCE 7-16)
* Rp: float
  * Component response factor (ASCE 7-16)
* omega: float
  * Component overstrength factor (ASCE 7-16)
* weight: float
  * Equipment weight
* CGz: float
  * Equipment center of mass above ground
* CGx: float or string (optional)
  * Equipment center of mass in plan in X direction. Default = "auto"
  * If equal to "auto", set in-plan COG = COR, no in-plane torsion.
  * +X points to the right
* CGy: float or string (optional)
  * Equipment center of mass in plan in Y direction. Default = "auto"
  * If equal to "auto", set in-plan COG = COR, no in-plane torsion.
  * +Y points up
* load_combo: string (optional)
  * Define which load combination to use. "LRFD" or "ASD". Default = "LRFD"
* use_omega: boolean (optional)
  * Define is overstrength load combination should be used. Default = True
  * Omega factor should be applied to equipment anchored to concrete

```python
# import ezanchor
import ezanchor as eza

# initialize equipment anchorage analysis
AHU4 = eza.equipment.Equipment(name="AHU4", Sds=1.85, Ip=1, h=44, z=44, ap=2.5, Rp=2, omega=2, weight=3500, CGz=64, CGx=40, CGy=85, load_combo="LRFD", use_omega=True)
```



### Step 2: Define equipment footprint

`Equipment.add_footprint(xo, yo, b, h)` adds a rectangular footprint to the equipment.

* xo: float
  * x coordinate of bottom left vertex
* yo: float
  * y coordinate of the bottom left vertex
* b: float
  * footprint width (dx)
* h: float
  * footprint height (dy)

Multiple footprints can be added and they can overlap. In the backend, each footprint acts as a bounding box which allows EZAnchor to determine the point of pivot at all orientations. In "stilt mode", effect of footprint is ignored.

```python 
# add footprint at origin with width of 60 and height of 120
AHU4.add_footprint(xo=0, yo=0, b=60, h=120)
# add another footprint at (60,60) with width of 60 and height of 60
AHU4.add_footprint(xo=60, yo=60, b=60, h=60)
```



### Step 3: Add anchors

There are two ways to add anchors to your equipment:

1. You may do so one-by-one using `.add_anchor()`
2. Or you may add a rectangular array using `.add_anchor_group()`

`Equipment.add_anchor(x, y)` add an anchor to the equipment:

* x: float
  * x coordinate of anchor (inches)
* y: float
  * y coordinate of anchor (inches)

```python
# add a single anchor at coordinate (30,-5)
AHU4.add_anchor(x=30, y=-5)
```



`Equipment.add_anchor_group(x0, y0, b, h, nx, ny, mode)` adds an rectangular array of anchors to equipment.

* x0: float
  * Bottom left corner of anchor array. X coordinate.
* y0: float
  * Bottom left corner of anchor array. Y coordinate.
* b: float
  * Anchor array width
* h: float
  * Anchor array height
* nx: int
  * number of columns in array
* ny: int
  * number of rows in array
* mode: string
  * "p" for perimeter mode. No interior anchors
  * "f" for filled mode. Full array. See figure below for clarification

```python
# adds a 2x3 anchor array at (5,5) 50 in width, 110 in height
AHU4.add_anchor_group(x0=5, y0=5, b=50, h=110, nx=2, ny=3, mode="p")
```



### Step 4: Solve

`Equipment.solve(on_stilt = False)` starts analysis routine.

* on_stilt: boolean (optional)
  * Choose between stilt mode or pivot mode. Default = False = pivot mode

Refer to "Theoretical Background" section for how pivot mode and stilt mode differs.

```python
# solve
AHU4.solve(on_stilt=False)
```



### Step 5: Visualize

There are currently three visualization options:

1. `ezanchor.plotter.preview()` - to show footprint and anchor arrangement. Can be ran before analyzing.
2. `ezanchor.plotter.plot_anchor()` - show tension and shear demand in a specific anchor
3. `ezanchor.plotter.plot_equipment()` - to show tension and shear demand envelope curve + other info.



`ezanchor.plotter.preview(equipment)` preview anchor and footprint arrangement.

* equipment: ezanchor equipment object
  * pass in your equipment analysis object

```python
fig1 = eza.plotter.preview(AHU4)
```



<img src="https://raw.githubusercontent.com/wcfrobert/ezanchor/master/docs/preview.png" alt="visual1" style="zoom:80%;" />



`ezanchor.plotter.plot_anchor(equipment, anchorID)` plot tension and shear in a specific anchor.

* equipment: ezanchor equipment object
  * pass in your equipment analysis object
* anchorID: int
  * specific anchor ID (use preview plot to see which anchor you are interested in)

```python
fig2 = eza.plotter.plot_anchor(AHU4, 2)
```



<img src="https://raw.githubusercontent.com/wcfrobert/ezanchor/master/docs/anchor.png" alt="visual2" style="zoom:80%;" />



`ezanchor.plotter.plot_equipment(equipment)` plot tension and shear evenlope curve and other information. 

* equipment: ezanchor equipment object
  * pass in your equipment analysis object

```python
fig3 = eza.plotter.plot_equipment(AHU4)
```



<img src="https://raw.githubusercontent.com/wcfrobert/ezanchor/master/docs/equip.png" alt="visual3" style="zoom:80%;" />



### Step 6: Export results to CSV

`Equipment.export_data()` export results to csv file in the current working directory.

EZAnchor will create a folder called {Equipment.name}_run_results. Within the folder you will see two csv files.

* AHU4_anchors.csv - results for individual anchors
* AHU4_equipment.csv - results for equipment

Note that if {Equipment.name}_run_results folder already exists, EZAnchor will create another folder by appending an integer to the end of the folder name (e.g. AHU4_run_results1).

```python
AHU4.export_data()
```




## Notes and Assumptions

<img src="https://raw.githubusercontent.com/wcfrobert/ezanchor/master/docs/coordinate.png" alt="coordinate" style="zoom:80%;" />

* Default coordinate system (X, Y, Z): 
  * Z is the vertical axis (Elevation)
  * X and Y are the axes on plan. +X points to the right, +Y points up
* Sign convention:
  * At degree 0, seismic load is applied in the +Y direction (upward)
  * Sign of moment follows the right-hand rule. Mz is positive counter-clockwise
  * Compression is negative (-), tension is positive (+)
* EZAnchor is agnostic when it comes to unit. Please ensure your input is consistent. I prefer to use lbs and inches




## License

MIT License

Copyright (c) 2023 Robert Wang

