# -*- coding: utf-8 -*-
# Created on Wed Sep  1 16:20:47 2021
# @author: toj
"""

mesh class
==========


"""

from . import utils, implicit, improvement, contour, converter, quality, rays, curvature, visualize, check_numba
from sys import getsizeof
import scipy
import numpy as np
import os, copy, warnings, pickle, json, itertools

class mesh:  
    """
    The :class:`mesh` class stores the nodes (``NodeCoords``) and elements (or node connectivity, ``NodeConn``) as its primary attributes. 

    Parameters
    ----------
    NodeCoords : array_like, optional
        Node coordinates, by default None. Node coordinates should be formatted 
        as an nx3 or nx2 array of coordinates.
    NodeConn : list, array_like, optional
        Node connectivity of elements, by default None. Node connectivity
        is formatted as a 2D array or list of lists where each row (or inner list)
        is contains the node IDs of the nodes that make up the element. NodeConn
        can contain a uniform element type or a mix of different element types.
    Type : str or None, optional
        Mesh type, 'surf' for surface, 'vol' for volume, 'line' for line. If not
        provided, it will be determined automatically 
        (:meth:`mesh.identify_type`), by default None
    verbose : bool, optional
        If true, some operations will print activity or other information, 
        by default True

    Attributes
    ----------
    NodeCoords : array_like, optional
        Node coordinates, by default None. Node coordinates should be formatted 
        as an nx3 or nx2 array of coordinates.
    NodeConn : list, array_like, optional
        Node connectivity of elements, by default None. Node connectivity
        is formatted as a 2D array or list of lists where each row (or inner list)
        is contains the node IDs of the nodes that make up the element. NodeConn
        can contain a uniform element type or a mix of different element types.
    Type : str or None, optional
        Mesh type, 'surf' for surface, 'vol' for volume, 'line' for line. If not
        provided, it will be determined automatically 
        (:meth:`mesh.identify_type`), by default None
    verbose : bool
        Verbosity mode of the mesh. If True, some operations will print activity or other information, 
        by default True
    NodeData : dict
        Node data dictionary for storing scalar or vector data associated with 
        each node in the mesh. Each entry should be an array_like with the same
        length as the number of nodes in the mesh. When using :meth:`mesh.write`, 
        this data will be transferred to the written file if supported by that
        file type.
    ElemData : dict
        Element data dictionary for storing scalar or vector data associated with 
        each element in the mesh. Each entry should be an array_like with the same
        length as the number of elements in the mesh. When using :meth:`mesh.write`, 
        this data will be transferred to the written file if supported by that
        file type.
    NodeSets : dict
        Dictionary used for creating named sets of nodes. Each entry should 
        be a set (or array_like) of node numbers.
    ElemSets : dict
        Dictionary used for creating named sets of elements. Each entry should 
        be a set (or array_like) of element numbers.
    FaceSets : dict
        Dictionary used for creating named sets of faces. Each entry should 
        be a set (or array_like) of face numbers.
    EdgeSets : dict
        Dictionary used for creating named sets of edges. Each entry should 
        be a set (or array_like) of edge numbers.

    """    

    def __init__(self, NodeCoords=None, NodeConn=None, Type=None, verbose=True):
        # Primary attributes
        if NodeCoords is None:
            self.NodeCoords = np.empty((0,3))
        else:
            if not isinstance(NodeCoords, (list,np.ndarray,tuple)):
                raise ValueError(f'NodeCoords must be a list, np.ndarray or tuple, not {str(type(NodeCoords)):s}.')
            self.NodeCoords = NodeCoords

        if NodeConn is None:
            self.NodeConn = []
        else:
            if not isinstance(NodeConn, (list,np.ndarray,tuple)):
                raise ValueError(f'NodeConn must be a list, np.ndarray or tuple, not {str(type(NodeConn)):s}.')
            self.NodeConn = NodeConn

        if Type is None:
            self.Type = self.identify_type()
        else:
            self.Type = Type

        # Mesh settings
        self.verbose = verbose

        # Properties:
        self._ElemType = []
        self._MeshNodes = None
        self._Surface = None
        self._SurfConn = None
        self._SurfNodes = None
        self._Boundary = None
        self._BoundaryConn = None
        self._BoundaryNodes = None
        self._NodeNeighbors = []
        self._ElemNeighbors = []
        self._ElemConn = []
        self._SurfNodeNeighbors = []
        self._SurfElemConn = []
        self._ElemNormals = []
        self._NodeNormals = []
        self._Centroids = np.empty((0,3))
        self._Faces = []  
        self._FaceConn = [] 
        self._FaceElemConn = [] # For each face, gives the indices of connected elements (nan -> surface)
        self._Edges = []    
        self._EdgeConn = []
        self._EdgeElemConn = []
        self._NodeNormalsMethod = 'Angle'
        self._bounds = None
        self._aabb = None
        self._mvbb = None
        
        # Sets:
        self.NodeSets = {}
        self.ElemSets = {}
        self.EdgeSets = {}
        self.FaceSets = {}

        # Data:
        self.NodeData = {}
        self.ElemData = {}
        
        self._printlevel = 0
    def __sizeof__(self):
        size = 0
        # Base attributes
        size += getsizeof(self.NodeCoords)
        size += getsizeof(self.NodeConn)
        size += getsizeof(self.Type)
        
        # Property attributes
        size += getsizeof(self._Faces)
        size += getsizeof(self._FaceConn)
        size += getsizeof(self._FaceElemConn)
        size += getsizeof(self._Edges)
        size += getsizeof(self._EdgeConn)
        size += getsizeof(self._EdgeElemConn)
        size += getsizeof(self._SurfConn)
        size += getsizeof(self._NodeNeighbors)
        size += getsizeof(self._ElemConn)
        size += getsizeof(self._SurfNodeNeighbors)
        size += getsizeof(self._SurfElemConn)
        size += getsizeof(self._ElemNormals)
        size += getsizeof(self._NodeNormals)
        size += getsizeof(self._Centroids)

        # Sets & Data
        size += getsizeof(self.NodeSets)
        size += getsizeof(self.EdgeSets)
        size += getsizeof(self.FaceSets)
        size += getsizeof(self.ElemSets)
        size += getsizeof(self.NodeData)
        size += getsizeof(self.ElemData)


        return size
    def __repr__(self):
        if self.Type.lower() in ('surf', 'surface'):
            Type = 'Surface'
        elif self.Type in ('vol', 'volume'):
            Type = 'Volume'
        else:
            Type = 'Unknown'
        return 'Mesh Object\nType: {0:s}\n{1:d} Nodes\n{2:d} Elements'.format(Type,self.NNode,self.NElem)
    def __iter__(self):
        return iter((self.NodeCoords,self.NodeConn))
    
    # Properties
    @property
    def points(self):
        """ Alias for ``NodeCoords`` """
        return self.NodeCoords
    @points.setter
    def points(self,NodeCoords):
        self.NodeCoords = NodeCoords
    @property
    def cells(self):
        """ Alias for ``NodeConn`` """
        return self.NodeConn
    @cells.setter
    def cells(self,NodeConn):
        self.NodeConn = NodeConn
    @property 
    def ND(self):
        """
        Number of spatial dimensions. This is based on how many components each
        node coordinate has.
        """
        return np.shape(self.NodeCoords)[1]
    @property
    def NNode(self):
        """
        Number of nodes in the mesh.
        """        
        return len(self.NodeCoords)
    @property
    def NElem(self):
        """
        Number of elements in the mesh.
        """   
        return len(self.NodeConn)
    @property
    def NEdge(self):
        """
        Number of edges in the mesh. If edges haven't been determined yet, they 
        will be. 
        """   
        return len(self.Edges)
    @property
    def NFace(self):
        """
        Number of faces in the mesh. If faces haven't been determined yet, they 
        will be. 
        """  
        return len(self.Faces)
    @property
    def Faces(self):
        """
        Element faces. Each face is defined as a list of node indices.
        """        
        if len(self._Faces) == 0:
            if self.verbose: 
                print('\n'+'\t'*self._printlevel+'Identifying element faces...',end='')
                self._printlevel+=1

            self._Faces, self._FaceConn, self._FaceElemConn = self._get_faces()

            if self.verbose: 
                self._printlevel-=1
                print('Done', end='\n'+'\t'*self._printlevel)
        return self._Faces
    @property
    def FaceConn(self):
        """
        Element-face connectivity. For each element, lists the connected faces.
        See :ref:`connectivity` for more info.
        """
        if len(self._FaceConn) == 0:
            if self.verbose: 
                print('\n'+'\t'*self._printlevel+'Identifying element-face connectivity...',end='')
                self._printlevel+=1

            self._Faces, self._FaceConn, self._FaceElemConn = self._get_faces()
            
            if self.verbose: 
                self._printlevel-=1
                print('Done', end='\n'+'\t'*self._printlevel)
        return self._FaceConn
    @property
    def FaceElemConn(self):
        """
        Face-element connectivity. For each face, lists the connected elements.
        See :ref:`connectivity` for more info.
        """
        if len(self._FaceElemConn) == 0:
            if self.verbose: 
                print('\n'+'\t'*self._printlevel+'Identifying element face-element connectivity...',end='')
                self._printlevel+=1

            self._Faces, self._FaceConn, self._FaceElemConn = self._get_faces()
            
            if self.verbose: 
                self._printlevel-=1
                print('Done', end='\n'+'\t'*self._printlevel)
        return self._FaceElemConn
    @property
    def Edges(self):
        """
        Element edges. Each edge is defined as a list of node indices.
        """        
        if len(self._Edges) == 0:
            if self.verbose: 
                print('\n'+'\t'*self._printlevel+'Identifying element edges...',end='')
                self._printlevel+=1

            self._Edges, self._EdgeConn, self._EdgeElemConn = self._get_edges()

            if self.verbose: 
                self._printlevel-=1
                print('Done', end='\n'+'\t'*self._printlevel)
        return self._Edges
    @property
    def EdgeConn(self):
        """
        Element-edge connectivity. For each element, lists the connected edges.
        See :ref:`connectivity` for more info.
        """
        if len(self._EdgeConn) == 0:
            if self.verbose: 
                print('\n'+'\t'*self._printlevel+'Identifying element-edge connectivity...',end='')
                self._printlevel+=1

            self._Edges, self._EdgeConn, self._EdgeElemConn = self._get_edges()
            
            if self.verbose: 
                self._printlevel-=1
                print('Done', end='\n'+'\t'*self._printlevel)
        return self._EdgeConn
    @property
    def EdgeElemConn(self):
        """
        Edge-element connectivity. For each edge, lists the connected elements.
        See :ref:`connectivity` for more info.
        """
        if len(self._EdgeElemConn) == 0:
            if self.verbose: 
                print('\n'+'\t'*self._printlevel+'Identifying element edge-element connectivity...',end='')
                self._printlevel+=1

            self._Edges, self._EdgeConn, self._EdgeElemConn = self._get_edges()
            
            if self.verbose: 
                self._printlevel-=1
                print('Done', end='\n'+'\t'*self._printlevel)
        return self._EdgeElemConn
    @property
    def MeshNodes(self):
        """
        Array of node IDs contained within the mesh. If all nodes 
        are connected to elements, this will just be equivalent to
        `np.arange(m.NNode)`,  but if there are free nodes disconnected 
        from any elements, those nodes will be excluded.
        """ 
        if self._MeshNodes is None:
            if self.verbose: 
                print('\n'+'\t'*self._printlevel+'Identifying mesh nodes...',end='')
                self._printlevel += 1
            if type(self.NodeConn) is np.ndarray:
                self._MeshNodes = np.unique(self.NodeConn)
            else:
                self._MeshNodes = np.unique(np.fromiter(itertools.chain.from_iterable(self.NodeConn), np.int64))
            self._MeshNodes = np.array(list({i for elem in self.NodeConn for i in elem}))
            if self.verbose: 
                print('Done', end='\n'+'\t'*self._printlevel)
                self._printlevel -= 1
        MeshNodes = self._MeshNodes
        return MeshNodes    
    @property
    def SurfConn(self):
        """
        Node connectivity for the surface mesh. If the mesh is already a surface, this is the same as ``NodeConn``.
        """        
        if self.Type == 'surf':
            SurfConn = self.NodeConn
        else:
            if self._SurfConn is None:
                if self.verbose: print('\n'+'\t'*self._printlevel+'Identifying surface...',end='')
                self._SurfConn = converter.solid2surface(*self)
                if self.verbose: print('Done', end='\n'+'\t'*self._printlevel)
            SurfConn = self._SurfConn
        return SurfConn
    @property
    def SurfNodes(self):
        """
        Array of node IDs on the surface of a mesh.
        """ 
        if self._SurfNodes is None:
            if self.verbose: 
                print('\n'+'\t'*self._printlevel+'Identifying surface nodes...',end='')
                self._printlevel += 1
            if type(self.SurfConn) is np.ndarray:
                self._SurfNodes = np.unique(self.SurfConn)
            else:
                self._SurfNodes = np.unique(np.fromiter(itertools.chain.from_iterable(self.SurfConn),np.int64))
            if self.verbose: 
                print('Done', end='\n'+'\t'*self._printlevel)
                self._printlevel -= 1
        SurfNodes = self._SurfNodes
        return SurfNodes
    @property
    def Surface(self):
        """
        :class:`mesh` object representation of the surface mesh. 
        ``Surface.NodeCoords`` and ``Surface.NodeConn`` are aliases of 
        ``NodeCoords`` and ``SurfConn``, so changes to one will change the 
        other, however some operations may break this link. 
        """
        if self.Type != 'surf':
            if self._Surface is None:
                self._Surface = mesh(self.NodeCoords, self.SurfConn, 'surf', verbose=self.verbose)
            surf = self._Surface
        else:
            surf = self
        return surf
    @property
    def BoundaryConn(self):
        """
        Node connectivity for the boundary mesh of a surface.
        """        
        if self._BoundaryConn is None:
            if self.verbose: print('\n'+'\t'*self._printlevel+'Identifying boundary...',end='')
            if self.Type == 'vol':
                self._BoundaryConn = converter.surf2edges(*self.Surface, ElemType='surf')
            elif self.Type == 'surf':
                self._BoundaryConn = converter.surf2edges(*self, ElemType='surf')
            elif self.Type == 'line':
                self._BoundaryConn = self.NodeConn
            else:
                raise ValueError('Invalid Type.')
            if self.verbose: print('Done', end='\n'+'\t'*self._printlevel)
        BoundaryConn = self._BoundaryConn
        return BoundaryConn
    @property
    def BoundaryNodes(self):
        """
        Array of node IDs on the boundary of a surface.
        """ 
        if self._BoundaryNodes is None:
            if self.verbose: 
                print('\n'+'\t'*self._printlevel+'Identifying boundary nodes...',end='')
                self._printlevel += 1
            self._BoundaryNodes = np.array(list({i for elem in self.BoundaryConn for i in elem}))
            if self.verbose: 
                print('Done', end='\n'+'\t'*self._printlevel)
                self._printlevel -= 1
        BoundaryNodes = self._BoundaryNodes
        return BoundaryNodes
    @property
    def Boundary(self):
        """
        :class:`mesh` object representation of the boundary mesh. 
        ``Boundary.NodeCoords`` and ``Boundary.NodeConn`` are aliases of 
        ``NodeCoords`` and ``BoundaryConn``, so changes to one will change the 
        other, however some operations may break this link. Volume (Type='vol')
        or closed surface meshes will have no Boundary and this mesh will be 
        empty.
        """
        if self.Type != 'line':
            if self._Boundary is None:
                self._Boundary = mesh(self.NodeCoords, self.BoundaryConn, 'line', verbose=self.verbose)
            surf = self._Boundary
        else:
            surf = self
        return surf
    @property
    def NodeNeighbors(self):
        """
        Node neighbors. For each node, lists adjacent nodes.
        See :ref:`connectivity` for more info.
        """
        if self._NodeNeighbors == []:
            if self.verbose: print('\n'+'\t'*self._printlevel+'Identifying volume node neighbors...',end='')
            self._NodeNeighbors = utils.getNodeNeighbors(*self,ElemType=self.Type)
            if self.verbose: print('Done', end='\n'+'\t'*self._printlevel)
        return self._NodeNeighbors
    @property
    def ElemNeighbors(self):
        """
        Element neighbors. For each element, lists adjacent elements.
        See :ref:`connectivity` for more info.
        """
        if self._ElemNeighbors == []:
            if self.verbose: print('\n'+'\t'*self._printlevel+'Identifying element neighbors...',end='')
            if self.Type == 'surf':
                mode = 'edge'
            elif self.Type == 'vol':
                mode = 'face'
            self._ElemNeighbors = utils.getElemNeighbors(*self, mode=mode)
            if self.verbose: print('Done', end='\n'+'\t'*self._printlevel)
        return self._ElemNeighbors
    @property
    def ElemConn(self):
        """ 
        Node-Element connectivity. For each node, lists the connected elements.
        See :ref:`connectivity` for more info.
        """
        if self._ElemConn == []:
            if self.verbose: print('\n'+'\t'*self._printlevel+'Identifying volume node element connectivity...',end='')
            self._ElemConn = utils.getElemConnectivity(*self)
            if self.verbose: print('Done', end='\n'+'\t'*self._printlevel)
        return self._ElemConn
    @property
    def SurfNodeNeighbors(self):
        """
        Node neighbors for the surface mesh.
        """
        if self._SurfNodeNeighbors == []:
            if self.verbose: 
                print('\n'+'\t'*self._printlevel+'Identifying surface node neighbors...',end='')
                self._printlevel+=1
            self._SurfNodeNeighbors = utils.getNodeNeighbors(self.NodeCoords,self.SurfConn)
            if self.verbose: 
                self._printlevel-=1
                print('Done', end='\n'+'\t'*self._printlevel)
        return self._SurfNodeNeighbors
    @property
    def SurfElemConn(self):
        """
        Node-Element connectivity for the surface mesh.
        """
        if self._SurfElemConn == []:
            if self.verbose: 
                print('\n'+'\t'*self._printlevel+'Identifying surface node element connectivity...',end='')
                self._printlevel+=1
            self._SurfElemConn = utils.getElemConnectivity(self.NodeCoords,self.SurfConn)
            if self.verbose: 
                self._printlevel-=1
                print('Done', end='\n'+'\t'*self._printlevel)
                
        return self._SurfElemConn
    @property
    def ElemNormals(self):
        """
        Surface element normal vectors. For volume meshes, these will 
        be calculated in reference to the surface mesh (:attr:`SurfConn`).
        """
        if np.size(self._ElemNormals) == 0:
            if self.verbose: 
                print('\n'+'\t'*self._printlevel+'Calculating surface element normals...',end='')
                self._printlevel+=1
            self._ElemNormals = utils.CalcFaceNormal(self.NodeCoords,self.SurfConn)
            if self.verbose: 
                self._printlevel-=1
                print('Done', end='\n'+'\t'*self._printlevel)
        return self._ElemNormals        
    @property
    def NodeNormalsMethod(self):
        """
        Sets the method for calculating surface node normals. By default, 
        "Angle". If the method gets changed, previously computed normal 
        vectors will be cleared. See :func:`~mymesh.utils.Face2NodeNormal` for options 
        and more details. 
        """
        return self._NodeNormalsMethod
    @NodeNormalsMethod.setter
    def NodeNormalsMethod(self,method):
        self._NodeNormals = []
        self._NodeNormalsMethod = method
    @property
    def NodeNormals(self):
        """
        Surface node normal vectors. Non-surface nodes will receive 
        [np.nan, np.nan, np.nan]. There are several methods for computing
        surface normal vectors at the nodes, the method to be used can be
        set with :attr:`NodeNormalsMethod`. See :func:`~mymesh.utils.Face2NodeNormal` 
        for more details. 
        """
        if np.size(self._NodeNormals) == 0:
            if self.verbose: 
                print('\n'+'\t'*self._printlevel+'Calculating surface node normals...',end='')
                self._printlevel+=1
            self._NodeNormals = utils.Face2NodeNormal(self.NodeCoords,self.SurfConn,self.SurfElemConn,self.ElemNormals,method=self.NodeNormalsMethod)
            if self.verbose: 
                self._printlevel-=1
                print('Done', end='\n'+'\t'*self._printlevel)
        return self._NodeNormals
    @property
    def Centroids(self):
        """ Element centroids. """
        if np.size(self._Centroids) == 0:
            if self.verbose: print('\n'+'\t'*self._printlevel+'Calculating element centroids...',end='')
            self._Centroids = utils.Centroids(*self)
            if self.verbose: print('Done', end='\n'+'\t'*self._printlevel)
        return self._Centroids
    @property
    def EulerCharacteristic(self):
        """ 
        Topological Euler characteristic number. For volume meshes, the surface mesh is used. To prevent unattached nodes from influencing
        the vertex count, vertices are counted as the number of unique nodes
        referenced in :attr:`mesh.Edges`.

        .. math:: \\chi = V-E+F

        E: number of edges

        V: number of vertices

        F: number of faces

        """
        if self.Type == 'vol':
            E = self.Surface.NEdge
            V = len(self.SurfNodes)
            F = self.Surface.NFace
        else:
            E = self.NEdge
            V = len(self.SurfNodes)
            F = self.NFace

        return V - E + F
    @property
    def Genus(self):
        """
        Topological genus calculated from the Euler characteristic. For volume
        meshes, the surface mesh is used.

        .. math:: g = -(\\chi - 2)/2

        """
        # Check for boundary edges
        if len(self.Surface.BoundaryConn) != 0:
            b = len(utils.getConnectedNodes(self.NodeCoords, self.Surface.BoundaryConn))
        else:
            b = 0

        return -(self.EulerCharacteristic - 2 + b)/2
    @property
    def ElemType(self):
        """ Element Types. """
        if len(self._ElemType) == 0:
            if self.verbose: print('\n'+'\t'*self._printlevel+'Identifying element types...',end='')
            self._ElemType = utils.identify_elem(*self, Type=self.Type)
            if self.verbose: print('Done', end='\n'+'\t'*self._printlevel)
        return self._ElemType
    @property
    def bounds(self):
        """ Bounds of the mesh, formatted as [min(x), max(x), min(y), max(y), min(z), max(z)]. """
        if self._bounds is None:
            if self.verbose: print('\n'+'\t'*self._printlevel+'Identifying bounds...',end='')
            self._bounds = np.array([np.min(self.NodeCoords[self.MeshNodes,0]), np.max(self.NodeCoords[self.MeshNodes,0]),
                                     np.min(self.NodeCoords[self.MeshNodes,1]), np.max(self.NodeCoords[self.MeshNodes,1]),
                                     np.min(self.NodeCoords[self.MeshNodes,2]), np.max(self.NodeCoords[self.MeshNodes,2]),
                                     ])
            if self.verbose: print('Done', end='\n'+'\t'*self._printlevel)
        return self._bounds
    @property
    def aabb(self):
        """ Axis aligned bounding box of the mesh. """
        if self._aabb is None:
            if self.verbose: print('\n'+'\t'*self._printlevel+'Identifying axis aligned bounding box...',end='')
            self._aabb = utils.AABB(self.NodeCoords[self.MeshNodes])
            if self.verbose: print('Done', end='\n'+'\t'*self._printlevel)
        return self._aabb
    @property
    def mvbb(self):
        """ Minimum volume bounding box of the mesh. """
        if self._mvbb is None:
            if self.verbose: print('\n'+'\t'*self._printlevel+'Identifying minimum volume bounding box...',end='')
            self._mvbb = utils.MVBB(self.NodeCoords[self.MeshNodes])
            if self.verbose: print('Done', end='\n'+'\t'*self._printlevel)
        return self._mvbb
    
    
    # Methods
    ## Maintenance Methods
    def identify_type(self):
        """
        Classify the mesh as either a surface or volume.
        A mesh is classified as a volume mesh ('vol') if any elements are unambiguous 
        volume elements - pyramid (5 nodes), wedge (6), hexahedron (8), or if 
        any of a random sample of 10 elements (or all elements if NElem < 10) has
        a volume less than machine precision (``np.finfo(float).eps``). 
        Alternatively, a surface mesh ('surf') is identified if any of the elements is 
        a triangle (3 nodes). In the case of a mesh containing both triangular
        and volume elements, the mesh will be classified arbitrarily by whichever
        appears first in NodeConn. 

        This approach has a chance of mislabeling the mesh in some rare or 
        non-standard scenarios, but attempts to be as efficient as possible
        to minimize overhead when creating a mesh. Potentially ambiguous meshes
        are:

        - 
            Meshes containing both triangular elements and volume elements 
            (this should generally be avoided as most functions aren't set up
            to handle that case).
        - 
            Tetrahedral meshes with many degenerate elements with 
            abs(vol) < machine precision. 
        - Quadrilateral meshes with non-planar elements.

        In such cases, Type should be specified explicitly when creating the mesh
        object.

        Returns
        -------
        Type : str
            Mesh type, either 'surf', 'vol', or 'empty'.
        """        

        Type = utils.identify_type(*self)

        return Type
    def validate(self):
        """
        Check validity of the mesh. This will verify that ``NodeCoords`` and
        ``NodeConn`` are of an appropriate type, confirm the mesh is non-empty, 
        check that elements don't reference non-existant nodes, and that the 
        ``Type`` is a valid option ('vol' or 'surf'). If any of these checks
        fail, an assertion error will be raised. Additionally, a warning will
        be issued if a volume mesh has any inverted elements.
        """

        assert isinstance(self.NodeCoords, (list,np.ndarray,tuple)), f'Invalid type:{str(type(self.NodeCoords)):s} for mesh.NodeCoords.'
        assert len(self.NodeCoords) > 0, 'Undefined Node Coordinates'
        assert isinstance(self.NodeCoords, (list,np.ndarray,tuple)), f'Invalid type:{str(type(self.NodeCoords)):s} for mesh.NodeConn.'
        assert len(self.NodeConn), 'Undefined Node Connectivity'
        assert max([max(elem) for elem in self.NodeConn]) <= len(self.NodeCoords), 'NodeConn references undefined nodes'
        
        assert self.Type in ('vol', 'surf'), 'Invalid mesh type.'

        if self.Type == 'vol':
            v = quality.Volume(*self)
            if np.nanmin(v) < 0:
                warnings.warn(f'Mesh has {np.sum(v < 0):d} inverted elements.')

    def reset(self,properties=None,keep=None):
        """
        Reset some or all properties. If no arguments are provided,
        all cached mesh properties will be reset. 

        Parameters
        ----------
        properties : NoneType, str, or list, optional
            If specified as a string or list of strings, will reset the properties specified by those names. By default, all properties
            other than those specified by ``keep`` will be reset.
        keep : NoneType, str or list, optional
            If specified as a string or list of strings, the corresponding
            properties will not be reset. If the same entry is found in
            ``properties`` and ``keep``, the former takes precedence and
            the property will be cleared. By default, None.

        """        
        # Reset calculated mesh attributes
        if type(keep) is str:
            keep = [keep]
        elif keep is None:
            keep = []
        if properties == None:
            if 'ElemType' not in keep: self._ElemType = []
            if 'SurfConn' not in keep: self._SurfConn = None
            if 'SurfNodes' not in keep: self._SurfNodes = None
            if 'Surface' not in keep: self._Surface = None
            if 'BoundaryConn' not in keep: self._BoundaryConn = None
            if 'BoundaryNodes' not in keep: self._BoundaryNodes = None
            if 'NodeNeighbors' not in keep: self._NodeNeighbors = []
            if 'ElemConn' not in keep: self._ElemConn = []
            if 'SurfNodeNeighbors' not in keep: self._SurfNodeNeighbors = []
            if 'SurfElemConn' not in keep: self._SurfElemConn = []
            if 'ElemNormals' not in keep: self._ElemNormals = []
            if 'NodeNormals' not in keep: self._NodeNormals = []
            if 'Centroids' not in keep: self._Centroids = []
            if 'Edges' not in keep: self._Edges = []
            if 'Edges' not in keep or 'EdgeConn' not in keep: self._EdgeConn = []
            if 'Edges' not in keep or 'EdgeElemConn' not in keep: self._EdgeElemConn = [] 
            if 'Faces' not in keep: self._Faces = []
            if 'Faces' not in keep or 'FaceConn' not in keep: self._FaceConn = []
            if 'Faces' not in keep or 'FaceElemConn' not in keep: self._FaceElemConn = [] 
            if 'Surface' not in keep: self._Surface = None
            
        elif type(properties) is list:
            for prop in properties:
                if prop[0] != '_':
                    prop = '_'+prop
                setattr(self,prop,[])
        elif type(properties) is str:
            if properties[0] != '_':
                properties = '_'+properties
            setattr(self,properties,[])
        else:
            raise Exception('Invalid input.')
    def cleanup(self,tol=1e-10):

        # TODO: This needs to be improved so other variables that point to nodes or elements are updated accordingly
        
        self.reset()
        self.NodeCoords,self.NodeConn,idx,newIds = utils.DeleteDuplicateNodes(self.NodeCoords,self.NodeConn,tol=tol,return_idx=True,return_inv=True)
        for key in self.NodeData.keys():
            self.NodeData[key] = np.asarray(self.NodeData[key])[idx]
            
        self.NodeCoords,self.NodeConn,OrigIds = utils.RemoveNodes(self.NodeCoords,self.NodeConn)
        for key in self.NodeData.keys():
            self.NodeData[key] = np.asarray(self.NodeData[key])[OrigIds]
    def copy(self):
        """
        Create a copy of the mesh. The copied mesh will be independent, with 
        no references to the original mesh, meaning changes to one mesh won't
        influence the other.

        Returns
        -------
        M : mymesh.mesh
            Copied mesh
        """        
        M = mesh(copy.copy(self.NodeCoords), copy.copy(self.NodeConn), self.Type)
        
        M._Faces = copy.copy(self._Faces)
        M._FaceConn = copy.copy(self._FaceConn)
        M._FaceElemConn = copy.copy(self._FaceElemConn)
        M._Edges = copy.copy(self._Edges)
        
        M.NodeSets = copy.copy(self.NodeSets)
        M.EdgeSets = copy.copy(self.EdgeSets)
        M.FaceSets = copy.copy(self.FaceSets)
        M.ElemSets = copy.copy(self.ElemSets)

        M.NodeData = copy.deepcopy(self.NodeData)
        M.ElemData = copy.deepcopy(self.ElemData)
        
        M._SurfConn = copy.copy(self._SurfConn)
        M._NodeNeighbors = copy.copy(self._NodeNeighbors)
        M._ElemConn = copy.copy(self._ElemConn)
        M._SurfNodeNeighbors = copy.copy(self._SurfNodeNeighbors)
        M._SurfElemConn = copy.copy(self._SurfElemConn)
        M._ElemNormals = copy.copy(self._ElemNormals)
        M._NodeNormals = copy.copy(self._NodeNormals)
        M._Centroids = copy.copy(self._Centroids)
        M.verbose = self.verbose
        
        return M
    
    # Modification Methods
    def addNodes(self,NodeCoords,NodeSet=None):
        """
        Add nodes to the mesh. These nodes will be appended to the end of the 
        coordinates array (:attr:`mesh.NodeCoords`).

        Parameters
        ----------
        NodeCoords : array_like
            Coordinates of the new node(s). This can either be a single node 
            (shape=(3,)) or multiple nodes (shape=(n,3)).
        NodeSet : str, optional
            If provided, name of a node set that the new nodes will be added to 
            in mesh.NodeSets[<NodeSet>], by default None.
        """   

        if len(np.shape(NodeCoords)) == 1:
            NodeCoords = [NodeCoords]
        nnode = self.NNode
        if type(self.NodeCoords) is np.ndarray:
            self.NodeCoords = np.vstack([self.NodeCoords, NodeCoords])
        else:
            if type(NodeCoords) is np.ndarray:
                NodeCoords = NodeCoords.tolist()
            elif type(NodeCoords) is not list:
                NodeCoords = list(NodeCoords)
            self.NodeCoords += NewCoords

        
        if NodeSet in self.NodeSets.keys():
            self.NodeSets[NodeSet] = set(self.NodeSets[NodeSet]).union(range(nnode,self.NNode))
        elif NodeSet:
            self.NodeSets[NodeSet] = set(range(nnode,self.NNode))

    def addFaces(self,NewFaces,FaceSet=None):
        """
        Add new faces to the mesh. These faces will be appended to the end of
        the list of faces (:meth:`mesh.Faces`). This should be done very carefully and
        only used for advanced manipulation of the mesh, as added faces may not 
        make sense with the rest of the mesh. If the mesh has been changed and
        updated faces are desired, it's safest to use :meth:`mesh.reset` then
        recompute the faces with (:meth:`mesh.Faces`). Note that if Faces hasn't
        been referenced before (``mesh._Faces==[]``) they will be obtained in
        this function, so if the new faces are already part of the mesh, this may 
        produce redundant faces.
        

        Parameters
        ----------
        NewFaces : array_like
            Node connectivities of the new face(s). This can either be a single 
            face (shape=(1,m)) or multiple faces (shape=(n,m) or list of lists 
            with length n for mixed element type faces). If a single face, it
            must be a 2D array or list of a single list (i.e. [[a,b,c]]).
        FaceSet : str, optional
            If provided, name of a face set that the new faces will be added to 
            in mesh.FaceSets[<FaceSet>], by default None.
        """  
        nface = self.NFace      
        if type(self._Faces) is np.ndarray:
            # If faces are an array, see if the new faces are compatible, if not convert to list of lists
            try:
                newshape = np.shape(NewFaces)
            except:
                self._Faces = self._Faces.tolist()
                newshape = (len(NewFaces),-1)
        else:
            if type(NewFaces) is np.ndarray:
                NewFaces = NewFaces.tolist()
            elif type(NewFaces) is not list:
                NewFaces = list(NewFaces)
            newshape = (len(NewFaces),-1)

        if len(newshape) != 2:
            raise ValueError('NewFaces must be a 2D array or list of lists')
        
        if newshape[1] == -1:
            # List concatenation
            self._Faces += NewFaces
        else:
            self._Faces = np.vstack([self.Faces, NewFaces])
        
        
        if FaceSet in self.FaceSets.keys():
            self.FaceSets[FaceSet] = set(self.FaceSets[FaceSet]).union(range(nface,self.NFace))
        elif FaceSet:
            self.FaceSets[FaceSet] = set(range(nface,self.NFace))

    def addEdges(self,NewEdges,EdgeSet=None):
        """
        Add new edges to the mesh. These edges will be appended to the end of
        the list of edges (:meth:`mesh.Edges`). This should be done very carefully and
        only used for advanced manipulation of the mesh, as added edges may not 
        make sense with the rest of the mesh. If the mesh has been changed and
        updated edges are desired, it's safest to use :meth:`mesh.reset` then
        recompute the edges with (:meth:`mesh.Edges`). Note that if Edges hasn't
        been referenced before (``mesh._Edges==[]``) they will be obtained in
        this function, so if the new edges are already part of the mesh, this may 
        produce redundant edges.
        

        Parameters
        ----------
        NewEdges : array_like
            Node connectivities of the new edge(s). This can either be a single 
            edge (shape=(1,m)) or multiple edges (shape=(n,m) or list of lists 
            with length n for mixed element type edges). If a single edge, it
            must be a 2D array or list of a single list (i.e. [[a,b,c]]).
        EdgeSet : str, optional
            If provided, name of a edge set that the new edges will be added to 
            in mesh.EdgeSets[<EdgeSet>], by default None.
        """  

        nedge = self.NEdge   
        if type(self._Edges) is np.ndarray:
            # If edges are an array, see if the new edges are compatible, if not convert to list of lists
            try:
                newshape = np.shape(NewEdges)
            except:
                self._Edges = self._Edges.tolist()
                newshape = (len(NewEdges),-1)
        else:
            if type(NewEdges) is np.ndarray:
                NewEdges = NewEdges.tolist()
            elif type(NewEdges) is not list:
                NewEdges = list(NewEdges)
            newshape = (len(NewEdges),-1)

        if len(newshape) != 2:
            raise ValueError('NewEdges must be a 2D array or list of lists')
        
        if newshape[1] == -1:
            # List concatenation
            self._Edges += NewEdges
        else:
            self._Edges = np.vstack([self.Edges, NewEdges])
        
        
        if EdgeSet in self.EdgeSets.keys():
            self.EdgeSets[EdgeSet] = set(self.EdgeSets[EdgeSet]).union(range(nedge,self.NEdge))
        elif EdgeSet:
            self.EdgeSets[EdgeSet] = set(range(nedge,self.NEdge))

    def addElems(self,NodeConn,ElemSet=None,reset=True):
        """
        Add new elements to the mesh. These elements will be appended to the end 
        of the list of elements (:attr:`mesh.NodeConn`) and should reference 
        nodes that already exist in the mesh. Note that properties that are
        calculated on demand are not updated by this operation - it's safest
        to use the reset=True option or use :meth:`mesh.reset` after this 
        operation

        Parameters
        ----------
        NodeConn : array_like
            Node connectivities of the new element(s). This can either be a 
            single element (shape=(1,m)) or multiple elements (shape=(n,m) or 
            list of lists with length n for mixed element type elements). If a 
            single element, it must be a 2D array or list of a single list 
            (i.e. [[a,b,c]]).
        ElemSet : str, optional
            If provided, name of a element set that the new elements will be 
            added to in mesh.ElemSets[<ElemSet>], by default None.
        reset : bool
            If True, will reset all cached mesh properties (e.g. Faces, 
            ElemNeighbors)
        """  
        nelem = self.NElem   
        if type(self.NodeConn) is np.ndarray:
            # If NodeConn is an array, see if the new elements are compatible, if not convert to list of lists
            try:
                newshape = np.shape(NodeConn)
            except:
                self.NodeConn = self.NodeConn.tolist()
                newshape = (len(NodeConn),-1)
        else:
            if type(NodeConn) is np.ndarray:
                NodeConn = NodeConn.tolist()
            elif type(NodeConn) is not list:
                NodeConn = list(NodeConn)
            newshape = (len(NodeConn),-1)

        if len(newshape) != 2:
            raise ValueError('NodeConn must be a 2D array or list of lists')
        
        if newshape[1] == -1:
            # List concatenation
            self.NodeConn += NodeConn
        else:
            self.NodeConn = np.vstack([self.NodeConn, NodeConn])
        
        
        if ElemSet in self.ElemSets.keys():
            self.ElemSets[ElemSet] = set(self.ElemSets[ElemSet]).union(range(nelem,self.NElem))
        elif ElemSet:
            self.ElemSets[ElemSet] = set(range(nelem,self.NElem))
        self._ElemType = [] # resetting, will be recalculated if requested
        if reset:
            self.reset()

    def removeElems(self, ElemIds):
        
        KeepSet = set(range(self.NElem)).difference(ElemIds)
        KeepIds = np.array(list(KeepSet))
        if len(KeepIds) == 0:
            if type(self.NodeConn) is np.ndarray:
                self.NodeConn = np.empty((0,np.shape(self.NodeConn)[1]))
            else:
                self.NodeConn = []
        elif type(self.NodeConn) is np.ndarray:
            self.NodeConn = self.NodeConn[KeepIds]
        else:
            self.NodeConn = [self.NodeConn[i] for i in KeepIds]

        for key in self.ElemData.keys():
            if len(KeepIds) > 0:
                self.ElemData[key] = np.asarray(self.ElemData[key])[KeepIds]
            else:
                shape = list(np.shape(self.ElemData[key]))
                shape[0] = 0
                self.ElemData[key] = np.empty(shape)

        # TODO: remove from ElemSets
        self.reset()

    def merge(self,Mesh2,cleanup=True,tol=1e-14):
        """
        Merge multiple meshes together into the current mesh.

        Parameters
        ----------
        Mesh2 : mymesh.mesh or list
            Second mesh, or list of meshes, to merge with the current mesh.
        cleanup : bool, optional
            Determines whether or not to :meth:``~mesh.cleanup`` the merged
            mesh, by default True.
        tol : float, optional
            Cleanup tolerance for identifying duplicate nodes (see 
            :meth:``~mesh.cleanup``), by default 1e-14
        
        """        
        if type(Mesh2) is list:
            MeshList = Mesh2
        else:
            MeshList = [Mesh2]
        for M in MeshList:
            m = M.copy()
            # Original Stats
            NNode = self.NNode
            NElem = self.NElem
            
            # Add Nodes
            if len(M.NodeSets) > 1:
                keys = list(m.NodeSets.keys())
                for i in range(len(keys)):
                    keyName = keys[i]
                    self.addNodes([m.NodeCoords[node] for node in m.NodeSets[keyName]],NodeSet=keyName)
            else:
                self.addNodes(m.NodeCoords)

            # Add Elems
            if len(m.ElemSets) > 1:
                keys = list(m.ElemSets.keys())
                for i in range(len(keys)):
                    keyName = keys[i]
                    self.addElems([[node+NNode for node in m.NodeConn[elem]] for elem in m.ElemSets[keyName]],ElemSet=keyName)
            else:
                self.addElems([[node+NNode for node in m.NodeConn[elem]] for elem in range(len(m.NodeConn))])
                    
            # Add Node and Element Data
            for key in self.NodeData.keys():
                if not key in m.NodeData.keys():
                    m.NodeData[key] = np.nan * np.ones_like(self.NodeData[key])[:m.NNode,...]
                if len(np.shape(self.NodeData[key])) == 1:
                    # 1D data
                    self.NodeData[key] = np.append(self.NodeData[key], m.NodeData[key])
                else: 
                    self.NodeData[key] = np.vstack([self.NodeData[key], m.NodeData[key]])

            for key in self.ElemData.keys():
                if not key in m.ElemData.keys():
                    m.ElemData[key] = np.nan * np.ones_like(self.ElemData[key])[:m.NElem,...]
                if len(np.shape(self.ElemData[key])) == 1:
                    # 1D data
                    self.ElemData[key] = np.append(self.ElemData[key], m.ElemData[key])
                else: 
                    self.ElemData[key] = np.vstack([self.ElemData[key], m.ElemData[key]])

        # Cleanup
        if cleanup:
            self.cleanup(tol=tol)
    def RenumberNodesBySet(self):
        # Re-organize the order of nodes based on their node sets and make required adjustments to other stored values
        setkeys = self.NodeSets.keys()
        # newIds is a list of node ids where the new index is located at the old index
        newIds = np.repeat(np.nan,len(self.NodeCoords))
        end = 0
        # Renumber nodes in node sets
        for key in setkeys:
            start = end
            end += len(self.NodeSets[key])
            newIds[list(self.NodeSets[key])] = np.arange(start,end)
            self.NodeSets[key] = range(start,end)
            
        # Renumber any nodes that aren't in node sets
        newIds[np.isnan(newIds)] = np.arange(end,len(self.NodeCoords))
        self.NodeCoords, self.NodeConn, self._Faces = utils.RelabelNodes(self.NodeCoords, self.NodeConn, newIds, faces=self._Faces)
        
        self.reset(keep=['Faces','FaceElemConn','FaceConn'])
    def RenumberFacesBySet(self):
        setkeys = list(self.FaceSets.keys())
        
        if any([len(set(self.FaceSets[key1]).intersection(self.FaceSets[key2]))>0 for i,key1 in enumerate(setkeys) for key2 in setkeys[i+1:]]):
            raise Exception('There must be no overlap between FaceSets')
        
        
        # newIds is a list of face ids where the new index is located at the old index
        newIds = np.repeat(np.nan,len(self.Faces))
        end = 0
        # Renumber faces in face sets
        for key in setkeys:
            start = end
            end += len(self.FaceSets[key])
            newIds[list(self.FaceSets[key])] = np.arange(start,end,dtype=int)
            self.FaceSets[key] = range(start,end)
        # Renumber any faces that aren't in face sets
        newIds[np.isnan(newIds)] = np.arange(end,len(newIds),dtype=int)
        newIds = newIds.astype(int)

        # Reorder faces
        NewFaces = np.zeros(utils.PadRagged(self.Faces).shape,dtype=int)
        NewFaceElemConn = np.zeros(np.shape(self.FaceElemConn))

        NewFaces[newIds,:] = utils.PadRagged(self.Faces)
        NewFaceElemConn[newIds] = self.FaceElemConn


        NewFaceConn = newIds[utils.PadRagged(self.FaceConn)]
        
        self._Faces = utils.ExtractRagged(NewFaces,dtype=int)
        self._FaceElemConn = NewFaceElemConn
        self._FaceConn = utils.ExtractRagged(NewFaceConn,dtype=int)
    
    def CreateBoundaryLayer(self,nLayers,FixedNodes=set(),StiffnessFactor=1,Thickness=None,OptimizeTets=True,FaceSets='surf'):
        """
        Generate boundary layer elements.
        Based partially on Bottasso, C. L., & Detomi, D. (2002). A procedure for 
        tetrahedral boundary layer mesh generation. Engineering with Computers, 
        18(1), 66-79. https://doi.org/10.1007/s003660200006 :cite:p:`Bottasso2002`
        
        Currently surfaces must be strictly triangular.

        Parameters
        ----------
        nLayers : int
            Number of element layers to generate. 
        FixedNodes : set or list, optional
            Set of nodes that will be held fixed, by default set().
            It is not necessary to specify any fixed nodes, and by default 
            the starting nodes of the boundary layer will be held fixed.
        StiffnessFactor : int or float, optional
            Stiffness factor used for the spring network, by default 1
        Thickness : float or NoneType, optional
            Specified value for the maximum total thickness of the boundary layers. 
            If nLayers > 1, this thickness is subdivided by nLayers, by default None
        OptimizeTets : bool, optional
            If True, will perform tetrahedral mesh optimization
            (see improvement.TetOpt), by default True.
        FaceSets : str or list, optional
            FaceSet or list of FaceSets to generate boundary later elements on, by default ['surf'].
            While mesh.FaceSets can generally contain any element face, boundary layer face sets
            must be surface faces; however, the face ids contained within the face sets should index
            mesh.Faces, and not mesh.SurfConn. The default value of 'surf' can be used even if no 
            sets exist in mesh.FaceSets and will generate boundary layer elements along the entire 
            surface. If mesh.FaceSets is empty, or doesn't contain a key with the name 'surf', the
            surface mesh will be used, otherwise, mesh.FaceSets['surf'] will be used.
        """        
        if type(FixedNodes) != set:
            FixedNodes = set(FixedNodes)
        if type(FaceSets) is str: 
            FaceSets = [FaceSets]

        # Create first layer with 0 thickness
        NOrigElem = self.NElem
        OrigConn = copy.copy(self.NodeConn)
        self.NodeNormalsMethod = 'MostVisible'
        NodeNormals = self.NodeNormals
        surfconn = self.SurfConn
        surfnodes = set(np.unique(surfconn).tolist())
        
        if len(self.FaceSets) == 0:
            if len(FaceSets) > 1 or 'surf' not in FaceSets:
                raise Exception('Requested FaceSets are undefined.')
            ForceNodes = copy.copy(surfnodes)            

        else:
            ForceNodes = set()
            for key in FaceSets:
                if key not in self.FaceSets.keys():
                    raise Exception('Requested set "{:s}" is undefined.'.format(key))
                FaceIds = self.FaceSets[key]
                FaceNodes = set([n for i in FaceIds for n in self.Faces[i]])
                ForceNodes.update(FaceNodes)
            NoGrowthNodes = surfnodes.difference(ForceNodes)
            FixedNodes.update(NoGrowthNodes)

        newsurfconn = [[node+len(self.NodeCoords) for node in elem] for elem in surfconn]
        newsurfnodes = np.unique(newsurfconn)
        BLConn = [elem + newsurfconn[i] for i,elem in enumerate(surfconn)]
        self.addNodes(self.NodeCoords)
        self.addElems(BLConn)
        self.reset()

        FixedNodes.update(newsurfnodes)
        Forces = [[0,0,0] if i not in ForceNodes else -1*np.array(NodeNormals[i]) for i in range(self.NNode)]
        allnodes = set([n for elem in self.NodeConn for n in elem])
        FixedNodes.update(set(i for i in range(len(self.NodeCoords)) if i not in allnodes))
        Fixed = np.array([1 if i in FixedNodes else 0 for i in range(self.NNode)])

        # Oriented wedge->tet conversion -  (Bottasso & Detomi)
        # surfedges = converter.solid2edges(self.NodeCoords,surfconn)
        surfedges,surfedgeconn,surfedgeelem = converter.solid2edges(self.NodeCoords,newsurfconn,return_EdgeElem=True,return_EdgeConn=True)

        UEdges,idx,inv = converter.edges2unique(surfedges,return_idx=True,return_inv=True)
        UEdgeConn = inv[surfedgeconn]

        NodeEdges = [[] for i in self.NodeCoords]
        for i,e in enumerate(UEdges):
            NodeEdges[e[0]].append(i)
            NodeEdges[e[1]].append(i)
        
        oriented = np.zeros(len(UEdges)) # 1 will indicate that the edge will be oriented as is, -1 indicates a flip
        for i,node in enumerate(newsurfnodes):
            for edge in NodeEdges[node]:
                if oriented[edge] == 0:
                    if UEdges[edge][0] == node:
                        oriented[edge] = 1
                    else:
                        oriented[edge] = -1
        OrientedEdges = copy.copy(UEdges)
        OrientedEdges[oriented==-1] = np.fliplr(UEdges[oriented==-1])

        surfedges = np.array(surfedges)
        
        # Tetrahedronization:
        # For each triangle, ElemEdgeOrientations will have a 3 entries, corresponding to the orientation of the edges
        # For a particular edge in an element, True -> the oriented edge is oriented clockwise, False -> counterclockwise 
        ElemEdgeOrientations = (OrientedEdges[UEdgeConn] == surfedges[surfedgeconn])[:,:,0] 

        # The are 6 possible combinations
        Cases = -1*np.ones(len(surfconn))
        Cases[np.all(ElemEdgeOrientations==[True,True,False],axis=1)] = 1
        Cases[np.all(ElemEdgeOrientations==[True,False,True],axis=1)] = 2
        Cases[np.all(ElemEdgeOrientations==[True,False,False],axis=1)] = 3
        Cases[np.all(ElemEdgeOrientations==[False,True,True],axis=1)] = 4
        Cases[np.all(ElemEdgeOrientations==[False,True,False],axis=1)] = 5
        Cases[np.all(ElemEdgeOrientations==[False,False,True],axis=1)] = 6

        
        # Each triangle in surfconn lines up with the indices of wedges in BLConn
        ArrayConn = np.asarray(BLConn)
        TetConn = -1*np.ones((len(BLConn)*3,4))
        t1 = np.zeros((len(ArrayConn),4))
        t2 = np.zeros((len(ArrayConn),4))
        t3 = np.zeros((len(ArrayConn),4))
        # Case 1:
        t1[Cases==1] = ArrayConn[Cases==1][:,[0,1,2,5]]
        t2[Cases==1] = ArrayConn[Cases==1][:,[1,4,5,0]]
        t3[Cases==1] = ArrayConn[Cases==1][:,[0,3,4,5]]
        # Case 2:
        t1[Cases==2] = ArrayConn[Cases==2][:,[0,1,2,4]]
        t2[Cases==2] = ArrayConn[Cases==2][:,[0,4,2,3]]
        t3[Cases==2] = ArrayConn[Cases==2][:,[4,5,2,3]]
        # Case 3:
        t1[Cases==3] = ArrayConn[Cases==3][:,[0,1,2,4]]
        t2[Cases==3] = ArrayConn[Cases==3][:,[0,4,2,5]]
        t3[Cases==3] = ArrayConn[Cases==3][:,[0,4,5,3]]
        # Case 4:
        t1[Cases==4] = ArrayConn[Cases==4][:,[0,1,2,3]]
        t2[Cases==4] = ArrayConn[Cases==4][:,[1,2,3,5]]
        t3[Cases==4] = ArrayConn[Cases==4][:,[1,5,3,4]]
        # Case 5:
        t1[Cases==5] = ArrayConn[Cases==5][:,[0,1,2,5]]
        t2[Cases==5] = ArrayConn[Cases==5][:,[1,5,3,4]]
        t3[Cases==5] = ArrayConn[Cases==5][:,[0,1,5,3]]
        # Case 6:
        t1[Cases==6] = ArrayConn[Cases==6][:,[0,1,2,3]]
        t2[Cases==6] = ArrayConn[Cases==6][:,[1,2,3,4]]
        t3[Cases==6] = ArrayConn[Cases==6][:,[4,5,2,3]]
        
        TetConn[0::3] = t1
        TetConn[1::3] = t2
        TetConn[2::3] = t3
        TetConn = TetConn.astype(int).tolist()

        # RelevantElems = [elem for elem in self.NodeConn if not all([n in FixedNodes for n in elem])]
        RelevantElems = TetConn + [elem for elem in self.NodeConn if len(elem)==4]
        RelevantCoords,RelevantConn,NodeIds = converter.removeNodes(self.NodeCoords,RelevantElems) 

        # TetConn = converter.solid2tets(RelevantCoords,RelevantConn)
        RelevantNodeNeighbors = utils.getNodeNeighbors(RelevantCoords,RelevantConn)
        RelevantElemConn = utils.getElemConnectivity(RelevantCoords,RelevantConn)
        RelevantForces = np.asarray(Forces)[NodeIds]
        RelevantFixed = Fixed[NodeIds]
        RelevantFixedNodes = set(np.where(RelevantFixed)[0])
        NewCoords = np.asarray(self.NodeCoords)

        if Thickness:
            L0Override = Thickness
        else:
            L0Override = 'min'
        
        # Expand boundary layer
        NewRelevantCoords,U,(K,F) = improvement.SegmentSpringSmoothing(RelevantCoords,RelevantConn,
            RelevantNodeNeighbors,RelevantElemConn,StiffnessFactor=StiffnessFactor,
            FixedNodes=RelevantFixedNodes,Forces=RelevantForces,L0Override=L0Override,return_KF=True)

        if Thickness:
            # Find stiffness factor that gives desired thickness

            # Full solve:
            # def fun(k):
            #     NewRelevantCoords,_ = improvement.SegmentSpringSmoothing(RelevantCoords,TetConn,
            #                                 RelevantNodeNeighbors,RelevantElemConn,StiffnessFactor=k,
            #                                 FixedNodes=RelevantFixedNodes,Forces=RelevantForces,L0Override=L0Override)
            #     t = max(np.linalg.norm(U,axis=1))
            #     # print(k,t)
            #     return abs(Thickness - t)
            # res = scipy.optimize.minimize_scalar(fun,(StiffnessFactor,StiffnessFactor/10),tol=ThicknessTol,options={'maxiter':ThicknessMaxIter})

            # Scaled K matrix:
            # def fun(k):
            #     U = scipy.sparse.linalg.spsolve((k/StiffnessFactor)*K.tocsc(), F).toarray()
            #     t = max(np.linalg.norm(U,axis=1))
            #     print(k,t)
            #     return abs(Thickness - t)s
            # res = scipy.optimize.minimize_scalar(fun,(StiffnessFactor,StiffnessFactor/10),tol=ThicknessTol,options={'maxiter':ThicknessMaxIter})
            # k = res.x
            
            # Power Law:
            # t = max(np.linalg.norm(NewCoords[ForceNodes] - NewCoords[SurfNodes],axis=1))
            t = np.nanmax(np.linalg.norm(U,axis=1))
            alpha = t*StiffnessFactor
            k = alpha*Thickness**-1
            U2 = scipy.sparse.linalg.spsolve(k*K.tocsc()/StiffnessFactor, F).toarray()
            # t2 = max(np.linalg.norm(U2,axis=1))
            NewRelevantCoords = np.add(RelevantCoords, U2)

        NewCoords[NodeIds] = NewRelevantCoords
        NewCoords[list(FixedNodes)] = np.array(self.NodeCoords)[list(FixedNodes)]
        # Collapse transition elements

        if OptimizeTets:
            Tets = [elem for elem in self.NodeConn if len(elem)==4]
            skew = quality.Skewness(NewCoords,Tets)
            BadElems = set(np.where(skew>0.9)[0])
            ElemNeighbors = utils.getElemNeighbors(NewCoords,Tets)
            BadElems.update([e for i in BadElems for e in ElemNeighbors[i]])
            BadNodes = set([n for i in BadElems for n in Tets[i]])

            SurfConn = converter.solid2surface(NewCoords,Tets)
            SurfNodes = set([n for elem in SurfConn for n in elem])

            FreeNodes = BadNodes.difference(SurfNodes)

            NewCoords = improvement.TetOpt(NewCoords,Tets,FreeNodes=FreeNodes,objective='eta',method='BFGS',iterate=4)
        
        # Divide the boundary layer to create the specified number of layers
        if nLayers > 1: 
            nNum = len(NewCoords)
            NewCoords2 = np.array(NewCoords)        
            for i in range(NOrigElem,self.NElem):
                elem = self.NodeConn[i]
                NewNodes = []
                NewElems = [[elem[0],elem[1],elem[2],elem[0],elem[1],elem[2]]] + [[] for j in range(nLayers-1)]
                for j in range(1,nLayers):
                    NewNodes += [NewCoords2[elem[0]] + (NewCoords2[elem[3]]-NewCoords2[elem[0]])*j/nLayers, 
                                     NewCoords2[elem[1]] + (NewCoords2[elem[4]]-NewCoords2[elem[1]])*j/nLayers, 
                                     NewCoords2[elem[2]] + (NewCoords2[elem[5]]-NewCoords2[elem[2]])*j/nLayers]
                    NewElems[j-1] = [NewElems[j-1][3],NewElems[j-1][4],NewElems[j-1][5],nNum,nNum+1,nNum+2]
                    NewElems[j] = [nNum,nNum+1,nNum+2,nNum,nNum+1,nNum+2]
                    nNum += 3
                NewElems[-1] = [NewElems[-2][3],NewElems[-2][4],NewElems[-2][5],elem[3],elem[4],elem[5]]
                NewCoords2 = np.append(NewCoords2,np.array(NewNodes),axis=0)
                OrigConn += NewElems
        
            self.NodeCoords = NewCoords2.tolist()
            self.NodeConn = OrigConn
        else:
            self.NodeCoords = NewCoords
        

        # Reduce or remove degenerate wedges -- TODO: This can probably be made more efficient
        # self.cleanup()
        self.NodeCoords,self.NodeConn = utils.DeleteDuplicateNodes(self.NodeCoords,self.NodeConn)
        Unq = [np.unique(elem,return_index=True,return_inverse=True) for elem in self.NodeConn]
        key = utils.PadRagged([u[1][u[2]] for u in Unq],fillval=-1)

        Cases = -1*np.ones(self.NElem,dtype=int)
        # Fully degenerate wedges (triangles):
        Cases[np.all(key[:,0:6]==[0,1,2,0,1,2],axis=1)] = 0
        Cases[np.all(key[:,0:6]==[3,4,5,3,4,5],axis=1)] = 0
        # Double-edge degenerate wedges (tetrahedrons):
        Cases[np.all(key[:,0:6]==[0,1,2,3,1,2],axis=1)] = 1
        Cases[np.all(key[:,0:6]==[0,1,2,0,4,2],axis=1)] = 2
        Cases[np.all(key[:,0:6]==[0,1,2,0,1,5],axis=1)] = 3
        Cases[np.all(key[:,0:6]==[0,4,5,3,4,5],axis=1)] = 4
        Cases[np.all(key[:,0:6]==[3,1,5,3,4,5],axis=1)] = 5
        Cases[np.all(key[:,0:6]==[3,4,2,3,4,5],axis=1)] = 6
        # Single-edge degenerate wedges (pyramids):
        Cases[np.all(key[:,0:6]==[0,1,2,3,1,5],axis=1)] = 7
        Cases[np.all(key[:,0:6]==[0,1,2,3,4,2],axis=1)] = 8
        Cases[np.all(key[:,0:6]==[0,1,2,0,4,5],axis=1)] = 9
        Cases[np.all(key[:,0:6]==[0,1,5,3,4,5],axis=1)] = 10
        Cases[np.all(key[:,0:6]==[3,1,2,3,4,5],axis=1)] = 11
        Cases[np.all(key[:,0:6]==[0,4,2,3,4,5],axis=1)] = 12
        # Non-wedges
        nNodes = np.array([len(elem) for elem in self.NodeConn])
        Cases[nNodes!=6] = -1

        ProperKeys = [
            [],             # 0
            [0,1,2,3],      # 1
            [0,1,2,4],      # 2
            [0,1,2,5],      # 3
            [0,4,5,3],      # 4
            [3,1,5,4],      # 5
            [3,4,2,5],      # 6
            [0,2,5,3,1],    # 7
            [0,3,4,1,2],    # 8
            [1,4,5,2,0],    # 9
            [0,3,4,1,5],    # 10
            [1,4,5,2,3],    # 11
            [0,2,5,3,4]     # 12
        ]
        RNodeConn = utils.PadRagged(self.NodeConn)
        for i,case in enumerate(Cases):
            if case == -1:
                continue
            else:
                self.NodeConn[i] = RNodeConn[i][ProperKeys[case]].tolist()
        self.NodeConn = [elem for elem in self.NodeConn if len(elem)>0]
        # Attempt to fix any element inversions
        # NewCoords = np.asarray(NewCoords)
        # NewRelevantCoords = NewCoords[NodeIds]
        V = quality.Volume(*self)
        if min(V) < 0:
            # print(sum(V<0))
            # BLConn = [elem for elem in self.NodeConn if len(elem) == 6]
            # self.NodeCoords = improvement.FixInversions(self.NodeCoords,BLConn,FixedNodes=np.unique(converter.solid2surface(self.NodeCoords,self.NodeConn)))
            BadElems = set(np.where(V<0)[0])
            ElemNeighbors = utils.getElemNeighbors(*self)
            BadElems.update([e for i in BadElems for e in ElemNeighbors[i]])
            BadNodes = set([n for i in BadElems for n in self.NodeConn[i]])
            # self.reset('SurfConn')
            SurfNodes = set([n for elem in self.SurfConn for n in elem])

            FreeNodes = BadNodes.difference(SurfNodes)
            FixedNodes = set(range(self.NNode)).difference(FreeNodes)
            # NewRelevantCoords = improvement.TetOpt(NewRelevantCoords,RelevantConn,FreeNodes=FreeNodes,objective='eta',method='BFGS',iterate=4)
            self.NodeCoords = improvement.FixInversions(*self,FixedNodes=FixedNodes)
            # NewCoords[NodeIds] = NewRelevantCoords
        self.reset()
    
    def Contour(self, scalars, threshold, threshold_direction=1, mixed_elements=True, Type=None, interpolation='linear'):
        """
        Contour the mesh to extract an isosurface/isoline based on nodal scalar values.

        Parameters
        ----------
        scalars : str or array_like
            Values to be used for thresholding, either a string indicating an entry in NodeData or ElemData, or an array_like of values.
        threshold : int, float
            Isosurface level that defines the boundary
        threshold_direction : signed int
            If threshold_direction is negative (default), values less than or equal to the threshold will be considered "inside" the mesh and the opposite if threshold_direction is positive, by default 1.
        mixed_elements : bool, optional
            If True, the generated mesh will have mixed element types 
            (triangles/quadrilaterals, tetrahedra/wedges), otherwise a single element 
            type (triangles, tetrahedra), by default False. 
        Type : str, optional
            Specfies the mesh type ('vol', 'surf', or 'line') to produce by 
            contouring. If None is provided, the output Type will be the same 
            as the input Type, by default None. A volumetric mesh can be contoured
            to create a volumetric mesh or a surface mesh, and a surface mesh can
            be contoured to create a surface mesh or a line mesh. Contouring of
            line meshes isn't currently supported.

        Returns
        -------
        M : mymesh.mesh
            Contoured mesh
        """
        if isinstance(scalars, str):
            scalar_str = scalars
            scalars = self.NodeData[scalars]
        else:
            scalar_str = 'scalars'

        if threshold_direction < 0:
            flip = False
        else:
            flip = True
        
        NewCoords, NewConn = contour.MarchingElements(self.NodeCoords, self.NodeConn,
                                                      scalars, threshold=threshold, 
                                                      flip=flip, mixed_elements=mixed_elements, 
                                                      Type=Type, interpolation=interpolation)
        M = mesh(NewCoords, NewConn, verbose=self.verbose)
        return M

    def Threshold(self, scalars, threshold, mode=None, scalar_preference='elements', all_nodes=True, InPlace=False, cleanup=False):
        """
        Threshold the mesh by scalar values at either nodes or elements. 

        Parameters
        ----------
        scalars : str or array_like
            Values to be used for thresholding, either a string indicating an entry in NodeData or ElemData, or an array_like of values.
        threshold : int, float, or tuple
            Thresholding value(s) to use. If provided as a two element tuple, they're taken to be lower and upper bounds.
        mode : str, optional
            Thresholding condition to determine which elements to keep in the mesh.

            Single threshold options:
                '>=' - Keeping condition is `value >= threshold`, default.

                '>' - Keeping condition is `value > threshold`.

                '<' - Keeping condition is `value < threshold`.

                '<=' - Keeping condition is `value <= threshold`.

                '==' - Keeping condition is `value == threshold`.

                '!=' - Keeping condition is `value != threshold`.

            Double threshold options:
                'in' - Inside bounds, inclusive of thresholds, default. 

                'xin' - Inside bounds, exclusive of thresholds. 

                'out' - Outside bounds, inclusive of thresholds.

                'xout' - Outside bounds, exclusive of threhsolds.

                '<=<=' - Keeping condition is `lower <= value <= upper`, equivalent to 'in'.

                '<<' - Keeping condition is `lower < value < upper`, equivalent to 'xin'.

                '>=>=' - Keeping condition is `(lower >= value) | (value >= upper)`, equivalent to 'out'.

                '>>' - Keeping condition is `(lower > value) | (value > upper)`, equivalent to 'xout'

        scalar_preference : str, optional
            If scalars is provided as a string and that string exists as an entry in both NodeData and ElemData,
            this determines which will be used. Must be either 'nodes' or 'elements', by default 'elements'.
        all_nodes : bool, optional
            If node data is being used, this determines whether to keep an element if all nodes pass the
            thresholding condition or if any nodes pass the condition, by default True
        InPlace : bool, optional
            If true, this mesh will be modified, otherwise a copy of the mesh will be created and modified, by default False.
        cleanup : bool, optional
            Option to run :meth:`mesh.cleanup`, removing nodes that are no 
            longer in the cropped mesh, by default False.
        """        

        # Process inputs
        if isinstance(scalars, str):
            scalar_str = scalars
            if scalar_preference.lower() == 'elements':
                if scalar_str in self.ElemData.keys():
                    scalars = self.ElemData[scalar_str]
                    scalar_type = 'elements'
                elif scalar_str in self.NodeData.keys():
                    scalars = self.NodeData[scalar_str]
                    scalar_type = 'nodes'
                else:
                    raise ValueError(f'{scalar_str:s} not in ElemData or NodeData.')
            elif scalar_preference.lower() == 'nodes':
                if scalar_str in self.NodeData.keys():
                    scalars = self.NodeData[scalar_str]
                    scalar_type = 'nodes'
                elif scalar_str in self.ElemData.keys():
                    scalars = self.ElemData[scalar_str]
                    scalar_type = 'elements'
                else:
                    raise ValueError(f'{scalar_str:s} not in ElemData or NodeData.')
            else:
                raise ValueError(f'scalar_preference must be specified as "elements" or "nodes", not "{scalar_preference:s}".')
        else:
            scalar_str = 'scalars'
            if len(scalars) == self.NElem:
                scalar_type = 'elements'
            elif len(scalars) == self.NNode:
                scalar_type = 'nodes'
            else:
                raise ValueError(f'Provided scalars must much either the number of nodes or number of elements in the mesh.')

        
        if isinstance(threshold, (list, tuple, np.ndarray)):
            if mode is None:
                # Default for upper/lower bound 
                mode = 'in'
            if mode == '<=<=':
                mode = 'in'
            elif mode == '<<':
                mode = 'xin'
            elif mode == '>=>=':
                mode = 'out'
            elif mode == '>>':
                mode = 'xout'
            lower = min(threshold)
            upper = max(threshold)
        else:
            if mode is None:
                mode = '>='
            if mode == '>=':
                lower = threshold
                upper = np.inf
                mode = 'in'
            elif mode == '>':
                lower = threshold
                upper = np.inf
                mode = 'xin'
            elif mode == '<=':
                lower = -np.inf
                upper = threshold
                mode = 'in'
            elif mode == '<':
                lower = -np.inf
                upper = threshold
                mode = 'xin'
            elif mode == '==':
                lower = threshold
                upper = threshold
                mode = 'in'
            elif mode == '!=':
                lower = threshold
                upper = threshold
                mode = 'xout'
            else:
                raise ValueError('For single-threshold inputs, mode must be ">=", ">", "<=", or "<".')
        
        # Determine which elements to keep
        if mode == 'in':
            keep = (lower <= scalars) & (scalars <= upper)
        elif mode == 'xin':
            keep = (lower < scalars) & (scalars < upper)
        elif mode == 'out':
            keep = (lower >= scalars) | (scalars >= upper)
        elif mode == 'xout':
            keep = (lower > scalars) | (scalars > upper)
        else:
            raise ValueError('Invalid thresholding mode.')

        if scalar_type == 'nodes':
            if type(self.NodeConn) is np.ndarray:
                if all_nodes:
                    keep = np.all(keep[self.NodeConn],axis=1)
                else:
                    keep = np.any(keep[self.NodeConn],axis=1)
            else:
                if all_nodes:
                    keep = np.array([np.all(keep[elem]) for elem in self.NodeConn])
                else:
                    keep = np.array([np.any(keep[elem]) for elem in self.NodeConn])

        RemoveElems = np.where(~keep)[0]

        if InPlace:
            M = self
        else:
            M = self.copy()

        M.removeElems(RemoveElems)
        if cleanup:
            M.cleanup()
        return M

    def Clip(self, pt=None, normal=[1,0,0], exact=False):
        """
        Clip the mesh along a plane. Clipping with this method will not cut
        through elements, but rather will only keep elements on one side of
        the specified plane.

        Parameters
        ----------
        pt : array_like or NoneType, optional
            Coordinates for a point on the clipping plane, by default None.
            If None, the center of the bounding box of the mesh will be used.
        normal : list, optional
            Normal vector of the clipping plane, by default [1,0,0]

        Returns
        -------
        clipped : mymesh.mesh
            Clipped mesh
        """        
        if pt is None:
            xmax, ymax, zmax = np.max(self.NodeCoords, axis=0)
            xmin, ymin, zmin = np.min(self.NodeCoords, axis=0)
            pt = np.array([(xmax+xmin)/2, (ymax+ymin)/2, (zmax+zmin)/2])
        
        if exact:
            vals = implicit.plane(pt, normal)(*self.NodeCoords.T)
            clipped = self.Contour(vals, 0)
        else:
            vals = implicit.plane(pt, normal)(*self.Centroids.T)
            clipped = self.Threshold(vals, 0)

        return clipped
    
    def Crop(self, bounds, method='centroids', InPlace=False, cleanup=False):
        """
        Crop the mesh to specified bounds. Cropping with this method doesn't
        modify any elements, it keeps the elements of the original mesh that
        are within the cropping bounds. 

        Parameters
        ----------
        bounds : array_like
            Six element list of of cropping bounds, formatted as 
            [xmin, xmax, ymin, ymax, zmin, zmax].
        method : str, optional
            Cropping method, by default 'centroids'

                - 'centroids' - keep elements whose centroids are within the bounds
                - 'nodes' - keep elements who have all of their nodes within the bound
        InPlace : bool, optional
            If True, the original mesh will be modified in place, otherwise a 
            copy will be made and modified, leaving the original mesh unaltered.
            By default False
        cleanup : bool, optional
            Option to run :meth:`mesh.cleanup`, removing nodes that are no 
            longer in the cropped mesh, by default False.

        Returns
        -------
        M : mymesh.mesh
            Cropped mesh. If InPlace=True, the output will be a reference to the
            same mesh instance as the input.

        """
        if InPlace:
            M = self
        else:
            M = self.copy()

        if method.lower() == 'centroids':
            points = np.asarray(M.Centroids)
            keep = ((bounds[0] < points[:,0]) & 
                    (points[:,0] < bounds[1]) & 
                    (bounds[2] < points[:,1]) & 
                    (points[:,1] < bounds[3]) & 
                    (bounds[4] < points[:,2]) & 
                    (points[:,2] < bounds[5]))
        elif method.lower() == 'nodes':
            points = np.asarray(M.NodeCoords)
            keep_nodes = ((bounds[0] < points[:,0]) & 
                    (points[:,0] < bounds[1]) & 
                    (bounds[2] < points[:,1]) & 
                    (points[:,1] < bounds[3]) & 
                    (bounds[4] < points[:,2]) & 
                    (points[:,2] < bounds[5]))
            keep = np.array([np.all(keep_nodes[elem]) for elem in M.NodeConn])
        else:
            raise ValueError(f'Invalid method: "{method:s}". Must be "centroids or nodes".')
        
        RemoveElems = np.where(~keep)[0]
        M.removeElems(RemoveElems)
        if cleanup:
            M.cleanup()

        return M
    
    def Mirror(self, x=None, y=None, z=None, InPlace=False):
        """
        Mirror the mesh across Cartesian planes. At least one of x, y, or z
        must be specified to mirror the mesh. If multiple planes are specified,
        the mesh will first be mirrored across the x plane, then the y, then the 
        z - for example, given x=0, y=0, z=None, a point at (-1,-1,0) would be
        mirrored to (1,-1,0) and then to (1,1,0). Note that reflections across
        planes parallel to the Cartesian planes are commutative, so the order
        of reflections don't matter.

        Parameters
        ----------
        x : float, optional
            YZ plane at X = x. The default is None.
        y : float, optional
            XZ plane at Y = y. The default is None.
        z : float, optional
            XY plane at Z = z. The default is None.
        InPlace : bool, optional
            If True, the original mesh will be modified in place, otherwise a 
            copy will be made and modified, leaving the original mesh unaltered.
            By default False

        Returns
        -------
        M : mymesh.mesh
            Cropped mesh. If InPlace=True, the output will be a reference to the
            same mesh instance as the input.
        """        
        if InPlace:
            M = self
        else:
            M = self.copy()

        M.NodeCoords, M.NodeConn = utils.MirrorMesh(M.NodeCoords, M.NodeConn, x=x, y=y, z=z)

        return M
        
    ## Mesh Measurements Methods
    def getQuality(self,metrics=['Skewness','Aspect Ratio'], verbose=None):
        """
        Evaluate mesh quality. This will create a dict with entries corresponding
        to the specified quality metrics. This dict can be stored in 
        mesh.ElemData by performing `m.ElemData.update(m.getQuality())` 
        or `m.ElemData |= m.getQuality()`

        Parameters
        ----------
        metrics : str or list, optional
            Quality metric, or list of quality metrics, to evaluate, by default 
            ['Skewness','Aspect Ratio']. 
            Available options are:
            
                - 'Skewness' : :func:`~mymesh.quality.Skewness`
                - 'Aspect Ratio' : :func:`~mymesh.quality.AspectRatio`
                - 'Inverse Orthogonal Quality' : :func:`~mymesh.quality.InverseOrthogonalQuality`
                - 'Orthogonal Quality' : :func:`~mymesh.quality.OrthogonalQuality`
                - 'Inverse Orthogonality' : :func:`~mymesh.quality.InverseOrthogonality`
                - 'Orthogonality' : :func:`~mymesh.quality.Orthogonality`
                - 'Min Dihedral' : :func:`~mymesh.quality.MinDihedral` - Reported in radians
                - 'Min Dihedral(deg)' : :func:`~mymesh.quality.MinDihedral` - Reported in degrees
                - 'Max Dihedral' : :func:`~mymesh.quality.MaxDihedral` - Reported in radians
                - 'Max Dihedral(deg)' : :func:`~mymesh.quality.MaxDihedral` - Reported in degrees
                - 'Mean Ratio' : :func:`~mymesh.quality.MeanRatio`
                - 'Volume' : :func:`~mymesh.quality.Volume`

            Note that not all metrics are suited to all element types.

        verbose : bool or NoneType, optional
            If True, quality reports will be printed. If None, this will be 
            determined by the verbosity state (mesh.verbose) of the mesh object, 
            by default None.

        Returns
        -------
        qual : dict
            Dictionary of element qualities

        """        
        
        if verbose is None:
            verbose = self.verbose
        qual = {}
        if type(metrics) is str: metrics = [metrics]
        for metric in metrics:
            assert isinstance(metric, str), 'Invalid quality metric. Metrics must be strings.'
            m = metric.lower()
            if m == 'skewness':
                qual[metric] = quality.Skewness(*self,verbose=verbose)
            elif m == 'aspect ratio':
                qual[metric] = quality.AspectRatio(*self,verbose=verbose)    
            elif m == 'inverse orthogonal quality':
                qual[metric] = quality.InverseOrthogonalQuality(*self,verbose=verbose)
            elif m == 'orthogonal quality':
                qual[metric] = quality.OrthogonalQuality(*self,verbose=verbose)
            elif m == 'inverse orthogonality':
                qual[metric] = quality.InverseOrthogonality(*self,verbose=verbose)
            elif m == 'orthogonality':
                qual[metric] = quality.Orthogonality(*self,verbose=verbose)
            elif m == 'min dihedral':
                qual[metric] = quality.MinDihedral(*self,verbose=verbose)
            elif m == 'min dihedral(deg)':
                qual[metric] = quality.MinDihedral(*self,verbose=verbose)*180/np.pi
            elif m == 'max dihedral':
                qual[metric] = quality.MaxDihedral(*self,verbose=verbose)
            elif m == 'max dihedral(deg)':
                qual[metric] = quality.MaxDihedral(*self,verbose=verbose)*180/np.pi
            elif m == 'mean ratio':
                qual[metric] = quality.MeanRatio(*self,verbose=verbose)
            elif m == 'volume':
                qual[metric] = quality.Volume(*self,verbose=verbose)
            else:
                raise Exception(f'Invalid quality metric "{metric:s}".')
        return qual
    def getCurvature(self,metrics=['Max Principal','Min Principal', 'Curvedness', 'Shape Index', 'Mean', 'Gaussian'], nRings=1, SplitFeatures=False):
        
        if type(metrics) is str: metrics = [metrics]
        Curvature = {}
        if SplitFeatures:
            edges,corners = utils.DetectFeatures(self.NodeCoords,self.SurfConn)
            FeatureNodes = set(edges).union(corners)
            NodeRegions = utils.getConnectedNodes(self.NodeCoords,self.SurfConn,BarrierNodes=FeatureNodes)
            MaxPs = np.nan*np.ones((self.NNode,len(NodeRegions))) 
            MinPs = np.nan*np.ones((self.NNode,len(NodeRegions))) 
            for i,region in enumerate(NodeRegions):
                Elems = [elem for elem in self.SurfConn if all([n in region for n in elem])]
                # ElemNormals = [self.ElemNormals[i] for i,elem in enumerate(self.SurfConn) if all([n in region for n in elem])]
                ElemNormals = utils.CalcFaceNormal(self.NodeCoords,Elems)
                Neighbors,ElemConn = utils.getNodeNeighbors(self.NodeCoords,Elems)
                if nRings > 1:
                    Neighbors = utils.getNodeNeighborhood(self.NodeCoords,Elems,nRings)
                NodeNormals = utils.Face2NodeNormal(self.NodeCoords,Elems,ElemConn,ElemNormals)
                MaxPs[:,i], MinPs[:,i] = curvature.CubicFit(self.NodeCoords,Elems,Neighbors,NodeNormals)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=RuntimeWarning)
                MaxPrincipal = np.nanmean(MaxPs,axis=1)
                MinPrincipal = np.nanmean(MinPs,axis=1)

        else:
            if nRings == 1:
                Neighbors = self.SurfNodeNeighbors
            else:
                Neighbors = utils.getNodeNeighborhood(self.NodeCoords,self.SurfConn,nRings=nRings)
            MaxPrincipal,MinPrincipal = curvature.CubicFit(self.NodeCoords,self.SurfConn,Neighbors,self.NodeNormals)
        if 'Max Principal' in metrics:
            Curvature['Max Principal Curvature'] = MaxPrincipal
        if 'Max Principal' in metrics:
            Curvature['Min Principal Curvature'] = MinPrincipal
        if 'Shape Index' in metrics or 'Shape Category' in metrics:
            SI = curvature.ShapeIndex(MaxPrincipal,MinPrincipal)
            if 'Shape Index' in metrics:
                Curvature['Shape Index'] = SI
        if 'Shape Category' in metrics:
            SC = curvature.ShapeCategory(SI)
            Curvature['Shape Category'] = SC
        if 'Curvedness' in metrics:
            C = curvature.Curvedness(MaxPrincipal,MinPrincipal)
            Curvature['Curvedness'] = C
        if 'Gaussian' in metrics:
            G = curvature.GaussianCurvature(MaxPrincipal,MinPrincipal)
            Curvature['Gaussian Curvature'] = G
        if 'Mean' in metrics:
            M = curvature.MeanCurvature(MaxPrincipal,MinPrincipal)
            Curvature['Mean Curvature'] = M
        
        return Curvature

    ## File I/O Methods
    def mymesh2meshio(self):
        """
        Convert mesh object to a `meshio <https://github.com/nschloe/meshio>`_  
        mesh object.

        Returns
        -------
        m : meshio._mesh.mesh
            meshio-type mesh object with nodes, elements (cells), and 
            node/element data.

        """        
        try:
            import meshio
        except:
            raise ImportError('mesh.Mesh2Meshio() requires the meshio library. Install with: pip install meshio')

        celldict = dict()
        elemlengths = np.array([len(elem) for elem in self.NodeConn])
        if len(self.ElemData) > 0:
            keys = self.ElemData.keys()
            for key in keys:
                celldata = [[],[],[],[],[],[],[],[],[],[]]
                data = np.asarray(self.ElemData[key])
                if data.dtype == bool:
                    data = data.astype(int)
                elif np.issubdtype(data.dtype, np.str_):
                    data = np.array([int.from_bytes(x.encode('utf-8'), 'little') for x in data])
                celldata[0] = data[elemlengths==2]  # line
                celldata[1] = data[elemlengths==3]  # tri
                celldata[2] = data[elemlengths==4]  # quad/tet
                celldata[3] = data[elemlengths==5]  # pyr
                celldata[4] = data[elemlengths==6]  # tri6/wdg
                celldata[5] = data[elemlengths==8]  # quad8/hex
                celldata[6] = data[elemlengths==10] # tet10
                celldata[7] = data[elemlengths==13] # pyr13
                celldata[8] = data[elemlengths==15] # wdg15
                celldata[9] = data[elemlengths==20] # hex20
                celldata = [c for c in celldata if len(c) > 0]
                celldict[key] = celldata
        NodeData = copy.copy(self.NodeData)
        if len(NodeData) > 0:
            for key in NodeData.keys():
                data = np.asarray(NodeData[key])
                if data.dtype == bool:
                    data = data.astype(int)
                elif np.issubdtype(data.dtype, np.str_):
                    data = np.array([int.from_bytes(x.encode('utf-8'), 'little') for x in data])
                NodeData[key] = data
        if np.all(elemlengths == elemlengths[0]):
            ArrayConn = np.array(self.NodeConn,dtype=int)
        else:
            ArrayConn = np.array(self.NodeConn,dtype=object)

        edges, tris, tri6s, quads, quad8s, tets, tet10s, pyrs, pyr13s, wdgs, wdg15s, hexs, hex20s = [np.empty((0,0)) for i in range(13)]

        if np.any(elemlengths == 2): edges = np.stack(ArrayConn[elemlengths==2])
        if np.any(elemlengths == 3): tris = np.stack(ArrayConn[elemlengths==3])
        if self.Type == 'surf':
            if np.any(elemlengths == 4): quads = np.stack(ArrayConn[elemlengths==4])
            if np.any(elemlengths == 6): tri6s = np.stack(ArrayConn[elemlengths==6])
            if np.any(elemlengths == 8): quad8s = np.stack(ArrayConn[elemlengths==8])
            tets = []
            wdgs = []
            hexs = []
        else:
            quads = []
            tri6s = []
            quad8s = []
            if np.any(elemlengths == 4): tets = np.stack(ArrayConn[elemlengths==4])
            if np.any(elemlengths == 6): wdgs = np.stack(ArrayConn[elemlengths==6])
            if np.any(elemlengths == 8): hexs = np.stack(ArrayConn[elemlengths==8])
        if np.any(elemlengths == 5): pyrs = np.stack(ArrayConn[elemlengths==5])
        if np.any(elemlengths == 10): tet10s = np.stack(ArrayConn[elemlengths==10])
        if np.any(elemlengths == 13): pyr13s = np.stack(ArrayConn[elemlengths==13])
        if np.any(elemlengths == 15): wdg15s = np.stack(ArrayConn[elemlengths==15])
        if np.any(elemlengths == 20): hex20s = np.stack(ArrayConn[elemlengths==20])
        
        if np.any(elemlengths == 13) or np.any(elemlengths == 15):
            raise Exception("meshio currently doesn't support quadratic (13-node) pyramids or quadratic (15-node) wedges.")

        elems = [e for e in [('line',edges),('triangle',tris),('triangle6',tri6s),('quad',quads),('quad8',quad8s),('tetra',tets),('tetra10',tet10s),('pyramid',pyrs),('pyramid13',pyr13s),('wedge',wdgs),('wedge15',wdg15s),('hexahedron',hexs),('hexahedron20',hex20s)] if len(e[1]) > 0]
        
        m = meshio.Mesh(self.NodeCoords, elems, point_data=NodeData, cell_data=celldict)

        m.point_sets = self.NodeSets
        m.cell_sets = self.ElemSets     # TODO: This might not give the expected result

        return m
    def write(self,filename,binary=True):
        """
        Write mesh to file. Utilizes `meshio <https://github.com/nschloe/meshio>`_ 
        to access a variety of filetypes.

        Parameters
        ----------
        filename : str
            Name of file with appropriate extension
        binary : bool, optional
            If True, will write the a binary file (if applicable) rather than an
            ASCII version of the file, by default True.
        """        
        if self.NNode == 0:
            warnings.warn('Mesh empty - file not written.')
            return
        if self.NElem == 0:
            self.NodeConn = [[0,0,0]]
        ext = os.path.splitext(filename)[1].lower()
        if ext == '.stl' or ext == '.ply':
            # Surface only support
            if self.Type.lower() == 'vol':
                M = self.Surface.copy()
            else:
                M = self.copy()
            if ext == '.stl':
                # Triangle only support
                M.NodeCoords, M.NodeConn = converter.surf2tris(M.NodeCoords, M.NodeConn)
        else:
            M = self
        m = M.mymesh2meshio()
        # File types that support the binary option: 
        binary_support = ['.msh', '.f3grid', '.ply', '.stl', '.vtk', '.vtu'] 
        if binary is not None and ext in binary_support:
            m.write(filename,binary=binary)
        else:
            m.write(filename)
    def meshio2mymesh(m):
        """
        Convert a `meshio <https://github.com/nschloe/meshio>`_ mesh object to a 
        MyMesh mesh object

        Parameters
        ----------
        m : meshio._mesh.Mesh
            Meshio mesh object

        Returns
        -------
        M : mymesh.mesh
            MyMesh mesh object

        """        
        try:
            import meshio
        except:
            raise ImportError('mesh.Meshio2Mesh() requires the meshio library. Install with: pip install meshio')
        if int(meshio.__version__.split('.')[0]) >= 5 and int(meshio.__version__.split('.')[1]) >= 2:
            if len(m.cells) == 1:
                # Single element type - keeps NodeConn as an array
                NodeConn = m.cells[0].data
            else:
                # Multiple element types - convert to list
                NodeConn = [elem for cells in m.cells for elem in cells.data.tolist()]
        else:
            # Support for older meshio version
            NodeConn = [elem for cells in m.cells for elem in cells[1].tolist()]
        NodeCoords = m.points
        M = mesh(NodeCoords,NodeConn)
        if len(m.point_data) > 0 :
            for key in m.point_data.keys():
                M.NodeData[key] = np.asarray(m.point_data[key])
        if len(m.cell_data) > 0:
            for key in m.cell_data.keys():
                M.ElemData[key] = np.asarray([data for celldata in m.cell_data[key] for data in celldata])
        M.NodeSets = m.point_sets
        M.ElemSets = m.cell_sets    # TODO: This might not give the expected result

        return M
    def read(file):
        """
        Read a mesh file written in any file type supported by meshio

        Parameters
        ----------
        file : str
            File path to a mesh file readable by meshio (.vtu, .vtk, .inp, .stl, ...)

        Returns
        -------
        M : mesh.mesh
            Mesh object
        """        
        try:
            import meshio
        except:
            raise ImportError('mesh.read() requires the meshio library. Install with: pip install meshio')
        m = meshio.read(file)
        M = mesh.meshio2mymesh(m)

        return M          
    def imread(img, voxelsize, scalefactor=1, scaleorder=1, return_nodedata=False, return_gradient=False, gaussian_sigma=1, threshold=None, crop=None, threshold_direction=1):
        """
        Load an image into a voxel mesh. :func:``~mymesh.converter.im2voxel`` is
        used to perform the conversion.

        Parameters
        ----------
        img : str or np.ndarray
            If a str, should be the directory to an image stack of tiff or dicom files.
            If an array, shoud be a 3D array of image data.
        voxelsize : float
            Size of voxel (based on image resolution).
        scalefactor : float, optional
            Scale factor for resampling the image. If greater than 1, there will be more than
            1 elements per voxel. If less than 1, will coarsen the image, by default 1.
        scaleorder : int, optional
            Interpolation order for scaling the image (see scipy.ndimage.zoom), by default 1.
            Must be 0-5.
        threshold : float, optional
            Voxel intensity threshold, by default None.
            If given, elements with all nodes less than threshold will be discarded.

        Returns
        -------
        M : mesh.mesh
            Mesh object, containing image data for elements and nodes in M.ElemData['Image Data'] and M.NodeData['Image Data'].
        """
        if return_nodedata:
            VoxelCoords, VoxelConn, VoxelData, NodeData = converter.im2voxel(img,voxelsize,scalefactor=scalefactor,scaleorder=scaleorder,return_nodedata=return_nodedata,return_gradient=return_gradient, gaussian_sigma=gaussian_sigma,threshold=threshold,crop=crop,threshold_direction=threshold_direction)
        else:
            VoxelCoords, VoxelConn, VoxelData = converter.im2voxel(img,voxelsize,scalefactor=scalefactor,scaleorder=scaleorder,return_nodedata=return_nodedata,return_gradient=return_gradient,gaussian_sigma=gaussian_sigma,threshold=threshold,crop=crop,threshold_direction=threshold_direction)
        M = mesh(VoxelCoords,VoxelConn)
        if return_gradient:
            M.ElemData['Image Data'],M.ElemData['Image Gradient'] = VoxelData
            if return_nodedata: M.NodeData['Image Data'], M.NodeData['Image Gradient']  = NodeData
        else:
            M.ElemData['Image Data'] = VoxelData
            if return_nodedata: M.NodeData['Image Data'] = NodeData
        return M

    def to_meshio(self):
        """
        Convert mesh object to a `meshio <https://github.com/nschloe/meshio>`_  
        mesh object. This is an alias to  mymesh2meshio.

        Returns
        -------
        m : meshio._mesh.mesh
            meshio-type mesh object with nodes, elements (cells), and 
            node/element data.
        """        
        return self.mymesh2meshio()
    
    def to_pyvista(self):
        """
        Convert mesh object to a `pyvista <https://pyvista.org/>`_  
        unstructured grid object. 

        Returns
        -------
        pvmesh : pyvista.core.pointset.UnstructuredGrid
            meshio-type mesh object with nodes, elements (cells), and 
            node/element data.
        """
        try: 
            import pyvista as pv
        except:
            raise ImportError('pyvista m ust be installed to create an pyvista mesh object. Install with: `pip install pyvista`')
        
        pvmesh = pv.wrap(self.to_meshio())
        return pvmesh

    ## Visualization Methods
    def view(self, **kwargs):
        """
        Generate an interactive plot of the mesh. See :func:`mymesh.visualize.view` 
        for a full list of optional arguments.

        Returns
        -------
        out 
            Output passed from :func:`mymesh.visualize.view`.
        """        
        out = visualize.View(self, **kwargs)   
        return out 
    def plot(self, show=True, return_fig=False, clim=None, show_colorbar=True, **kwargs):
        """
        Generate a static plot of the mesh. See :func:`mymesh.visualize.view` 
        for a full list of optional arguments.

        Parameters
        ----------
        show : bool, optional
            Display the plotted mesh, by default True. If False,
            the plot will be generated and can be returned, but won't 
            be displayed.
        return_fig : bool, optional
            If True, a matplotlib figure and axis holding the plotted mesh
            will be returned, by default False
        clim : array_like, optional
            Two-element tuple, list, or array containing the lower and upper
            bound for the colorscale if a scalar is displayed, by default None.
            If None, the minimum and maximum values will be used.

        Returns
        -------
        fig : matplotlib.figure.Figure
            matplotlib figure of the plotted mesh
        ax : matplotlib.axes._axes.Axes
            matplotlib axes of the plotted mesh

        """        
        try:
            import matplotlib
            import matplotlib.pyplot as plt
        except:
            raise ImportError('Matplotlib required for plotting. Install with `pip install matplotlib`.')
        kwargs['return_image'] = True
        kwargs['interactive'] = False
        kwargs['hide'] = True
        img = visualize.View(self, **kwargs)

        fig, ax = plt.subplots()
        ax.imshow(img)
        ax.set_axis_off()
        if 'scalars' in kwargs and kwargs['scalars'] is not None:
            scalars = kwargs['scalars']
            if 'scalar_preference' in kwargs:
                scalar_preference = kwargs['scalar_preference']
            else:
                scalar_preference = 'nodes'

            if type(scalars) is str:
                if scalar_preference.lower() == 'nodes':
                    if scalars in self.NodeData.keys():
                        scalars = self.NodeData[scalars]
                    elif scalars in self.ElemData.keys():
                        scalars = self.ElemData[scalars]
                    else:
                        raise ValueError(f'Scalar {scalars:s} not present in mesh.')
                elif scalar_preference.lower() == 'elements':
                    if scalars in self.ElemData.keys():
                        scalars = self.ElemData[scalars]
                    elif scalars in self.NodeData.keys():
                        scalars = self.NodeData[scalars]
                    else:
                        raise ValueError(f'Scalar {scalars:s} not present in mesh.')
                else:
                    raise ValueError('scalar_preference must be "nodes" or "elements"')
            if clim is None:
                cmin, cmax = np.min(scalars), np.max(scalars)
            else:
                cmin, cmax = clim

            scale = matplotlib.cm.ScalarMappable(cmap='coolwarm')
            scale.set_clim(cmin, cmax)
            if show_colorbar:
                colorbar = matplotlib.pyplot.colorbar(scale, ax=ax)
        if show:
            plt.show()
        if return_fig:
            return fig, ax

    ## Helper Functions
    def _get_faces(self):
        if self.NElem > 0:
            # Get all element faces
            faces,faceconn,faceelem = converter.solid2faces(self.NodeCoords,self.NodeConn,return_FaceConn=True,return_FaceElem=True)
            # Pad Ragged arrays in case of mixed-element meshes
            Rfaces = utils.PadRagged(faces)
            Rfaceconn = utils.PadRagged(faceconn)
            # Get all unique element faces (accounting for flipped versions of faces)
            _,idx,inv = np.unique(np.sort(Rfaces,axis=1),axis=0,return_index=True,return_inverse=True)
            RFaces = Rfaces[idx]
            FaceElem = faceelem[idx]
            RFaces = np.append(RFaces, np.repeat(-1,RFaces.shape[1])[None,:],axis=0)
            inv = np.append(inv,-1)
            RFaceConn = inv[Rfaceconn] # Faces attached to each element
            # Face-Element Connectivity
            FaceElemConn = np.nan*(np.ones((len(RFaces),2))) # Elements attached to each face

            FECidx = (FaceElem[RFaceConn] == np.repeat(np.arange(self.NElem)[:,None],RFaceConn.shape[1],axis=1)).astype(int)
            FaceElemConn[RFaceConn,FECidx] = np.repeat(np.arange(self.NElem)[:,None],RFaceConn.shape[1],axis=1)
            FaceElemConn = [[int(x) if not np.isnan(x) else x for x in y] for y in FaceElemConn[:-1]]


            Faces = utils.ExtractRagged(RFaces[:-1],dtype=int)
            FaceConn = utils.ExtractRagged(RFaceConn,dtype=int)
            return Faces, FaceConn, FaceElemConn
        else:
            return [], [], []
    def _get_edges(self):
        # TODO: This might not work properly with mixed element types - but I think it shoud
        if self.NElem > 0:
            # Get all element edges
            edges, edgeconn, edgeelem = converter.solid2edges(self.NodeCoords,self.NodeConn,return_EdgeConn=True,return_EdgeElem=True,ElemType=self.Type)
            # Convert to unique edges
            Edges, UIdx, UInv = converter.edges2unique(edges,return_idx=True,return_inv=True)
            EdgeElem = np.asarray(edgeelem)[UIdx]
            EdgeConn = UInv[utils.PadRagged(edgeconn)]
            
            rows = EdgeConn.flatten()
            cols = np.repeat(np.arange(self.NElem),[len(x) for x in EdgeConn])
            data = np.ones(len(rows))
            
            mat = scipy.sparse.coo_matrix((data,(rows,cols)),shape=(len(Edges),self.NElem)).tocsr()
            EdgeElemConn = [list(mat.indices[mat.indptr[i]:mat.indptr[i+1]]) for i in range(mat.shape[0])]
            
            return Edges, EdgeConn, EdgeElemConn
        else:
            return [], [], []

    def mesh2dmesh(self, ElemLabels=None):
        """
        Convert to a dynamic mesh (:class:`dmesh`)

        Returns
        -------
        D : mesh.dmesh
            dynamic mesh


        """      

        # Ensure relevant data is in properly typed numpy arrays
        try:
            NodeConn = np.array(self.NodeConn, dtype=np.int64)
        except:
            raise ValueError('Dynamic meshes are only valid for meshes with a single element type.')
        
        NodeCoords = np.array(self.NodeCoords, dtype=np.float64)

        Edges = np.array(self.Edges, dtype=np.int64)

        try:
            Faces = np.array(self.Faces, dtype=np.int64)
        except:
            raise ValueError('Dynamic meshes are not valid for meshes with elements that have mixed faces (e.g. wedges or pyramids).')
        
        # ElemNeighbors = utils.PadRagged(self.ElemNeighbors. fillval=-1)
        
        ElemConn_head = np.full(self.NNode, -1, dtype=np.int64)
        ElemConn_elem = np.array([e for elems in self.ElemConn for e in elems], dtype=np.int64)
        ElemConn_next = np.full(len(ElemConn_elem), -1, dtype=np.int64)
        ElemConn_prev = np.full(len(ElemConn_elem), -1, dtype=np.int64)
        ElemConn_tail = np.full(self.NNode, -1, dtype=np.int64)
        k = 0
        for i,elems in enumerate(self.ElemConn):
            if len(elems) == 0:
                continue
            ElemConn_head[i] = k
            # ElemConn_prev[k] = -1 # Implied by initialization
            for e in elems[:-1]:
                ElemConn_next[k] = k+1
                ElemConn_prev[k+1] = k
                k += 1
            # ElemConn_next[k] = -1 # Implied by initialization
            ElemConn_tail[i] = k
            k += 1
        
        # if self.Type == 'surf':
        #     # Neighbors are connected by edges
        #     NeighborConnection = len(Edges[0])
        # elif self.Type == 'vol':
        #     # Neighbors are connected by faces
        #     NeighborConnection = len(Faces[0])
        if ElemLabels is None:
            ElemLabels = np.empty(0, np.int64)
        else:
            ElemLabels = np.asarray(ElemLabels, np.int64)

        D = dmesh(NodeCoords, NodeConn, ElemConn_head, ElemConn_elem, ElemConn_next, ElemConn_prev, ElemConn_tail, ElemLabels)

        return D
if check_numba():
    import numba
    from numba.experimental import jitclass
    
    @jitclass([
        ('_NodeCoords', numba.float64[:,:]),
        ('_NodeConn', numba.int64[:,:]),
        ('ElemConn_head', numba.int64[:]),
        ('ElemConn_elem', numba.int64[:]),
        ('ElemConn_next', numba.int64[:]),
        ('ElemConn_prev', numba.int64[:]),
        ('ElemConn_tail', numba.int64[:]),
        ('ElemConn_size', numba.int64),
        ('NNode', numba.int64),
        ('NElem', numba.int64),
        ('ElemLabels', numba.int64[:]),
    ])
    class dmesh:
        """
        A specialized mesh class intended for dynamic modification of mesh 
        connectivity. 
        
        The dmesh (Dynamic Mesh) class only supports single element
        type meshes, and only element types that contain a single face type (e.g. 
        wedge elements aren't supported because they have both quadrilateral and
        triangular faces). 
        
        It's recommended that a :class:`dmesh` object is created from a :class:`mesh` 
        object using :meth:`mesh.mesh2dmesh`. Incorrect initialization of the mesh
        will likely lead to misbehavior. 

        Parameters
        ----------
        NodeCoords : np.ndarray(dtype=np.float64)
            Node coordinates array with shape=(n,3)
        NodeConn : np.ndarray
            Node connectivity of elements with shape=(l,m)
            

        """    
        def __init__(self, NodeCoords, NodeConn, ElemConn_head, ElemConn_elem, ElemConn_next, ElemConn_prev, ElemConn_tail,ElemLabels=np.empty(0, np.int64)):
            self._NodeCoords = NodeCoords
            self._NodeConn = NodeConn
            # self.ElemNeighbors = ElemNeighbors
            self.ElemConn_head = ElemConn_head # Points from a node to the first connected element
            self.ElemConn_elem = ElemConn_elem # Element ids
            self.ElemConn_next = ElemConn_next # Points to the next element id connected to the node
            self.ElemConn_prev = ElemConn_prev # Points to the previous element id connected to the node
            self.ElemConn_tail = ElemConn_tail # Points from a node to the last connected element
            self.ElemConn_size = len(self.ElemConn_elem) # 
            # self.ElemConn_slots = [] # E
            # self.NeighborConnection = NeighborConnection # Number of shared nodes required to be considered an element neighbor. If Faces/Edges get added, this could be removed

            self.NNode = len(self._NodeCoords)
            self.NElem = len(self._NodeConn)
            self.ElemLabels = ElemLabels

        @property
        def NodeCoords(self):
            return self._NodeCoords[:self.NNode]
        
        @property
        def NodeConn(self):
            return self._NodeConn[:self.NElem,:]
        
        def addNodes(self,NodeCoords,labels=np.array([], dtype=np.int64)):
            """
            Add nodes to the mesh.

            Parameters
            ----------
            NodeCoords : array_like
                Coordinates of the new node(s). This can either be a single node 
                (shape=(3,)) or multiple nodes (shape=(n,3)).

            """   

            NodeCoords = np.atleast_2d(NodeCoords)
            NewLength = self.NNode + len(NodeCoords)
            if len(self._NodeCoords) < NewLength:
                # Amortized O(1) insertion by doubling  - double the length of the array to make space for the new data.
                # If the new addition is more than double the current length, the array will be extended 
                # to exactly fit the new nodes
                newsize = np.maximum(NewLength,len(self._NodeCoords)*2)
                self._NodeCoords = np.resize(self._NodeCoords, (newsize,3))
                
                # update the ElemConn structure as well
                self.ElemConn_head = np.resize(self.ElemConn_head, newsize)
                self.ElemConn_tail = np.resize(self.ElemConn_tail, newsize)
            
            self._NodeCoords[self.NNode:NewLength] = NodeCoords
            self.ElemConn_head[self.NNode:NewLength] = -1
            self.ElemConn_tail[self.NNode:NewLength] = -1
            self.NNode = NewLength

        def addElem(self,NodeConn,Label=0):
            """
            Add a new element to the mesh. The element should reference 
            nodes that already exist in the mesh.

            Parameters
            ----------
            NodeConn : array_like
                Node connectivity of the new element. This should be a single
                element (shape=(m,))
            """  

            NewLength = self.NElem + 1
            NewElemId = self.NElem
            if len(self._NodeConn) < NewLength:
                # Amortized O(1) insertion by doubling  - double the length of the array to make space for the new data.
                # If the new addition is more than double the current length, the array will be extended 
                # to exactly fit the new elements
                self._NodeConn = np.resize(self._NodeConn, (int(np.maximum(NewLength,len(self._NodeConn)*2)),np.shape(self._NodeConn)[1]))

                if len(self.ElemLabels) > 0:
                    self.ElemLabels = np.resize(self.ElemLabels, int(np.maximum(NewLength,len(self.ElemLabels)*2)))

            self._NodeConn[NewElemId] = NodeConn
            if len(self.ElemLabels) > 0:
                self.ElemLabels[NewElemId] = Label

            # Update ElemConn with new connections
            for node in self._NodeConn[NewElemId]:
                self.addElemConn(node, NewElemId)


            self.NElem += 1

        def removeElem(self, ElemId):
            # Remove an element from the mesh by swap removal
            # Swaps the position of the element definition in NodeConn to the position
            # of the last defined element. References to the last element are updated
            # to refer to the swapped position
            # NOTE: If removing multiple elements, be sure to remove them in reverse
            # order (largest first)

            LastId = self.NElem - 1
            oldnodes = self._NodeConn[LastId].copy()

            # Remove connections to the old element
            for node in self._NodeConn[ElemId]:
                self.removeElemConn(node,ElemId)
    
            if ElemId != LastId:
                # Swap element @ ElemId with the element in the last position
                self._NodeConn[ElemId] = oldnodes
                if len(self.ElemLabels) > 0:
                    self.ElemLabels[ElemId] = self.ElemLabels[LastId]
                # Update ElemConn for each node in the element
                for n in oldnodes:
                    i = self.ElemConn_head[n]
                    while i != -1:
                        if self.ElemConn_elem[i] == LastId:
                            self.ElemConn_elem[i] = ElemId
                        i = self.ElemConn_next[i]

            self.NElem -= 1

        def swapNode(self, NodeId1, NodeId2):

            # Swap all references of Node1 to Node2
            elemconn1 = self.getElemConn(NodeId1)
            elemconn2 = self.getElemConn(NodeId2)
            for ElemId in elemconn1:
                elem = self._NodeConn[ElemId]
                elem[elem == NodeId1] = NodeId2
                self._NodeConn[ElemId] = elem
                self.removeElemConn(NodeId1, ElemId)
                if ElemId not in elemconn2:
                    self.addElemConn(NodeId2, ElemId)
        
        def getElemConn(self, NodeId):
            
            i = self.ElemConn_head[NodeId]
            ElemConn = []
            while i != -1:
                ElemConn.append(self.ElemConn_elem[i])
                i = self.ElemConn_next[i]
            return ElemConn

        def addElemConn(self, NodeId, ElemId):
            # Add a connection between an existing node and an element
            
            if len(self.ElemConn_elem) == self.ElemConn_size:
                # Amortized O(1) insertion by doubling 
                self.ElemConn_elem = np.resize(self.ElemConn_elem, np.maximum(len(self.ElemConn_elem)*2,1))
                self.ElemConn_next = np.resize(self.ElemConn_next, np.maximum(len(self.ElemConn_next)*2,1))
                self.ElemConn_prev = np.resize(self.ElemConn_prev, np.maximum(len(self.ElemConn_prev)*2,1))

            i = self.ElemConn_tail[NodeId]
            newIdx = self.ElemConn_size
            self.ElemConn_elem[newIdx] = ElemId
            if i == -1:
                # If this is the first connection for the node
                self.ElemConn_head[NodeId] = newIdx
                self.ElemConn_prev[newIdx] = -1
            else:
                self.ElemConn_next[i] = newIdx
                self.ElemConn_prev[newIdx] = i

            self.ElemConn_tail[NodeId] = newIdx
            self.ElemConn_next[newIdx] = -1

            self.ElemConn_size += 1

        def removeElemConn(self, NodeId, ElemId):
            # Remove a connection between a node and an element

            # Find the position of the element
            i = self.ElemConn_head[NodeId]
            while i != -1:
                elem = self.ElemConn_elem[i]
                if elem == ElemId:
                    # Remove
                    if self.ElemConn_prev[i] == -1:
                        # this node is the head
                        self.ElemConn_head[NodeId] = self.ElemConn_next[i]
                    else:
                        self.ElemConn_next[self.ElemConn_prev[i]] = self.ElemConn_next[i]

                    if self.ElemConn_next[i] == -1:
                        # this node is the tail
                        self.ElemConn_tail[NodeId] = self.ElemConn_prev[i]
                    else:
                        self.ElemConn_prev[self.ElemConn_next[i]] = self.ElemConn_prev[i]

                    self.ElemConn_elem[i] = -1
                    self.ElemConn_next[i] = -1
                    self.ElemConn_prev[i] = -1
                    break
                else:
                    i = self.ElemConn_next[i]
                    

            # NOTE: Not currently tracking freed slots so the remnants of old connections
            # remain, taking up space. Could implement a tracker of free indices
            # to all for reuse

else:
    class dmesh:
        def __init__(*args):
            raise ImportError('The dmesh class requires numba.\nInstall with `pip install numba`.\nA restart of the python session will be required.')
        