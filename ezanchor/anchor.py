class Anchor:
    """
    Anchor object definition
        tag:        user-specified tag for each anchor
        xo:         initial x coordinate
        yo:         initial y coordinate
        
    The following attributes are dictionaries storing data as equipment is rotated 360 degrees. 
    Key is float from 0 to 360
        x_360:      dictionary of x coordinate
        y_360:      dictionary of y coordinate
        vd_360:     dictionary of direct shear in anchor [dx, dy]
        vt_360:     dictionary of torsional shear in anchor [vx, vy]
        Vtotal_360: dictionary of total shear in anchor = Vd + Vt
        Ttotal_360: dictionary of total tension in anchor
        
    Unique to Pivot Mode
        d_360:      dictionary of depth from top to anchor
        
    Unique to Stilt Mode
        cx_360      dictionary of cx (x distance between cog and anchor)
        cy_360      dictionary of cy (y distance between cog and anchor)
        Tx_360      tension due to Mx
        Ty_360      tension due to My
        Ta_360      tension due to weight/N_anchor
    """
    def __init__(self, tag, x, y):
        self.tag = tag
        self.xo = x
        self.yo = y
        
        self.x_360 = {}
        self.y_360 = {}
        self.vd_360 = {}
        self.vt_360 = {}
        self.Vtotal_360 = {}
        self.Ttotal_360 = {}
        
        self.d_360 = {}
        
        self.cx_360 = {}
        self.cy_360 = {}
        self.Tx_360 = {}
        self.Ty_360 = {}
        self.Ta_360 = {}
    
    