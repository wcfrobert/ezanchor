import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import os
import math

def preview(equip_obj):
    """function use to visualize equipment base and anchor location prior to analysis"""
    fig, axs = plt.subplots()
    fig.set_size_inches(6,6)
    
    # calculate center of gravities externally
    if equip_obj.N_anchor != 0:
        x_list = []
        y_list = []
        for a in equip_obj.anchor_list:
            x_list.append(a.xo)
            y_list.append(a.yo) 
        x_cog = sum(x_list) / equip_obj.N_anchor
        y_cog = sum(y_list) / equip_obj.N_anchor
        anchor_cog = [x_cog, y_cog]
        equip_cog = anchor_cog if equip_obj.equip_cog == None else equip_obj.equip_cog
        
        # plot anchor points
        for anchor in equip_obj.anchor_list:
            axs.plot([anchor.xo],[anchor.yo], marker=".",c="blue",markersize=9,zorder=2,linestyle="none")
            axs.annotate("{}".format(anchor.tag), xy=(anchor.xo, anchor.yo), xycoords='data', xytext=(0, 5), textcoords='offset points', fontsize=10, c="blue")
        
        # plot COGs
        axs.plot(equip_cog[0], equip_cog[1], marker="x",c="black",markersize=6,zorder=2,linestyle="none")
        axs.annotate("CoG",xy=(equip_cog[0], equip_cog[1]), xycoords='data', color="black",
                        xytext=(0, 5), textcoords='offset points', fontsize=12)
        axs.plot(anchor_cog[0], anchor_cog[1], marker="x",c="blue",markersize=6,zorder=2,linestyle="none")
        axs.annotate("CoR",xy=(anchor_cog[0], anchor_cog[1]), xycoords='data', color="blue",
                        xytext=(0, 5), textcoords='offset points', fontsize=12)
    
    # plot base patches
    N = int(len(equip_obj.bounding_points)/4)
    for i in range(N):
        pt1 = equip_obj.bounding_points[4*i]
        pt2 = equip_obj.bounding_points[4*i+1]
        pt3 = equip_obj.bounding_points[4*i+2]
        pt4 = equip_obj.bounding_points[4*i+3]
        polygon_coord = np.array([pt1,pt2,pt3,pt4])
        axs.add_patch(patches.Polygon(polygon_coord,closed=True,facecolor="lightgray",edgecolor="black",zorder=1,lw=1.0))
    
    # styling
    fig.suptitle("Anchor and Footprint Preview")
    axs.set_aspect('equal', 'box')
    plt.tight_layout()
    axs.autoscale_view()
        
    return fig
    
    
def plot_anchor(equip,anchorID):
    """plot tension and shear demand of a single anchor"""
    # set up figure
    fig, axs = plt.subplots(2, sharex=True)
    fig.set_size_inches(11,8.5)
    
    # extract data
    selected_anchor = equip.anchor_list[anchorID]
    degree = equip.orientations
    tension = []
    shear = []
    for deg in degree:
        tension.append(selected_anchor.Ttotal_360[deg])
        shear.append(selected_anchor.Vtotal_360[deg])

    # plot tension and shear
    axs[0].plot(degree,tension,linewidth=3,color="cornflowerblue")
    axs[1].plot(degree,shear,linewidth=3,color="cornflowerblue")
    
    # annotations
    tmax_idx = np.argmax(tension)
    vmax_idx = np.argmax(shear)
    axs[0].plot(degree[tmax_idx],tension[tmax_idx],color="purple", markersize=8, marker="o")
    axs[1].plot(degree[vmax_idx],shear[vmax_idx],color="purple", markersize=8, marker="o")
    
    axs[0].annotate("Tmax = {:.0f} lbs at {:.0f} deg".format(tension[tmax_idx], degree[tmax_idx]),
                    xy=(degree[tmax_idx],tension[tmax_idx]), xycoords='data', 
                    xytext=(10, 10), textcoords='offset points', fontsize=12)
    
    axs[1].annotate("Vmax = {:.0f} lbs at {:.0f} deg".format(shear[vmax_idx], degree[vmax_idx]),
                    xy=(degree[vmax_idx],shear[vmax_idx]), xycoords='data', 
                    xytext=(10, 10), textcoords='offset points', fontsize=12)
    
    # styling
    fig.suptitle(f"Anchor {anchorID}", fontsize=16, weight='bold')
    axs[0].grid()
    axs[1].grid()
    axs[0].set_ylabel("Tension (lbs)", fontsize=14)
    axs[1].set_ylabel("Shear (lbs)", fontsize=14)
    axs[1].set_xlabel("Rotation (degree)", fontsize=14)
    axs[0].set_ylim(1.2*min(tension),1.2*max(tension))
    axs[1].set_ylim(0,1.2*max(shear))
    axs[1].set_xlim(0,360)
    axs[1].set_xticks([0,45,90,135,180,225,270,315,360])
    axs[1].set_xticklabels([0,45,90,135,180,225,270,315,360])
    axs[0].axhline(y=0, color='black', linestyle='-', lw=0.8)
    axs[1].axhline(y=0, color='black', linestyle='-', lw=0.8)
    plt.tight_layout()
    
    return fig


def plot_equipment(equip):
    """plot tension and shear demand envelope for the entire equipment"""
    # set up figure
    fig, axs = plt.subplots(2, 2, width_ratios = [1,3], height_ratios = [1,1])
    fig.set_size_inches(16,9)
    
    # plot tension and shear envelope
    degree = equip.orientations
    tension = []
    shear = []
    t_anc = []
    v_anc = []
    for deg in degree:
        tension.append(equip.T_max[deg])
        shear.append(equip.V_max[deg])
        t_anc.append(equip.T_crit_anchor[deg])
        v_anc.append(equip.V_crit_anchor[deg])
    tmax_idx = np.argmax(tension)
    vmax_idx = np.argmax(shear)
    axs[0][1].plot(degree,tension,linewidth=3,color="red")
    axs[1][1].plot(degree,shear,linewidth=3,color="red")
    
    # plot individual anchor lines
    for anchor in equip.anchor_list:
        t = []
        v = []
        for deg in degree:
            t.append(anchor.Ttotal_360[deg])
            v.append(anchor.Vtotal_360[deg])
            
        if anchor.tag == t_anc[tmax_idx]:
            axs[0][1].plot(degree,t,linewidth=2,color="blue")
        else:
            axs[0][1].plot(degree,t,linewidth=1,color="skyblue")
        
        if anchor.tag == v_anc[vmax_idx]:
            axs[1][1].plot(degree,v,linewidth=2,color="blue")
        else:
            axs[1][1].plot(degree,v,linewidth=1,color="skyblue")
    
    # plot marker and annotation at max point
    axs[0][1].plot(degree[tmax_idx],tension[tmax_idx],color="purple", markersize=8, marker="o")
    axs[1][1].plot(degree[vmax_idx],shear[vmax_idx],color="purple", markersize=8, marker="o")
    axs[0][1].annotate("Tmax = {:.0f} lbs at {:.0f} deg at anchor {}".format(tension[tmax_idx], degree[tmax_idx], t_anc[tmax_idx]),
                    xy=(degree[tmax_idx],tension[tmax_idx]), xycoords='data', 
                    xytext=(10, 10), textcoords='offset points', fontsize=12)
    axs[1][1].annotate("Vmax = {:.0f} lbs at {:.0f} deg at anchor {}".format(shear[vmax_idx], degree[vmax_idx], v_anc[vmax_idx]),
                    xy=(degree[vmax_idx],shear[vmax_idx]), xycoords='data', 
                    xytext=(10, 10), textcoords='offset points', fontsize=12)
    
    
    # plot equipment footprint previews
    deg_t = degree[tmax_idx]
    anc_t = t_anc[tmax_idx]
    deg_v = degree[vmax_idx]
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
    
    # TENSION
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
    axs[0][0].set_aspect('equal', 'box')
    axs[0][0].arrow(equip.equip_cog_dict[deg_t][0], equip.equip_cog_dict[deg_t][1], dx_t, dy_t, width=1.5, head_width=8, head_length=8, fc='k', ec='k')
    
    # SHEAR
    for anchor in equip.anchor_list:
        if anchor.tag == anc_v:
            axs[1][0].plot([anchor.x_360[deg_v]],[anchor.y_360[deg_v]], marker=".",c="red",markersize=18,zorder=2,linestyle="none")
            axs[1][0].annotate("{}".format(anchor.tag), xy=(anchor.x_360[deg_v], anchor.y_360[deg_v]), xycoords='data', xytext=(0, 8), textcoords='offset points', fontsize=12, c="red")
        else:
            axs[1][0].plot([anchor.x_360[deg_v]],[anchor.y_360[deg_v]], marker=".",c="blue",markersize=9,zorder=2,linestyle="none")
            axs[1][0].annotate("{}".format(anchor.tag), xy=(anchor.x_360[deg_v], anchor.y_360[deg_v]), xycoords='data', xytext=(0, 5), textcoords='offset points', fontsize=10, c="blue")
            
        anchor_arrow_length = arrow_length / 3
        dx_anchor = (anchor.vd_360[deg_v][0] + anchor.vt_360[deg_v][0]) / anchor.Vtotal_360[deg_v] * anchor_arrow_length
        dy_anchor = (anchor.vd_360[deg_v][1] + anchor.vt_360[deg_v][1]) / anchor.Vtotal_360[deg_v] * anchor_arrow_length
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
    axs[1][0].set_aspect('equal', 'box')
    axs[1][0].arrow(equip.equip_cog_dict[deg_v][0], equip.equip_cog_dict[deg_v][1], dx_v, dy_v, width=1.5, head_width=8, head_length=8, fc='k', ec='k')
    
    # styling
    fig.suptitle(f"Equipment: {equip.name}", fontsize=16, weight='bold')
    axs[0][1].grid()
    axs[1][1].grid()
    axs[0][1].set_ylabel("Tension (lbs)", fontsize=14)
    axs[1][1].set_ylabel("Shear (lbs)", fontsize=14)
    axs[1][1].set_xlabel("Rotation (degree)", fontsize=14)
    axs[0][1].set_ylim(-1.2*max(tension),1.2*max(tension))
    axs[1][1].set_ylim(0,1.2*max(shear))
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
    plt.tight_layout()
    
    return fig
