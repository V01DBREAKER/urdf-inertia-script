# urdf-inertia-script
A python script used to modify generated URDFs from onshape-to-robot. Also can recalculate inertias using MeshLab.

Inertias from [onshape-to-robot](https://github.com/rhoban/onshape-to-robot/) weren't behaving correctly in Gazebo Sim when using the [DetachableJoint plugin](https://gazebosim.org/api/gazebo/6/classignition_1_1gazebo_1_1systems_1_1DetachableJoint.html) to close kinematic loops.

Modify for yourself before using!

This tool is based off [this Gazebo Classic tutorial](https://classic.gazebosim.org/tutorials?tut=inertia)

Credit to [Hamza Merzić](https://github.com/hamzamerzic) for his advice on meshlab filters and [online tool](https://www.hamzamerzic.info/mesh_cleaner/) to which values were compared to.

Credit to [this repo](https://github.com/vonunwerth/MeshLabInertiaToURDF) for inspiration
