<h1 align="center">
  <br>
  <img src="https://raw.githubusercontent.com/wcfrobert/ezanchor/master/docs/logo.png" alt="logo" style="zoom:80%;" />
  <br>
  Nonstructural Component Anchorage Calculator
  <br>
</h1>
<p align="center">
EZAnchor evaluates overturning of nonstructural components due to seismic excitation at all orientations for critical anchor shear/tension demands.
</p>







<div align="center">
  <img src="https://raw.githubusercontent.com/wcfrobert/ezanchor/master/docs/pivot.gif" alt="demogif2" style="width: 100%;" />
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
* Quick and easy-to-use

The impetus for this package came from a lengthy technical discussion at work. I wanted to resolve two questions that's been gnawing at me for months:

1. Should overturning be evaluated in all possible orientations? Is it worth the effort?
	- I don't think so. For simple cases, you really don't gain all that much insight with the additional effort; however, there are situations where I think the additional rigor can be justified. For instance:
	  - equipment is on feet (must use stilt-mode)
	  - irregular equipment shape (like a L or T)
	  - large eccentricity between center of mass (of equipment), and center of resistance (of anchors) which creates significant torsion effects
	- With EZAnchor, you can evaluate all possible overturning orientations, for anchor group of arbitrary complexity, and get results in seconds. This was extremely time-consuming, if not impossible, to do by hand or spreadsheet.
2. Is it appropriate to use the classical mechanics equation (e.g. P/N + My/I) even when an equipment is bearing on the floor?
	- No, those equations are only valid if equipment is standing on feet because anchor is assumed to take compression (see the free-body diagrams above). If blindly applied, the results tend to be overly conservative, not to mention erroneous from the outset. 
	- Furthermore, even when they are appropriate, they are often incorrectly applied when anchor group is more complicated (not rectangular). Linear combination of moments in two orthogonal directions MUST be about the anchor group's principal axes of inertia. Meaning you'd first have to 1.) find anchor group centroid and moment of inertias, 2.) use those Mohr's circle equations, 3.) rotate all coordinates to the principal axes, 4.) find new centroid and moment of inertia and do all calculation at this rotated geometry.

The current standard of practice is to perform equipment anchorage calculations in the two most obvious orthogonal directions. I personally think this is good enough. However, ASCE 7-16 13.3.1.1 states that for "vertically cantilevered systems", Fp shall be assumed to act in **any** horizontal direction. Since all floor-mounted equipment can be considered "vertically cantilevered", many engineers and authority-having jurisdictions are pushing for finding the "critical angle" of overturning. I don't think this is trivial.

In "Pivot Mode" where point of overturning is about the edge of an equipment, the tension demand at a particular anchor is NOT the linear combination of results from two arbitrarily selected basis (that can be conveniently added together). In "Stilt Mode", we must be cognizant of the fact that critical overturning orientation (where max tension occurs) usually does not align with the minimum principal axis of inertia (it's usually 10 to 45 degrees offset from it).

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



## Theoretical Background


### Load Combination and Seismic Force (ASCE 7-16 Chapter 13)

The component seismic design force can be calculated as

$$F_p = 0.4 (\frac{a_p}{R_p / I_p}) (1 + \frac{2z}{h}) S_{DS} W_p$$

subject to the following floor and ceiling values.

$$F_{pmax} = 1.6 S_{DS} I_p W_p$$

$$F_{pmin} = 0.3 S_{DS} I_p W_p$$

where:

* $a_p$ is the component amplification factor (which accounts for flexibility of equipment and resulting dynamic amplification. 1.0 for rigid, 2.5 for highly flexible)
* $R_p$ is the component response modification factor (which accounts for equipment's inherent ductility)
* $W_p$ is the component weight
* $I_p$ is the component importance factor
* $z$ is the height in elevation of component's point of attachment
* $h$ is the height of the building

The z/h ratio essentially converts PGA to PFA and is equal to 1.0 at ground and 3.0 at the roof. $F_p$ force shall be applied at component's center of gravity. Component parameters ($a_p, R_p, \Omega_p$) can be found in ASCE 7-16.

* Mechanical and electrical: Table 13.6-1
* Architectural: Table 13.5-1

Depending on the load combination type ("ASD" or "LRFD"), the following adjustments are made to the seismic force and equipment weight.

* For LRFD:
  * $(0.9 - 0.2 S_{ds}) \times W_p$
  * $1.0F_p$
* For ASD:
  * $(0.6 - (0.7)(0.2)S_{ds}) \times W_p$
  * $0.7F_p$

For analyses requiring overstrength such as equipment anchorage into concrete, replace $F_p$ with $E_{mh}$ where:

$$ E_{mh} = \Omega_p \times F_p $$



### Anchor Group Geometric Properties

Let $(x_i, y_i)$ be the anchor coordinates. For an anchor group:

The center of gravity (or center of resistance) is:

$$\bar{x} = \frac{x_i}{\sum x_i}$$

$$\bar{y} = \frac{y_i}{\sum y_i}$$

The moment of inertia about x and y axis is:

$$I_x = \sum (y_i - \bar{y})^2$$

$$I_y = \sum (x_i - \bar{x})^2$$

The polar moment of inertia is:

$$I_z = I_x + I_y$$

The product moment of inertia (which is zero at principal axis) is:

$$I_xy = \sum (x_i - \bar{x})(y_i - \bar{y})$$

From the above parameters, we can use the Mohr's circle equations for moment of inertia to get max/min moment of inertia and the associated rotation to principal axes:

$$I_{max} = \frac{I_x + I_y}{2} + \sqrt{((I_x - I_y)/2)^2 + (I_{xy})^2}$$

$$I_{max} = \frac{I_x + I_y}{2} - \sqrt{((I_x - I_y)/2)^2 + (I_{xy})^2}$$

$$\theta = \arctan{\left( \frac{I_{xy}}{(I_x - I_y)/2} \right ) } / 2$$



### Equipment Orientation

All anchors and footprints have a specific x,y coordinates (e.g. anchor.x, anchor.y). Rotating the equipment is simply a matter of applying a rotational transformation matrix.

let the original coordinate be as a position vector:

$$\bar{r}=\{ x,y \}$$

The new coordinate after rotation is:

$$\bar{r'}=\{ x',y'\}$$

The relationship between the two is:

$$\bar{r'}=[T] \bar{r}$$

Where the transformation matrix is defined as:

$$
[T] = 
\begin{bmatrix}
cos(\theta) & -sin(\theta)\\
sin(\theta) & cos(\theta)
\end{bmatrix}\\
$$

The user defines equipment orientation at deg = 0. The angle $\theta$ is rotation <u>counter-clockwise</u>.

### Pivot Mode

In pivot mode, the seismic force (Fp) is always applied in the +Y direction. It's the equipment geometry that is being rotated.


<div align="center">
  <img src="https://raw.githubusercontent.com/wcfrobert/ezanchor/master/docs/pivot.gif" alt="demogif1" style="width: 80%;" />
</div>

<div align="center">
  <img src="https://raw.githubusercontent.com/wcfrobert/ezanchor/master/docs/FBD1.png" alt="FBD1" style="width:40%;" />
</div>


**Tension Demand**

0.) This methodology involves finding a point of pivot at the edge of the equipment footprint, then calculating anchor tension using the rigid base assumption. EZAnchor determines the point of pivot as the topmost bounding box point.

$$y_{pivot} = max(y)$$

1.) Find the depth from pivot point for all anchors:

$$d_i = y_{pivot} - y_i$$

2.) Calculate overturning moment due to seismic force (see section above for required load combination factors). ($CG_z$ is equipment center of mass above ground).

$$M_{ot} = F_p \times CG_z$$

3.) Calculate resisting moment from equipment self weight (see section above for required load combination factors): ($y_{cog}$ is y-coordinate of equipment center of mass).

$$M_r = W_p \times (y_{pivot} - y_{cog}) $$

4.) Calculate net moment. If negative, seismic force is small enough for the equipment to remain stable without any anchorage (i.e. T = 0)

$$M_{net} = M_{ot} - M_r$$

5.) Anchors are indexed i, i+1, ... N-1, N. Where i is the anchor closest to pivot, and N is anchor furthest from pivot. The tension demand in the anchor furthest from pivot is equal to the following (from moment equilibrium about pivot):

$$T_{max} = T_{N} = \frac{M_{net}}{\sum d_i^2 /d_N}$$

6.) For the other anchors:

$$T_i = \frac{d_i}{d_N} \times T_{max}$$

Note that in-plane torsion due to COG and COR offset does not affect tension demand in pivot mode. In fact, we did not need to find any geometric properties of anchor groups for they are not required here.

IMPORTANT ASSUMPTION: Please note that an important simplification is made here which is very typical for equpment anchorage calculations. Refering to the free-body diagram above, notice how the concrete bearing reaction (C) is represented as a concentrated point load, rather than a distributed stress profile (e.g. rectangular stress block). In essence, rather than meshing with concrete fibers and finding the exact neutral axis depth for every orientation (which takes significantly more memory and compute), we recognize that the depth of concrete stress block is always small relative to the equipment footprint, and that the phenomenon of overturning involves the edge of the equipment. In other words, although it is more exact to mesh and find the exact depth of neutral axis, the change to the final answer is insignificant. That being said, the user should ensure that the footprint of the equipment is large enough relative to neutral axis depth.



**Shear Demand**

0.) The total shear demand at each anchor can be separated into two components.

$$V_{total} = V_{direct} + V_{torsion}$$

1.) Direct shear  is easy to determine

$$v_{dx} = 0$$

$$v_{dy}=-\frac{F_p}{N_{anchor}}$$

2.) In pivot mode, eccentricity is always in the x-direction because seismic force (Fp) is always applied in the +Y direction.

$$ecc_x = x_{cog} - x_{cor}$$

$$ecc_y = 0$$

3.) Torsion caused by this offset is equal to:

$$torsion = F_p \times ecc_x$$

4.) Torsional shear is calculated as follows for anchor i:

$$v_{tx} = \frac{torsion \times (y_i - y_{cor})}{I_z}$$

$$v_{ty} = 0$$

5.) Total shear is equal to:

$$V_{total} = \sqrt{(v_{dx} +v_{tx})^2 + (v_{dy} + v_{ty})^2}$$





### Stilt Mode

In stilt mode, the equipment geometry does not change, instead we are rotating the force/moment vector. Please note that 0th degree refers to Fp being applied in the +Y direction. Angle $\theta$ is measured from the vertical +Y axis.



<div align="center">
  <img src="https://raw.githubusercontent.com/wcfrobert/ezanchor/master/docs/stilt.gif" alt="demogif2" style="width: 80%;" />
</div>


<div align="center">
  <img src="https://raw.githubusercontent.com/wcfrobert/ezanchor/master/docs/FBD2.png" alt="FBD2" style="width:40%;" />
</div>


**Tension Demand**

0.) This methodology is appropriate for equipment standing on feet, as the anchors are assumed to take compression. The procedure is essentially equivalent to $(P/A) + (M_x y/I_x) + (M_y x /I_y)$ for sections. First step is to rotate the equipment to the principal axes geometry.

1.) Overturning moment contribution due to self-weight ($W_p$ is negative):

$$M_{wx} = W_p (y_{cog} - y_{cor})$$

$$M_{wy} = -W_p (x_{cog} - x_{cor})$$

2.) Overturning moment contribution due to seismic force:

$$M_{otx}= -F_p cos(\theta) \times CG_z$$

$$M_{oty}= -F_p sin(\theta) \times CG_z$$

3.) Tension demand due to axial self-weight for all anchors

$$T_{axial} = -W_p/N_{anchor}$$

4.) Tension demand due to overturning moment for anchor i:

$$T_{tx} = \frac{(M_{wx}+M_{otx})(y_i - y_{cor})}{I_x}$$

$$T_{ty} = -\frac{(M_{wy}+M_{oty})(x_i - x_{cor})}{I_y}$$

5.) Total tension demand:

$$T_{total} = T_{axial} + T_{tx} + T_{ty}$$



**Shear Demand**

0.) Unlike pivot mode, we first need to determine the component of seismic force vectors:

$$F_{px} = - F_p \times sin(\theta)$$

$$F_{py} = F_p \times cos(\theta)$$

1.) Direct shear demand is easy to determine

$$v_{dx} =-\frac{F_{px}}{N_{anchor}}$$

$$v_{dy} =-\frac{F_{py}}{N_{anchor}}$$

2.) Eccentricity is calculated as shown:

$$ecc_x = x_{cog} - x_{cor}$$

$$ecc_y = -(y_{cog} - y_{cor})$$

3.) Torsion caused by this offset is equal to:

$$torsion = F_{py} \times ecc_x + F_{px} \times ecc_y$$

4.) Torsional shear is calculated as follows for anchor i:

$$v_{tx} = \frac{torsion \times (y_i - y_{cor})}{I_z}$$

$$v_{ty} = torsion \times (x_i - x_{cor})$$

5.) Total shear is equal to:

$$V_{total} = \sqrt{(v_{dx} +v_{tx})^2 + (v_{dy} + v_{ty})^2}$$






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

