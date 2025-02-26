"""
Class to create data list for Conduit Flow Process (cfp) (required for all CFP
    modes)

Documentation: https://pubs.usgs.gov/tm/tm6a24/    
"""

import warnings

class cfp():
    """
    This class handles the writing of the .cfp input file for MODFLOW CFP.

    Dependencies: None
    
    Parameters
    ----------
    mode : CFP mode; int
    nnodes : number of nodes (get from nbr output, see the CFPy.utils.nbr
        module); int
    npipes : number of pipes (get from nbr output, see the CFPy.utils.nbr
        module); int
    nlay : number of MODFLOW layers; int
    nbr_data : data as returned from the CFPy.utils.nbr module; list
    geoheight : absolute height of nodes (use cond_elev from CFPy.utils.nbr
        module output), list
    sa_exchange : flag (if 0: user assigns pipe conductance
        for each node, if 1: user assigns conduit wall 
        permeability); int
    epsilon : convergence criterion; float
    niter : maximum number of iterations, int
    relax : relaxation parameter 0 < relax < 1, float
    p_nr : flag (if 0: iteration results are not printed, if 1: iteration
        results are printed), int
    cond_data : conduit parametrization data (list-like), has to contain list-
        likes for NO_P, DIAMETER, TORTUOSITY, RHEIGHT, LCRITREY_P, and
        TCRITREY_P in that order, i.e. [[0, 1, ...], [0.1, 1.0, ...], ...];
        list-like
    n_head : pre-defined node heads as list-like with length nnodes, where -1
        indicates that the head should be calculated and other values define a
        fixed head, e.g., [-1, 20.1, ...]; list-like 
    k_exchange : conduit conductances or wall permeabilities as list like with
        length npipes; list-like of floats
    ncl : total number of conduit layers (HAS NO EFFECT AT THE MOMENT); int
    cl : list specifying which MODFLOW layers are conduit layers (HAS NO EFFECT
        AT THE MOMENT); list-like of ints
    ltemp : mean water temperature; float
    condl_data : conduit layer parametrization data (list-like), has to contain
        list-likes for VOID, LCRITREY_L, and TCRITREY_L in that order; list-like
        (NOT IMPLEMENTED)
    cads : CADS parametrization data, either None if CADS is not considered or
        list-like with length npipes containing the CADS width for each pipe;
        list-like of floats or None
    fbc: FBC (further boundary conditions) parameterization data, either None if
        FBC are not considered or list of tuples for each node where an FBC is
        set (see notes below); list of tuples or None

    NOTE (fbc):
        There are multiple types of FBCs:
            - fixed head-limited flow boundary (FHLQ)
                - value (below) is a float representing the flow limitation
                    (i.e., a flow rate)
                - example: [(1, "FHLQ", 0.75), (...), ...]
            - conduit well boundary (WELL)
                - value (below) is None (the flow rate for the node has to
                    be given in the CFPy.cfp.crch module)
                - example: [(1, "WELL", None), (...), ...]
            - Cauchy boundary (CAUCHY)
                - value (below) is a tuple for the Cauchy conductivity and
                    the Cauchy limited inflow; the node head represents the
                    Cauchy head if this type of FBC is used
                - example: [(1, "CAUCHY", (0.01, 0.04)), (...), ...]
            - limited head boundary (LH)
                - value (below) is None (the head specified for the node
                    represents the limited head)
                - example: [(1, "LH", None), (...), ...]
            - time-dependent boundary (TD) - NOT IMPLEMENTED
                - value (below) is ...
        
        Specify FBCs via a list of tuples of the form:
        [(node_number, FBC_type, value), (...), ...], e.g.,
        [(1, "WEL", {1: -0.25, 2: -0.25, ...})]

    Input Variables / Lines of the MODFLOW CFP Module (.cfp file):
        0, 2, 3, 5, 7, 9, 10, 11, 13, 15, 17, 19, 21, 23, 24, 26, 28, 30, 31,
            33, 35, 37, 38: Comment lines
        1 : mode - is an integer value controlling the activation of conduit
            pipes and (or) layers
        4 : nnodes - is an integer value for the total number of nodes in the
                conduit pipe network. Each node is located at the center of a
                model cell in plan view.
            npipes - is an integer value for the total number of pipes in the
                conduit network.
           nlayers - is an integer value for the total number of model layers.
        6 : temperature - is a real number in degrees Celsius, representing the
            average temperature of ground water in the conduit pipes.
        8 : no_n mc mr ml nb1 nb2 nb3 nb4 nb5 nb6 pb1 pb2 pb3 pb4 pb5 pb6 - are
            integer values that describe how the nodes are connected to the
            MODFLOW model cells, and how node and pipe connections are formed.
        12 : geoheight - is the absolute elevation of the pipe nodes.
        14 : sa_exchange - is an integer that equals either 0 or 1.
            If sa_exchange = 0, the user assigns the pipe conductance for each
                node in the CFP Input File.
            If sa_exchange = 1, the user assigns the conduit wall permeability,
                and the CFP will compute the surface areas of pipes when
                assembling pipe conductances.
        16 : epsilon - is a real number for the convergence criterion of the
            Newton-Raphson iteration for pipe flow equations. Use a very small
            number, such as 0.000001.
        18 : niter - is an integer number for the maximum number of
            Newton-Raphson iterations. If convergence cannot be achieved, the
            program will stop and a warning will be printed in the MODFLOW
            listing file.
        20 : relax - is a real number of relaxation that determines the step
            length of the Newton-Raphson iterations. Changing relax to a value
            slightly less than 1.0 may facilitate convergence of the pipe flow
            equations.
        22 : p_nr - is an integer print flag for Newton Raphson 22. iterations.
        25 : no_p diameter tortuosity rheight lcritrey_p tcritrey_p - are the
            pipe numbers and hydraulic properties.
        27 : no_n n_head - are integer node numbers and either node constant
            heads or a flag that activates a CFP solution for node head. Use one
            line for each node.
        29 : no_n k_exchange - are integer node numbers and real numbers for
            either conduit wall permeabilities (when sa_exchange=1) or pipe
            conductances (when sa_exchange=0), one line for each node.
        32 : ncl - is an integer equal to the total number of conduit layers.
        34 : cl - is a one-dimensional integer array entered on a single line of
            the CFP Input File. This array holds the MODFLOW layer numbers that
            are conduit layers.
        36 : ltemp - is the mean water temperature in degrees Celsius of all
            conduit layers.
        39 : void lcritrey_l tcritrey_l - are real numbers for each conduit
            flow layer.    
    """
    
    def __init__(
        self,
        mode,
        nnodes,
        npipes,
        nlay,
        nbr_data=0,
        geoheight=0,
        sa_exchange=0,
        epsilon=0,
        niter=0,
        relax=0,
        p_nr=0,
        cond_data=0,
        n_head=0,
        k_exchange=0,
        ncl=0,
        cl=0,
        ltemp=0,
        condl_data=0,
        cads=None,
        fbc=None
        ):
        
        self.mode = str(mode)
        self.nnodes = str(nnodes)
        self.npipes = str(npipes)
        self.nlay = str(nlay)
        self.geoheight = geoheight
        self.sa_exchange = str(sa_exchange)
        self.epsilon = str(epsilon)
        self.niter = str(niter)
        self.relax = str(relax)
        self.p_nr = str(p_nr)
        self.cond_data = cond_data
        self.n_head = n_head
        self.k_exchange = k_exchange
        self.ncl = str(ncl)
        self.cl = str(cl)
        self.ltemp = str(ltemp)
        self.condl_data = str(condl_data)
        self.nbr_data = nbr_data
        self.nbr_str = []
        self.geoheight_str = []
        self.cond_data_str = []
        self.n_head_str = []
        self.k_exchange_str = []
        self.condl_data_str = []
        # extra cads_str (as for other parameters) not neccessary as it gets
        #   added with the k_exchange string
        self.cads = cads
        self.fbc = fbc
        
        ######
        ## nbr
        ######
        # create strings for nbr_data
        # get number of nodes and for each node append an empty list to the nbr
        #   string
        for i in range(len(self.nbr_data[0])):
            self.nbr_str.append([])
        
        # create neighbor-information for each node from network information in
        #   nbr_data
        # append relevant values for each node
        for i in range(len(self.nbr_data[0])):
            self.nbr_str[i] = (
                str(self.nbr_data[0][i]) + ' ' +
                str(self.nbr_data[2][i][0]) + ' ' +
                str(self.nbr_data[2][i][1]) + ' ' +
                str(self.nbr_data[2][i][2]) + ' ' +
                str(self.nbr_data[4][i][0]) + ' ' +
                str(self.nbr_data[4][i][1]) + ' ' +
                str(self.nbr_data[4][i][2]) + ' ' +
                str(self.nbr_data[4][i][3]) + ' ' +
                str(self.nbr_data[4][i][4]) + ' ' +
                str(self.nbr_data[4][i][5]) + ' ' +
                str(self.nbr_data[7][i][0]) + ' ' +
                str(self.nbr_data[7][i][1]) + ' ' +
                str(self.nbr_data[7][i][2]) + ' ' +
                str(self.nbr_data[7][i][3]) + ' ' +
                str(self.nbr_data[7][i][4]) + ' ' +
                str(self.nbr_data[7][i][5])
            )
        
        ######
        ## geoheight
        ######
        # prepare strings / lists for geoheight
        # for each node, append an empty list to geoheight_str
        for i in range(int(self.nnodes)):
            self.geoheight_str.append([])
        
        # produce nnodes number of lines with strings (node_num, geoheight)
        # append relevant values for each node
        # initialize node counter
        node = 0
        # iterate over node planes
        for plane in range(len(self.geoheight)):
            # iterate over rows (nodes are numbered in the order they
            #   appear when iterating through 1. node planes / layers,
            #   2. rows, 3. columns)
            # order should be kept when iterating similarly
            # no need to separately get the node numbers from somewhere
            for row in range(len(self.geoheight[plane])):
                # iterate over the columns
                for col in range(len(self.geoheight[plane][row])):
                    # get the elevation value / the height for the current node
                    geoheight_val = str(geoheight[plane][row][col])
                    # separate value if it has a leading "c" (e.g., "c25.1")
                    #   meaning the node is vertically connected to another
                    #   node
                    if geoheight_val[0] == "c":
                        geoheight_val = geoheight_val[1:]
                    # if the (float) value is NOT equal to -999, it represents
                    #   a node elevation value
                    if float(geoheight_val) != -999:
                        # increment the counter
                        node += 1
                        # make the string for the current node
                        geoheight_tuple = str(node) + ' ' + str(geoheight_val)
                        # put the individual string to the global data structure
                        #   holding all such strings
                        self.geoheight_str[node - 1] = geoheight_tuple

        ######
        ## cond_data
        ######
        # create strings for cond_data given a list of lists with each list
        #   describing one parameter for all respective pipes (i.e., each inner
        #   list has length npipes): NO_P, DIAMETER, TORTU., RHEIGHT,
        #   LCRITREY_P, TCRITREY_P
        # prepare strings / lists for cond_data
        for pipe in range(len(self.cond_data[0])):
            self.cond_data_str.append([])

        # initialize the counter
        pipe_iter = 0
        # loop over all pipes / lines in cond_data and create strings
        for num, dia, tor, rhe, lre, hre in zip(self.cond_data[0],
                                                self.cond_data[1],
                                                self.cond_data[2],
                                                self.cond_data[3],
                                                self.cond_data[4],
                                                self.cond_data[5]):
            # create the full string for the current pipe
            cond_str = (
                str(num) + ' ' +
                str(dia) + ' ' +
                str(tor) + ' ' +
                str(rhe) + ' ' +
                str(lre) + ' ' +
                str(hre)
            )
            # put the individual string to the global data structure
            #   holding all such strings
            self.cond_data_str[pipe_iter] = cond_str
            # increment the counter
            pipe_iter += 1

        ######
        ## node heads and fbc data
        ######
        # create strings / lists for n_head
        for node in range(len(self.n_head[0])):
            self.n_head_str.append([])

        # loop over all nodes and create head strings if there is 
        #   no FBC data
        if self.fbc is None:
            # initialize counter
            node_iter = 0
            # loop over all nodes
            for node in zip(self.n_head[0], self.n_head[1]):
                # create string of node number and node head
                node_str = str(node[0]) + ' ' + str(node[1])
                # put the individual string to the global data structure
                #   holding all such strings
                self.n_head_str[node_iter] = node_str
                # increment the counter
                node_iter += 1
        # if there is FBC data, handle it
        elif self.fbc is not None:
            # if available, check FBC data; it is not possible to have
            #     more than one FBC for a given node
            fbc_nodes = []

            # get fbc nodes and indices
            # loop over fbc dict keys
            for i in self.fbc:
                # append the node number to the fbc_nodes
                fbc_nodes.append(i[0])

            # get unique node numbers
            fbc_nodes_unique = list(set(fbc_nodes))

            # raise an error if there is a node with two boundary conditions
            try:
                if not fbc_nodes == fbc_nodes_unique:
                    msg = ("There are multiple FBCs specified for a single"
                        "node!")
                    raise ValueError(msg)
            except ValueError:
                raise

            # make structure that has FBC information for EVERY node
            #     (even if there is no FBC at that node)
            # initialize counters
            node_iter = 0
            node_str_iter = 0
            # make list of node numbers
            node_nums = [[i] for i in range(1, int(self.nnodes) + 1)]
            # iterate over the nodes
            for i, j in zip(node_nums, self.n_head[1]):
                # append the node head
                i.append(j)
                # check if node has FBC data
                if i[0] in fbc_nodes:
                    # if there is an FBC for the node, append the Type
                    i.append(fbc[node_iter][1])

                    # check individual FBC types and append corresponding
                    #   values if applicable (not for WELL)
                    if fbc[node_iter][1] == "TD":
                        raise ValueError("TD / time dependent boundary is not"
                            "implemented!")
                    elif fbc[node_iter][1] == "FHLQ":
                        i.append(fbc[node_iter][2])
                    elif fbc[node_iter][1] == "CAUCHY":
                        i.append(fbc[node_iter][2][0])
                        i.append(fbc[node_iter][2][1])
                    elif fbc[node_iter][1] == "WELL":
                        msg = ("When using a WELL FBC, make sure to include the"
                               "BC values, i.e., flow rates, in the CRCH"
                               "module!")
                        warnings.warn(msg)
                    # check if an invalid fbc type was given
                    elif fbc[node_iter][1] not in [
                        "FHLQ",
                        "WELL",
                        "CAUCHY",
                        "LH",
                        "TD"
                    ]:
                        raise ValueError("The FBC '{}' you specified does not"
                            "exist!".format(fbc[node_iter][1]))
                    # increment counter
                    node_iter += 1
                else:
                    # if there is no FBC for the node, append an "x"
                    i.append("x")

                # make the full node string
                node_str = ""
                for k in i:
                    node_str += str(k) + " "
                # put the individual string to the global data structure
                #   holding all such strings
                self.n_head_str[node_str_iter] = node_str
                # increment counter
                node_str_iter += 1

        ######
        ## k exchange
        ######
        # prepare strings / lists for k_exchange
        for node in range(len(self.k_exchange[0])):
            self.k_exchange_str.append([])

        # initialize counter
        kex_iter = 0
        # if cads information not given, only use the k_exchange data
        if self.cads == None:
            # loop over all nodes and create strings not including cads
            #   information (if cads = None)
            for node in zip(self.k_exchange[0], self.k_exchange[1]):
                # create the k_exchange string
                node_str = str(node[0]) + ' ' + str(node[1])
                # 
                self.k_exchange_str[kex_iter] = node_str
                kex_iter += 1

        # loop over all nodes and create strings including cads information
        elif self.cads is not None:
            for node in zip(self.k_exchange[0], self.k_exchange[1], self.cads):
                node_str = (
                    str(node[0]) + ' ' +
                    str(node[1]) + ' ' +
                    str(node[2])
                )
                # put the individual string to the global data structure
                #   holding all such strings
                self.k_exchange_str[kex_iter] = node_str
                # increment counter
                kex_iter += 1

        # create strings for condl_data

        ### TODO

        # create strings for component data (nnodes, npipes, nlayers)
        self.components = (
            str(self.nnodes) + ' ' +
            str(self.npipes) + ' ' +
            str(self.nlay)
        )

        return
    
    def cfp(self):
        """
        Write the .cfp input file for MODFLOW-CFP

        Parameters
        ----------
        None

        Returns
        -------
        cfp : the list of strings representing the contents of the .cfp file
        """
        
        # create line 0 string
        in0 = '# CFP file - Mode'

        # create line 2 string depending on cads and fbc data given
        if self.cads is None and self.fbc is None:
            in2 = '# Conduit data for mode 1 and 3'
        elif self.cads is not None and self.fbc is None:
            in2 = 'CADS'
        elif self.cads is None and self.fbc is not None:
            in2 = 'FBC'
        elif self.cads is not None and self.fbc is not None:
            in2 = 'CADS FBC'

        # create remaining fixed strings
        in3 = "# (nnodes, npipes, nlayers)"
        in5 = "# Water temperature"
        in7 = ("# Node number, column, row, layer, neighbor node numbers,"
               "connected pipe numbers (no_n, mc, mr, ml, nb1, nb2, nb3,"
               "nb4, nb5, nb6, pb1, pb2, pb3, pb4, pb5, pb6)")
        in9 = "# Geoheight"
        in10 = "# Option 1: Node number (no_n), elevation (one line per node)"
        in11 = ("# Option 2: Total number of nodes (nnodes), elevation (one"
                "line for all nodes)")
        in13 = "# Pipe conductance (sa_exchange)"
        in15 = "# Convergence criterion (epsilon)"
        in17 = "# Maximum number of iterations (niter)"
        in19 = "# Step length of iterations (relax)"
        in21 = "# Print flag (p_nr)"
        in23 = "# Conduit parameters"
        in24 = ("# Pipe number, diameter, tortuosity, roughness, lower critical"
                "Reynolds number, upper critical Reynolds number (no_p, diameter,"
                "tortuosity, rheight, lcritrey_p, tcritrey_p)")
        in26 = "# Node heads (no_n, n_head)"
        in28 = ("# Node number, pipe conductance (no_n, k_exchange; sa_exchange"
                "= 0) or conduit wall permeability (sa_exchange = 1)")
        in30 = "# Conduit layers for mode 2 and 3"
        in31 = "# Number of conduit layers (ncl)"
        in33 = "# Layer numbers that are conduit layers (cl)"
        in35 = "# Mean water temperature of all conduit layers (ltemp)"
        in37 = "# Conduit layer parameters"
        in38 = ("# Mean void diameter, lower critical Reynolds number, upper"
                "critical Reynolds number (void, lcritrey_l, tcritrey_l")
        
        # create full content for mode 1
        if self.mode == '1':
            self.cfp = [in0, self.mode, in2, in3, self.components, in5, self.ltemp, in7, *self.nbr_str, in9, in10, 
                        in11, *self.geoheight_str, in13, self.sa_exchange, in15, self.epsilon, in17, self.niter, in19, self.relax, 
                        in21, self.p_nr, in23, in24, *self.cond_data_str, in26, *self.n_head_str, in28, *self.k_exchange_str]
        
        # create full content for mode 1 (NOT SUPPORTED AT THE MOMENT)
        elif self.mode == '2':
            self.cfp = [in0, self.mode, in30, in31, self.ncl, in33, self.cl, in35, self.ltemp, in37, in38, self.condl_data]
        
        # create full content for mode 1 (NOT SUPPORTED AT THE MOMENT)
        elif self.mode == '3':
            self.cfp = [in0, self.mode, in2, in3, self.components, in5, self.ltemp, in7, *self.nbr_str, in9, in10, 
                        in11, *self.geoheight_str, in13, self.sa_exchange, in15, self.epsilon, in17, self.niter, in19, self.relax, 
                        in21, self.p_nr, in23, in24, *self.cond_data_str, in26, *self.n_head_str, in28, *self.k_exchange_str, in30,
                        in31, self.ncl, in33, self.cl, in35, self.ltemp, in37, in38, self.condl_data]
        
        return self.cfp
