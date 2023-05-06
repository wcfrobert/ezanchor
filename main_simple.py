import ezanchor as eza

# initialize equipment anchorage analysis
AHU4 = eza.equipment.Equipment(name="AHUsimple", Sds=1.85, Ip=1, h=44, z=44, ap=2.5, Rp=2, omega=2, 
                               weight=4000, CGz=50, load_combo="LRFD", use_omega=True)    

# add equipment footprint
AHU4.add_footprint(xo=0, yo=0, b=80, h=80)

# add anchors
AHU4.add_anchor_group(x0=5, y0=5, b=70, h=70, nx=2, ny=2, mode="p")

# visualize
fig = eza.plotter.preview(AHU4)

# solve
AHU4.solve(on_stilt=True)
fig3 = eza.plotter.plot_equipment(AHU4)
fig3.savefig("simple.png")

# export data
# AHU4.export_data()






