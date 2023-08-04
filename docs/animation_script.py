import ezanchor as eza
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import math
import os
plt.ioff()


def main():
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
    
    # solve
    AHU4.solve(on_stilt=True)
    
    # animation
    N = len(AHU4.orientations)-1
    for i in range(N):
        print(i)
        stop_step = i + 1
        degree_slice = AHU4.orientations[:stop_step]
        
        fig = animate_equipment(AHU4, degree_slice)
        filename = "anim_stilt/frame{:04d}.png".format(i)
        png_path = os.path.join(os.getcwd(), filename)
        fig.savefig(png_path, dpi=100)




def animate_equipment(equip, degree_slice):
    """plot tension and shear demand envelope for the entire equipment"""
    # set up figure
    fig, axs = plt.subplots(2, 2, width_ratios = [1,3], height_ratios = [1,1])
    fig.set_size_inches(16,9)
    
    tension = []
    shear = []
    t_anc = []
    v_anc = []
    for deg in degree_slice:
        tension.append(equip.T_max[deg])
        shear.append(equip.V_max[deg])
        t_anc.append(equip.T_crit_anchor[deg])
        v_anc.append(equip.V_crit_anchor[deg])
    tmax_idx = len(degree_slice)-1
    vmax_idx = len(degree_slice)-1
    
    # plot tension and shear envelope
    axs[0][1].plot(degree_slice,tension,linewidth=3,color="red")
    axs[1][1].plot(degree_slice,shear,linewidth=3,color="red")
    
    # plot individual anchor lines
    for anchor in equip.anchor_list:
        t = []
        v = []
        for deg in degree_slice:
            t.append(anchor.Ttotal_360[deg])
            v.append(anchor.Vtotal_360[deg])
        if anchor.tag == t_anc[tmax_idx]:
            axs[0][1].plot(degree_slice,t,linewidth=2,color="blue")
        else:
            axs[0][1].plot(degree_slice,t,linewidth=1,color="skyblue")
        
        if anchor.tag == v_anc[vmax_idx]:
            axs[1][1].plot(degree_slice,v,linewidth=2,color="blue")
        else:
            axs[1][1].plot(degree_slice,v,linewidth=1,color="skyblue")
    
    # plot marker and annotation at max point
    axs[0][1].plot(degree_slice[tmax_idx],tension[tmax_idx],color="purple", markersize=8, marker="o")
    axs[1][1].plot(degree_slice[vmax_idx],shear[vmax_idx],color="purple", markersize=8, marker="o")
    
    # plot equipment footprint previews
    deg_t = degree_slice[tmax_idx]
    anc_t = t_anc[tmax_idx]
    deg_v = degree_slice[vmax_idx]
    anc_v = v_anc[vmax_idx]
    max_y= max([a[1] for a in equip.bounding_points])
    arrow_length = 0.2*max_y
    dx_t = 0
    dx_v = 0
    dy_t = arrow_length
    dy_v = arrow_length
    
    if equip.on_stilt:
        dx_t = arrow_length * -math.sin(deg_t/180*math.pi)
        dy_t = arrow_length * math.cos(deg_t/180*math.pi)
        dx_v = arrow_length * -math.sin(deg_v/180*math.pi)
        dy_v = arrow_length * math.cos(deg_v/180*math.pi)
        deg_t = 0
        deg_v = 0
        
    for anchor in equip.anchor_list:
        if anchor.tag == anc_t:
            axs[0][0].plot([anchor.x_360[deg_t]],[anchor.y_360[deg_t]], marker=".",c="red",markersize=18,zorder=2,linestyle="none")
            axs[0][0].annotate("{}".format(anchor.tag), xy=(anchor.x_360[deg_t], anchor.y_360[deg_t]), xycoords='data', xytext=(0, 8), textcoords='offset points', fontsize=12, c="red")
        else:
            axs[0][0].plot([anchor.x_360[deg_t]],[anchor.y_360[deg_t]], marker=".",c="blue",markersize=9,zorder=2,linestyle="none")
            axs[0][0].annotate("{}".format(anchor.tag), xy=(anchor.x_360[deg_t], anchor.y_360[deg_t]), xycoords='data', xytext=(0, 5), textcoords='offset points', fontsize=10, c="blue")
    axs[0][0].plot(equip.equip_cog_dict[deg_t][0], equip.equip_cog_dict[deg_t][1], marker="x",c="black",markersize=6,zorder=2,linestyle="none")
    axs[0][0].plot(equip.anchor_cog_dict[deg_t][0], equip.anchor_cog_dict[deg_t][1], marker="x",c="blue",markersize=6,zorder=2,linestyle="none")
    N = int(len(equip.bounding_points_dict[deg_t])/4)
    for i in range(N):
        pt1 = equip.bounding_points_dict[deg_t][4*i]
        pt2 = equip.bounding_points_dict[deg_t][4*i+1]
        pt3 = equip.bounding_points_dict[deg_t][4*i+2]
        pt4 = equip.bounding_points_dict[deg_t][4*i+3]
        polygon_coord = np.array([pt1,pt2,pt3,pt4])
        axs[0][0].add_patch(patches.Polygon(polygon_coord,closed=True,facecolor="lightgray",edgecolor="black",zorder=1,lw=1.0))
    axs[0][0].arrow(equip.equip_cog_dict[deg_t][0], equip.equip_cog_dict[deg_t][1], dx_t, dy_t, width=1.5, head_width=8, head_length=8, fc='k', ec='k')
    
    for anchor in equip.anchor_list:
        if anchor.tag == anc_v:
            axs[1][0].plot([anchor.x_360[deg_v]],[anchor.y_360[deg_v]], marker=".",c="red",markersize=18,zorder=2,linestyle="none")
            axs[1][0].annotate("{}".format(anchor.tag), xy=(anchor.x_360[deg_v], anchor.y_360[deg_v]), xycoords='data', xytext=(0, 8), textcoords='offset points', fontsize=12, c="red")
        else:
            axs[1][0].plot([anchor.x_360[deg_v]],[anchor.y_360[deg_v]], marker=".",c="blue",markersize=9,zorder=2,linestyle="none")
            axs[1][0].annotate("{}".format(anchor.tag), xy=(anchor.x_360[deg_v], anchor.y_360[deg_v]), xycoords='data', xytext=(0, 5), textcoords='offset points', fontsize=10, c="blue")
        anchor_arrow_length = arrow_length / 3
        deg_v1 = degree_slice[vmax_idx]
        dx_anchor = (anchor.vd_360[deg_v1][0] + anchor.vt_360[deg_v1][0]) / anchor.Vtotal_360[deg_v1] * anchor_arrow_length
        dy_anchor = (anchor.vd_360[deg_v1][1] + anchor.vt_360[deg_v1][1]) / anchor.Vtotal_360[deg_v1] * anchor_arrow_length
        axs[1][0].arrow(anchor.x_360[deg_v],anchor.y_360[deg_v], dx_anchor, dy_anchor, width=0.5, head_width=3, head_length=3, fc='k', ec='k')
    
    axs[1][0].plot(equip.equip_cog_dict[deg_v][0], equip.equip_cog_dict[deg_v][1], marker="x",c="black",markersize=6,zorder=2,linestyle="none")
    axs[1][0].plot(equip.anchor_cog_dict[deg_v][0], equip.anchor_cog_dict[deg_v][1], marker="x",c="blue",markersize=6,zorder=2,linestyle="none")
    N = int(len(equip.bounding_points_dict[deg_v])/4)
    for i in range(N):
        pt1 = equip.bounding_points_dict[deg_v][4*i]
        pt2 = equip.bounding_points_dict[deg_v][4*i+1]
        pt3 = equip.bounding_points_dict[deg_v][4*i+2]
        pt4 = equip.bounding_points_dict[deg_v][4*i+3]
        polygon_coord = np.array([pt1,pt2,pt3,pt4])
        axs[1][0].add_patch(patches.Polygon(polygon_coord,closed=True,facecolor="lightgray",edgecolor="black",zorder=0,lw=1.0))
    axs[1][0].arrow(equip.equip_cog_dict[deg_v][0], equip.equip_cog_dict[deg_v][1], dx_v, dy_v, width=1.5, head_width=8, head_length=8, fc='k', ec='k')
    
    # styling
    fig.suptitle(f"Equipment: {equip.name}", fontsize=16, weight='bold')
    axs[0][1].grid()
    axs[1][1].grid()
    axs[0][1].set_ylabel("Tension (lbs)", fontsize=14)
    axs[1][1].set_ylabel("Shear (lbs)", fontsize=14)
    axs[1][1].set_xlabel("Rotation (degree)", fontsize=14)
    axs[0][1].set_xlim(0,360)
    axs[1][1].set_xlim(0,360)
    axs[1][1].set_xticks([0,45,90,135,180,225,270,315,360])
    axs[1][1].set_xticklabels([0,45,90,135,180,225,270,315,360])
    axs[0][1].set_xticks([0,45,90,135,180,225,270,315,360])
    axs[0][1].set_xticklabels([0,45,90,135,180,225,270,315,360])
    axs[0][1].axhline(y=0, color='black', linestyle='-', lw=0.8)
    axs[1][1].axhline(y=0, color='black', linestyle='-', lw=0.8)
    axs[0][0].set_aspect('equal', 'box')
    axs[1][0].set_aspect('equal', 'box')
    axs[0][1].set_ylim(-4600,4600)
    axs[1][1].set_ylim(0,2200)
    plt.tight_layout()
    
    return fig





main()