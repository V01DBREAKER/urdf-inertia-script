# urdf-modifier
A python script used to modify generated URDFs from onshape-to-robot. Also can recalculate inertias using MeshLab.

Inertias from onshape-to-robot weren't behaving correctly in Gazebo Sim when using the DetachableJoint plugin to close kinematic loops.
https://gazebosim.org/api/gazebo/6/classignition_1_1gazebo_1_1systems_1_1DetachableJoint.html
https://github.com/rhoban/onshape-to-robot/

This tool is based off [this Gazebo Classic tutorial](https://classic.gazebosim.org/tutorials?tut=inertia) and [this repo](https://github.com/vonunwerth/MeshLabInertiaToURDF)

Compared to values from:
https://www.hamzamerzic.info/mesh_cleaner/ \
It is very similar.

Modify for yourself before using!
