import ezanchor as eza

# initialize equipment anchorage analysis
AHU4 = eza.equipment.Equipment(name="AHU4", Sds=1.85, Ip=1, h=44, z=44, ap=2.5, Rp=2, omega=2, 
                               weight=3500, CGz=64, CGx=40, CGy=85, load_combo="LRFD", use_omega=True)

# define base footprint
AHU4.add_footprint(xo=0, yo=0, b=60, h=120)
AHU4.add_footprint(xo=60, yo=60, b=60, h=60)

# define anchors
AHU4.add_anchor_group(x0=5, y0=5, b=50, h=110, nx=2, ny=3, mode="p")
AHU4.add_anchor_group(x0=65, y0=65, b=50, h=50, nx=2, ny=2, mode="p")
AHU4.add_anchor(x=30, y=-5)
AHU4.add_anchor(x=30, y=125)
AHU4.add_anchor(x=90, y=55)
AHU4.add_anchor(x=90, y=125)

# solveW
AHU4.solve(on_stilt=True)

# visualization options
fig = eza.plotter.preview(AHU4)
fig3 = eza.plotter.plot_equipment(AHU4)
fig2 = eza.plotter.plot_anchor(AHU4, 2)

# export data
#AHU4.export_data()
