User Guide
==========

.. toctree::
    :maxdepth: 2
    :hidden:
    
    guide/installation
    guide/getting_started
    guide/what_mesh
    guide/mesh_class
    guide/elem_types
    guide/connectivity
    guide/implicit_meshing
    guide/image_meshing
    guide/csg
    guide/io
    guide/ref

Package Overview
----------------

MyMesh has a collection of algorithms for generation, manipulation, and analysis
of 2D and 3D meshes. These capabilities are organized into the following 
submodules:

.. autosummary:: 
    :nosignatures:
    
    ~mymesh.booleans
    ~mymesh.contour
    ~mymesh.converter
    ~mymesh.curvature
    ~mymesh.delaunay
    ~mymesh.image
    ~mymesh.implicit
    ~mymesh.improvement
    ~mymesh.tree
    ~mymesh.primitives
    ~mymesh.quality
    ~mymesh.rays
    ~mymesh.register
    ~mymesh.utils
    ~mymesh.visualize

Importing MyMesh
----------------

There are several ways MyMesh can be imported and used. 

.. code::

    import mymesh
    S = mymesh.primitives.Sphere([0,0,0], 1)

Alternatively, submodules can be imported directly as

.. code::

    from mymesh import primitives
    S = primitives.Sphere([0,0,0], 1)

Or to import all submodules (and the :class:`mesh` class), they can be imported
as using :code:`*`, but this should be done carefully to avoid conflicts with
other variables or modules that might have the same names. 

.. code::

    from mymesh import *
    S = primitives.Sphere([0,0,0], 1)

