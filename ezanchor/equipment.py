import ezanchor.anchor
import itertools
import numpy as np
import math
import time
import os

class Equipment:
    """
    Equipment object definition
        name                    name or ID for the equipment
        Sds                     short period spectra parameter
        Ip                      importance factor (ASCE 7-16)
        h                       building height (ASCE 7-16)
        z                       height where equipment is attached to the building (ASCE 7-16)
        ap                      component amplification factor (ASCE 7-16)
        Rp                      component response factor (ASCE 7-16) 
        omega                   component overstrength factor (ASCE 7-16)            
        weight                  equipment weight (ASCE 7-16)                    
        CGz                     center of gravity above ground
        CGx                     OPTIONAL. Center of gravity in plan. Default = "auto" => no in-plane torsion
        CGy                     OPTIONAL. Center of gravity in plan. Default = "auto" => no in-plane torsion
        load_combo              "LRFD" or "ASD"                    
        use_omega               set to True if using omega-level load combination 
                      
        equip_cog               location of COG in plan [cog_x, cog_y]
        anchor_cog              anchor group's center of resistance [cog_x, cog_y]
        N_anchor                number of anchors specified by user. Automatically increments each time an anchor is added                        
        anchor_list             list of anchor object
        bounding_points         list of bounding points   [   [x,y],[x,y],[x,y], .....]
        Fpgovern                seismic acceleration per ASCE 7-16
        Emh                     overstrength level seismic acceleration per ASCE 7-16
        weight_factor           factor to apply to dead load; depending on if using LRFD or ASD
        
        is_solved               .solve() done. Analysis results available
        on_stilt                boolean to indicate if equipment is on feet
        folder_created          flag to see if output directory has already been created
        output_dir              output directory where results will be stored
        orientations            the angles of rotation at which the analysis will be conducted e.g. [0, 5, 10, ...]
        
    The following attributes are dictionaries storing data as equipment is rotated 360 degrees. 
    Key is float from 0 to 360 from orientations list
        Ix                      anchor group moment of inertia about x-axis
        Iy                      anchor group moment of inertia about y-axis
        Iz                      anchor group polar moment of inertia (also sometimes denoted as J or Ip)
        Ixy                     anchor group product moment of inertia (used to find max/min inertias)
        equip_cog_dict          equipment COG [x,y]
        anchor_cog_dict         anchor COG [x,y]
        bounding_points_dict    bounding points [pt1,pt2,pt3,.....]
        
        Fh                      horizontal force = Fp or Emh * weight
        Fv                      vertical force = weight * weight_factor
        T_crit_anchor           save anchor tag with max tension
        V_crit_anchor           save anchor tag with max shear
        torsion                 in-plane torsion moment
        T_max                   max tension demand envelope for all anchors
        V_max                   max shear demand for all anchors
        ecc_x                   dx between equip COG and anchor group COR
        ecc_y                   dy between equip COG and anchor group COR
        
    Unique to Pivot Mode
        y_max                   y coordinate used as pivot point
        M_ot                    overturning moment
        M_r                     resisting moment
        M_net                   net moment
        d_max                   distance between pivot point to furthest anchor
        
    Unique to Stilt Mode
        theta                   orientation in degrees to principal axes
        Fh_x                    seismic force x-component
        Fh_y                    seismic force y-component
        Mw_x                    moment due to plan cog offset (x-component)
        Mw_y                    moment due to plan cog offset (y-component)
        Mot_x                   moment due to overturning (x-component)
        Mot_y                   moment due to overturning (y-component)
        Mtotal_x                total moment demand (x-component)
        Mtotal_y                total moment demand (y-component)
        T_min                   max compression demand envelope for all anchors
        C_crit_anchor           save anchor tag with max compression
    """
    def __init__(self, name, Sds, Ip, h, z, ap, Rp, omega, weight, CGz, CGx="auto", CGy="auto", load_combo="LRFD", use_omega=True):
        self.name = name
        self.Sds = Sds
        self.Ip = Ip
        self.h = h
        self.z = z
        self.ap = ap
        self.Rp = Rp
        self.omega = omega
        self.weight = weight
        self.CGz = CGz
        self.load_combo = load_combo
        self.use_omega = use_omega
        
        self.anchor_cog = None
        self.equip_cog = None if CGx == "auto" or CGy == "auto" else [CGx, CGy]
        self.N_anchor = 0
        self.anchor_list = []
        self.bounding_points = []
        self.weight_factor = None
        self.Fpgovern = None
        self.Emh = None
        
        self.is_solved = False
        self.on_stilt = False
        self.folder_created = False
        self.output_dir = None
        self.orientations = None
        
        # the quantities below depends on orientation
        self.Ix = {}
        self.Iy = {}
        self.Iz = {}
        self.Ixy = {}
        self.equip_cog_dict = {}
        self.anchor_cog_dict = {}
        self.bounding_points_dict = {}
        
        self.Fh = {}
        self.Fv = {}
        self.ecc_x = {}
        self.ecc_y = {}
        self.torsion = {}
        self.T_max = {}
        self.V_max = {}
        self.T_crit_anchor = {}
        self.V_crit_anchor = {}
        
        # unique to pivot mode
        self.y_max = {}
        self.M_ot = {}
        self.M_r = {}
        self.M_net = {}
        self.d_max = {}
        
        # unique to stilt mode
        self.theta = None
        self.Fh_x = {}
        self.Fh_y = {}
        self.Mw_x = {}
        self.Mw_y = {}
        self.Mot_x = {}
        self.Mot_y = {}
        self.Mtotal_x = {}
        self.Mtotal_y = {}
        self.T_min = {}
        self.C_crit_anchor = {}

        
    def add_footprint(self, xo, yo, b, h):
        """add base geometry bounding box"""
        pt1 = [xo,yo]
        pt2 = [xo+b,yo]
        pt3 = [xo+b,yo+h]
        pt4 = [xo,yo+h]
        self.bounding_points.append(pt1)
        self.bounding_points.append(pt2)
        self.bounding_points.append(pt3)
        self.bounding_points.append(pt4)
    
    def add_anchor(self, x, y):
        """add a single anchor"""
        anchor_obj = ezanchor.anchor.Anchor(self.N_anchor,x,y)
        self.anchor_list.append(anchor_obj)
        self.N_anchor += 1
    
    def add_anchor_group(self, x0, y0, b, h, nx, ny, mode):
        """
        Add a retangular array of anchors
            xo = x coordinate of bottom left corner of anchor group
            yo = y coordinate of bottom left corner of anchor group
            b = width of anchor group
            h = height of anchor group
            nx = number of anchors in x
            ny = number of anchors in y
            mode = "f" for full array, "p" to only have anchors on perimeter of bounding box
        """
        # determine spacing
        sx = 0 if nx==1 else b / (nx-1)
        sy = 0 if ny==1 else h / (ny-1)
        
        # generate anchor coordinate
        xcoord=[]
        ycoord=[]
        xcoord.append(x0)
        ycoord.append(y0)
        if sx != 0:
            for i in range(nx-1):
                xcoord.append(xcoord[-1]+sx)
        if sy !=0:
            for i in range(ny-1):
                ycoord.append(ycoord[-1]+sy)
        anchor_coord = list(itertools.product(xcoord,ycoord))
        
        # remove middle bars if in perimeter mode
        if mode == "p":
            x_edge0=x0
            x_edge1=xcoord[-1]
            y_edge0=y0
            y_edge1=ycoord[-1]
            anchor_coord = [e for e in anchor_coord if e[0]==x_edge0 or e[0]==x_edge1 or e[1]==y_edge0 or e[1]==y_edge1]
        
        # add anchors
        for a in anchor_coord:
            self.add_anchor(a[0], a[1])
            
    def solve(self, on_stilt=False):
        """start analysis routine"""
        # conduct one analysis or several analyses from 0 to 360 degrees
        DEG_INC = 1
        degrees = list(np.linspace(0,360,360//DEG_INC+1))
        
        # calculate seismic demand and center of gravities
        self.calculate_cog()
        self.calculate_fp()
        if on_stilt:
            self.theta = self.stilt_mode_prep()
            
        # conduct analyses
        time_start = time.time()
        for deg in degrees:
            self.update_geometry(deg)
            self.calculate_I(deg)
            self.calculate_shear_stilt(deg) if on_stilt else self.calculate_shear_pivot(deg)
            self.calculate_tension_stilt(deg) if on_stilt else self.calculate_tension_pivot(deg)
        time_end = time.time()
        self.is_solved = True
        self.orientations = degrees
        self.on_stilt = on_stilt
        print("Analysis completed for equipment: {}".format(self.name))
        print("Elapsed time: {:.4f} seconds".format(time_end - time_start))
        
    def stilt_mode_prep(self):
        """
        When solving in stilt-mode, rotate everything the user defined to its
        principal axes first. Nice to have principal axes at var[0]
        """
        # calculate moment of inertias
        xy_list = []
        xsquared_list = []
        ysquared_list = []
        for a in self.anchor_list:
            dx = a.xo - self.anchor_cog[0]
            dy = a.yo - self.anchor_cog[1]
            xsquared_list.append((dx) ** 2)
            ysquared_list.append((dy) ** 2) 
            xy_list.append(dx*dy)
        Ixy = sum(xy_list)
        Iy = sum(xsquared_list)
        Ix = sum(ysquared_list)
        
        # Mohr's circle stuff
        Imax = (Ix + Iy)/2 + math.sqrt(((Ix - Iy)/2)**2 + (Ixy)**2)
        Imin = (Ix + Iy)/2 - math.sqrt(((Ix - Iy)/2)**2 + (Ixy)**2)
        if Ix==Iy:
            theta = 0
        else:
            theta = (  math.atan((Ixy)/((Ix-Iy)/2)) / 2) * 180 / math.pi
            theta = (90 + theta) if theta<0 else theta #nice to always have +ve rotation
        print("Stilt mode. Calculating orientation of principal axes")
        print("Principal Axes: {:.1f} deg rotation. Imin = {:.1f} and Imax = {:.1f}".format(theta,Imin,Imax))
        
        # modify all anchor coordinates to principal axes
        for a in self.anchor_list:
            coord = [a.xo, a.yo]
            x_rotated,y_rotated = self.transform_rotate(coord, theta)
            a.xo = x_rotated
            a.yo = y_rotated
        
        # modify cogs to principal axes
        self.equip_cog = self.transform_rotate(self.equip_cog, theta)
        self.anchor_cog = self.transform_rotate(self.anchor_cog, theta)
        
        # modify bounding box to principal axes
        bounding_rotated = []
        for coord in self.bounding_points:
            bounding_rotated.append(self.transform_rotate(coord, theta))
        self.bounding_points = bounding_rotated

        return theta

    def calculate_fp(self):
        """calculate seismic force per ASCE 7-16 chapter 14"""
        # seismic force Fp
        Fp = 0.4*self.ap*self.Sds / (self.Rp/self.Ip) * (1 + 2*self.z/self.h)
        Fpmax = 1.6*self.Sds*self.Ip
        Fpmin = 0.3*self.Sds*self.Ip
        if Fp < Fpmin:
            self.Fpgovern = Fpmin
        elif Fp > Fpmax:
            self.Fpgovern = Fpmax
        else:
            self.Fpgovern = Fp
            
        # load combination factor for dead load
        if self.load_combo == "LRFD":
            self.weight_factor = 0.9 - 0.2*self.Sds
        elif self.load_combo == "ASD":
            self.weight_factor = 0.6 - 0.7*0.2*self.Sds
            self.Fpgovern = self.Fpgovern * 0.7
        else:
            raise RuntimeError("load combo tag not recognized")
        
        self.Emh = self.Fpgovern * self.omega
        
    def calculate_cog(self):
        """calculate center of gravity of anchor group"""
        # calculate centroid of anchor group
        x_list = []
        y_list = []
        for a in self.anchor_list:
            x_list.append(a.xo)
            y_list.append(a.yo) 
        x_cog = sum(x_list) / self.N_anchor
        y_cog = sum(y_list) / self.N_anchor
        self.anchor_cog = [x_cog, y_cog]
        
        # if equipment COG not provided
        if self.equip_cog == None:
            self.equip_cog = [x_cog, y_cog]
          
    def transform_rotate(self, coord, deg):
        """helper function to perform rotation of x,y coordinate with rotation matrix"""
        rad = deg * math.pi / 180
        T = np.array([
            [math.cos(rad), -math.sin(rad)],
            [math.sin(rad), math.cos(rad)]])
        coord_transformed = T @ np.array(coord)
        return list(coord_transformed)
    
    def update_geometry(self, deg):
        """rotate equipment and adjust x,y coordinates at a specified degree"""
        # transformed anchor coordinate
        for a in self.anchor_list:
            coord = [a.xo, a.yo]
            x_rotated,y_rotated = self.transform_rotate(coord, deg)
            a.x_360[deg] = x_rotated
            a.y_360[deg] = y_rotated
        
        # transformed cogs
        equip_cog_rotated = self.transform_rotate(self.equip_cog, deg)
        anchor_cog_rotated = self.transform_rotate(self.anchor_cog, deg)
        self.equip_cog_dict[deg] = equip_cog_rotated
        self.anchor_cog_dict[deg] = anchor_cog_rotated
        
        # transformed bounding box
        bounding_rotated = []
        for coord in self.bounding_points:
            bounding_rotated.append(self.transform_rotate(coord, deg))
        self.bounding_points_dict[deg] = bounding_rotated
    
    def calculate_I(self, deg):
        """
        Calculate moment of inertias for anchor group at a specified degree
            x is horizontal axis
            y is vertical axis
            
            https://www.eng-tips.com/viewthread.cfm?qid=466107
            I = sum(Ii) + Ad^2     It is customary to ignore first term for bolts
            I = Ad^2               Use unit area
            I = d^2                Where d is equal to distance from anchor to centroid
            
            Ix = moment of inertia about x-axis (horizontal axis)
            Iy = moment of inertia about y_axis (vertical axis)
            Iz = polar moment of inertia = Ix + Iy
            Ixy = product moment of inertia
        """
        xsquared_list = []
        ysquared_list = []
        xy_list = []
        for a in self.anchor_list:
            dx = a.x_360[deg] - self.anchor_cog_dict[deg][0]
            dy = a.y_360[deg] - self.anchor_cog_dict[deg][1]
            xsquared_list.append((dx) ** 2)
            ysquared_list.append((dy) ** 2) 
            xy_list.append(dx*dy)
        self.Iy[deg] = sum(xsquared_list)
        self.Ix[deg] = sum(ysquared_list)
        self.Ixy[deg] = sum(xy_list)
        self.Iz[deg] = self.Ix[deg] + self.Iy[deg]
        
    def calculate_tension_stilt(self, deg):
        """
        Calculate tension demand in the anchors for equipment on stilts.
        
        This methodology uses classical mechanics equations. We rotate the moment vector rather
        than the actual equipment geometry.
            Procedure equivalent to P/A + Mx*y/Ix + My*x/Iy
            
        Signs become important to track. To be consistent with pivot point methodology, 0 degree
        refers to seismic force applied towards +y (upwards). Angle with respect to +y axis
            Let tension = +ve, compression = -ve
            Let origin be at anchor COG
            Let +x point to the right, let +y point up, let +z point out of page
            
        Adjustment to force/moment vectors to obey right-hand rule
            0. starting at vertical axis rotating ccw. Need to adjust sin and cos
                cos + - - + (Fy = F cos theta = + - - +) ok
                sin + + - - (Fx = F sin theta = - - + +) FLIP
            1. Fy=+ve, Mx should be -ve (FLIP)
            2. Fx=-ve, My should be -ve (ok)
            3. W=-ve, if dy +ve, Mx should be -ve (ok)
            4. W=-ve, if dx +ve, My should be +ve (FLIP)
            
        Adjustment to tension/compression demands:
            5. Weight will always be downwards -ve. T_axial always negative = compression (ok)
            6. if Mx +ve and anchor_y is +ve, then demand (+*+ = +ve = tension) ok
            7. if My +ve and anchor_x is +ve, then demand (+*+ = +ve = tension) FLIP
        """
        # moment contribution from self-weight is constant
        W = - (self.weight_factor * self.weight) #FLIP
        dx = self.equip_cog[0] - self.anchor_cog[0]
        dy = self.equip_cog[1] - self.anchor_cog[1]
        Mwx = W * dy
        Mwy = -(W * dx) #FLIP
        
        # calculate overturning moment
        F = (self.Emh * self.weight) if self.use_omega else (self.Fpgovern * self.weight)
        Motx = -(F*math.cos(deg/180*math.pi)) * self.CGz #FLIP
        Moty = (F*(-math.sin(deg/180*math.pi))) * self.CGz #FLIP sin()
        
        # compute tension demand
        T_axial = W / self.N_anchor
        Tmax = -np.inf
        Tmin = np.inf
        t_crit_anchor = None
        c_crit_anchor = None
        for anc in self.anchor_list:
            cx = anc.xo - self.anchor_cog[0]
            cy = anc.yo - self.anchor_cog[1]
            T_x = (Mwx + Motx) * cy / self.Ix[0]
            T_y = -((Mwy + Moty) * cx / self.Iy[0]) #FLIP
            T_total = T_axial + T_x + T_y
            
            # save anchor results
            anc.d_360[deg] = 0
            anc.Ttotal_360[deg] = T_total
            anc.cx_360[deg] = cx
            anc.cy_360[deg] = cy
            anc.Tx_360[deg] = T_x
            anc.Ty_360[deg] = T_y
            anc.Ta_360[deg] = T_axial
            
            if T_total > Tmax:
                Tmax = T_total
                t_crit_anchor = anc.tag
            if T_total < Tmin:
                Tmin = T_total
                c_crit_anchor = anc.tag

        # save results in dicts
        self.Fh_y[deg] = (F*math.cos(deg/180*math.pi))
        self.Fh_x[deg] = (F*(-math.sin(deg/180*math.pi)))
        self.Mw_x[deg] = Mwx
        self.Mw_y[deg] = Mwy
        self.Mot_x[deg] = Motx
        self.Mot_y[deg] = Moty
        self.Mtotal_x[deg] = Motx+Mwx
        self.Mtotal_y[deg] = Moty+Mwy
        self.T_crit_anchor[deg] = t_crit_anchor
        self.C_crit_anchor[deg] = c_crit_anchor
        self.M_ot[deg] = math.sqrt((Mwx + Motx)**2 + (Mwy + Moty)**2)
        self.T_min[deg] = Tmin
        self.T_max[deg] = Tmax
        self.Fh[deg] = F
        self.Fv[deg] = W
        
    
    
    def calculate_tension_pivot(self, deg):
        """
        Calculate tension demand in the anchors assuming a pivot point at edge of equipment footprint
        
        This methodology involves finding the point of pivot, then calculating anchor demand using the rigid
        base assumption (similar triangles). Please note that an important simplification is made here which is very
        typical for equipment anchorage calculations. EZanchor calculates pivot point as max(y) - topmost point.
        
        In essence, rather than meshing the concrete fibers and finding the exact depth of neutral axis and concrete bearing
        stress profile at each orientation (which takes more memory and compute), we recognize that the depth of 
        concrete stress block is always small relative to the equipment footprint, and the phenomenon of OVERTURNING
        involves the edge of the equipment by definition. In other words, although it is more correct to mesh and find the
        exact depth of neutral axis, the change to the final answer is insignificant. That being said, the user should ensure that
        the footprint of equipment is actually large. EZanchor should NOT be used for things like base plate design or equipment 
        with small footprint.       
        """
        # get pivot point
        bounding_pts = self.bounding_points_dict[deg]
        y_max = -np.inf
        for pts in bounding_pts:
            y_max = pts[1] if y_max < pts[1] else y_max
        
        # get lever arm for every anchor
        d_max = -np.inf
        crit_anchor = None
        for a in self.anchor_list:
            d_current = max(y_max - a.y_360[deg], 0) #anchors above pivot is inactive hence 0
            a.d_360[deg] = d_current
            if d_current > d_max:
                d_max = d_current
                crit_anchor = a.tag
        
        # calculate overturning and resisting moment
        Fv = self.weight_factor * self.weight
        Fh = self.Emh * self.weight if self.use_omega else self.Fpgovern * self.weight
        Mot = Fh * self.CGz
        Mr = Fv * abs(y_max - self.equip_cog_dict[deg][1])
        Mnet = max(Mot - Mr, 0)
        
        # compute tension demand
        di_over_dmax = []
        for a in self.anchor_list:
            di_over_dmax.append(a.d_360[deg]**2/d_max)
        Tmax = Mnet / sum(di_over_dmax)
        
        for a in self.anchor_list:
            a.Ttotal_360[deg] = a.d_360[deg]/d_max * Tmax
        
        # save results in dicts
        self.y_max[deg] = y_max
        self.d_max[deg] = d_max
        self.T_crit_anchor[deg] = crit_anchor
        self.M_ot[deg] = Mot
        self.M_r[deg] = Mr
        self.M_net[deg] = Mnet
        self.T_max[deg] = Tmax
        self.Fh[deg] = Fh
        self.Fv[deg] = Fv
    
    def calculate_shear_stilt(self, deg):
        """
        Calculate shear demand in the anchors stilt mode.
        let ecc_x = equip - anchor. let CCW be positive.
            0. starting at vertical axis rotating ccw. Need to adjust sin and cos
                cos + - - + (Fy = F cos theta = + - - +) ok
                sin + + - - (Fx = F sin theta = - - + +) FLIP
            1. +Fy, +ecc_x = +M => OK
            2. +Fx, +ecc_y = +M but CW should be -ve. FLIP
            3. if +torsion, CCW, +cx, vdy should be -ve down FLIP
            4. if +torsion, CCW, +cy, vdx should be +ve right ok
        """
        # calculate torsion demand
        ecc_x = (self.equip_cog_dict[0][0] - self.anchor_cog_dict[0][0])
        ecc_y = -(self.equip_cog_dict[0][1] - self.anchor_cog_dict[0][1]) #FLIP
        
        Fh = self.Emh * self.weight if self.use_omega else self.Fpgovern * self.weight
        Fh_y = (Fh*math.cos(deg/180*math.pi))
        Fh_x = (Fh*(-math.sin(deg/180*math.pi))) #FLIP
        
        torsion = Fh_y * ecc_x + Fh_x * ecc_y
        
        Vmax = -np.inf
        crit_anchor = None
        for anc in self.anchor_list:
            # calculate direct shear
            vdx = -Fh_x /self.N_anchor #shear resistance in opposite direction of Fp
            vdy = -Fh_y /self.N_anchor #shear resistance in opposite direction of Fp
            
            # calculate torsional shear
            cx = anc.x_360[0] - self.anchor_cog_dict[0][0]
            cy = anc.y_360[0] - self.anchor_cog_dict[0][1]
            rx = torsion * cy / self.Iz[0]
            ry = -torsion * cx / self.Iz[0] #FLIP
            
            # calculate total shear
            vtotal = math.sqrt((rx+vdx)**2 + (ry + vdy)**2)
            
            # save to anchor object
            anc.vd_360[deg] = [vdx, vdy]
            anc.vt_360[deg] = [rx, ry]
            anc.Vtotal_360[deg] = vtotal
            if vtotal > Vmax:
                Vmax = vtotal
                crit_anchor = anc.tag
        
        self.V_max[deg] = Vmax
        self.torsion[deg] = torsion
        self.V_crit_anchor[deg] = crit_anchor
        self.ecc_x[deg] = ecc_x
        self.ecc_y[deg] = ecc_y
    
    def calculate_shear_pivot(self, deg):
        """
        Calculate shear demand in the anchors pivot mode.
        In pivot mode, force is always in the +y direction. ecc_x is 0
        """
        # calculate torsion demand
        ecc_x = (self.equip_cog_dict[deg][0] - self.anchor_cog_dict[deg][0])
        ecc_y = 0
        Fh = self.Emh * self.weight if self.use_omega else self.Fpgovern * self.weight
        Fh_y = Fh
        Fh_x = 0
        torsion = Fh_y * ecc_x

        Vmax = -np.inf
        crit_anchor = None
        for anc in self.anchor_list:
            # calculate direct shear
            vdx = 0
            vdy = -Fh_y /self.N_anchor #shear resistance in opposite direction of Fp
            
            # calculate torsional shear
            cx = anc.x_360[deg] - self.anchor_cog_dict[deg][0]
            cy = anc.y_360[deg] - self.anchor_cog_dict[deg][1]
            rx = torsion * cy / self.Iz[deg]
            ry = -torsion * cx / self.Iz[deg] #FLIP
            
            # calculate total shear
            vtotal = math.sqrt((rx+vdx)**2 + (ry + vdy)**2)
            
            # save to anchor object
            anc.vd_360[deg] = [0, vdy]
            anc.vt_360[deg] = [rx, ry]
            anc.Vtotal_360[deg] = vtotal
            if vtotal > Vmax:
                Vmax = vtotal
                crit_anchor = anc.tag
        
        self.V_max[deg] = Vmax
        self.ecc_x[deg] = ecc_x
        self.ecc_y[deg] = ecc_y
        self.torsion[deg] = torsion
        self.V_crit_anchor[deg] = crit_anchor
    
    def create_output_folder(self):
        """Create a folder in current working directory to store results"""
        result_folder = "{}_run_results".format(self.name)
        parent_dir = os.getcwd()
        
        # check if path exists. Handle errors and mkdir if needed
        if os.path.isdir(result_folder):
            folderexists = result_folder
            j=1
            while os.path.isdir(result_folder):
                result_folder = folderexists + str(j)
                j=j+1
            output_dir = os.path.join(parent_dir,result_folder)
            os.makedirs(output_dir)
            print("{} folder already exists, results will be stored here instead: {}".format(folderexists,output_dir))
        else:
            output_dir = os.path.join(parent_dir,result_folder)
            os.makedirs(output_dir)
            print("Results to be generated in output folder: {}".format(output_dir))
        
        self.folder_created = True
        self.output_dir = output_dir
        
    def export_data(self):
        """export analysis data to csv"""
        # handle exceptions
        if not self.is_solved:
            raise RuntimeError("Please .solve() prior to exporting data")
        if not self.folder_created:
            self.create_output_folder()
        
        # not very elegant. Can turn into data frame then to_csv along with __dict__. Will try to fix when I have the time.
        # write to csv files
        if self.on_stilt:
            file_path = os.path.join(self.output_dir, "{}_equipment.csv".format(self.name))
            with open(file_path,'w') as f:
                f.write("degree,Fp,W,Fp_x,Fp_y,Mot_x,Mot_y,Mw_x,Mw_y,Mtotal_x,Mtotal_y,ecc_x,ecc_y,torsion,Tmax,Cmax,Vmax,T_anchor,C_anchor,V_anchor,equip_xo,equip_yo,anchor_xo,anchor_yo,Ix,Iy,Iz,Ixy\n")
                for deg in self.Fh.keys():
                    f.write(f"{deg}"+
                            f",{self.Fh[deg]}"+
                            f",{self.Fv[deg]}"+
                            f",{self.Fh_x[deg]}"+
                            f",{self.Fh_y[deg]}"+
                            f",{self.Mot_x[deg]}"+
                            f",{self.Mot_y[deg]}"+
                            f",{self.Mw_x[deg]}"+
                            f",{self.Mw_y[deg]}"+
                            f",{self.Mtotal_x[deg]}"+
                            f",{self.Mtotal_y[deg]}"+
                            f",{self.ecc_x[deg]}"+
                            f",{self.ecc_y[deg]}"+
                            f",{self.torsion[deg]}"+
                            f",{self.T_max[deg]}"+
                            f",{self.T_min[deg]}"+
                            f",{self.V_max[deg]}"+
                            f",{self.T_crit_anchor[deg]}"+
                            f",{self.C_crit_anchor[deg]}"+
                            f",{self.V_crit_anchor[deg]}"+
                            f",{self.equip_cog_dict[deg][0]}"+
                            f",{self.equip_cog_dict[deg][1]}"+
                            f",{self.anchor_cog_dict[deg][0]}"+
                            f",{self.anchor_cog_dict[deg][1]}"+
                            f",{self.Ix[deg]}"+
                            f",{self.Iy[deg]}"+
                            f",{self.Iz[deg]}"+
                            f",{self.Ixy[deg]}\n")
                    
            file_path = os.path.join(self.output_dir, "{}_anchors.csv".format(self.name))
            with open(file_path,'w') as f:
                self.cx_360 = {}
                self.cy_360 = {}
                self.Tx_360 = {}
                self.Ty_360 = {}
                self.Ta_360 = {}
                f.write("anchor,degree,x,y,V_dx,V_dy,V_tx,V_ty,V_total,cx,cy,T_x,T_y,Ta,T_total\n")
                for anc in self.anchor_list:
                    for deg in anc.x_360.keys():
                        f.write(f"{anc.tag}"+
                                f",{deg}"+
                                f",{anc.x_360[deg]}"+
                                f",{anc.y_360[deg]}"+
                                f",{anc.vd_360[deg][0]}"+
                                f",{anc.vd_360[deg][1]}"+
                                f",{anc.vt_360[deg][0]}"+
                                f",{anc.vt_360[deg][1]}"+
                                f",{anc.Vtotal_360[deg]}"+
                                f",{anc.cx_360[deg]}"+
                                f",{anc.cy_360[deg]}"+
                                f",{anc.Tx_360[deg]}"+
                                f",{anc.Ty_360[deg]}"+
                                f",{anc.Ta_360[deg]}"+
                                f",{anc.Ttotal_360[deg]}\n")
        else:
            file_path = os.path.join(self.output_dir, "{}_equipment.csv".format(self.name))
            with open(file_path,'w') as f:
                f.write("degree,Fp,W,Mot,Mr,Mnet,dmax,ecc,torsion,Tmax,Vmax,T_anchor,V_anchor,equip_xo,equip_yo,anchor_xo,anchor_yo,Ix,Iy,Iz,Ixy\n")
                for deg in self.Fh.keys():
                    f.write(f"{deg}"+
                            f",{self.Fh[deg]}"+
                            f",{self.Fv[deg]}"+
                            f",{self.M_ot[deg]}"+
                            f",{self.M_r[deg]}"+
                            f",{self.M_net[deg]}"+
                            f",{self.d_max[deg]}"+
                            f",{self.ecc_x[deg]}"+
                            f",{self.torsion[deg]}"+
                            f",{self.T_max[deg]}"+
                            f",{self.V_max[deg]}"+
                            f",{self.T_crit_anchor[deg]}"+
                            f",{self.V_crit_anchor[deg]}"+
                            f",{self.equip_cog_dict[deg][0]}"+
                            f",{self.equip_cog_dict[deg][1]}"+
                            f",{self.anchor_cog_dict[deg][0]}"+
                            f",{self.anchor_cog_dict[deg][1]}"+
                            f",{self.Ix[deg]}"+
                            f",{self.Iy[deg]}"+
                            f",{self.Iz[deg]}"+
                            f",{self.Ixy[deg]}\n")
            
            file_path = os.path.join(self.output_dir, "{}_anchors.csv".format(self.name))
            with open(file_path,'w') as f:
                f.write("anchor,degree,x,y,d,V_dx,Vdy,V_tx,V_ty,V_total,T_total\n")
                for anc in self.anchor_list:
                    for deg in anc.x_360.keys():
                        f.write(f"{anc.tag}"+
                                f",{deg}"+
                                f",{anc.x_360[deg]}"+
                                f",{anc.y_360[deg]}"+
                                f",{anc.d_360[deg]}"+
                                f",{anc.vd_360[deg][0]}"+
                                f",{anc.vd_360[deg][1]}"+
                                f",{anc.vt_360[deg][0]}"+
                                f",{anc.vt_360[deg][1]}"+
                                f",{anc.Vtotal_360[deg]}"+
                                f",{anc.Ttotal_360[deg]}\n")




