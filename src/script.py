"""
Use on urdf after onshape-to-robot, plz enable dynamics when exporting the urdf first!
This tool will look for the stl model of each link with an inertia and use them to recalculate inertias.
There are also other helper functions that may be useful

Expected input:
<robot>
    <link name="l2long">
        <visual>
            <origin xyz="-0.14313438028418518089 -0.089852930840691458414 -0.012499999999999983347" rpy="-1.3540116215689451197e-17 2.7136208718968067492e-17 -6.1954989111890029015e-17" />
            <geometry>
                <mesh filename="file://$(find rover_description)/arm/newmeshes/l2long.stl"/>
            </geometry>
            <material name="l2long_material">
                <color rgba="0.86666666666666669627 0.074509803921568626417 0.32549019607843138191 1.0"/>
            </material>
        </visual>
        <collision>
            <origin xyz="-0.14313438028418518089 -0.089852930840691458414 -0.012499999999999983347" rpy="-1.3540116215689451197e-17 2.7136208718968067492e-17 -6.1954989111890029015e-17" />
            <geometry>
                <mesh filename="file://$(find rover_description)/arm/newmeshes/l2long.stl"/>
            </geometry>
        </collision>
        <inertial>
            <mass value="0.251" />
            <origin xyz="5.4346870000e-02 3.4116440000e-02 1.2500000000e-02" rpy="0 0 0" />
            <inertia ixx="8.7767360018e-04" ixy="-1.2976894559e-03" ixz="-4.8761081726e-11" iyy="2.1302489598e-03" iyz="-5.4481655560e-12" izz="2.9713597961e-03" />
        </inertial>
    </link>
</robot>

Gazebo expects:
    - Mass in kg (Calculated by onshape, after adding a material)
    - Center of Mass in length vector
    - Length in meters

Onshape STLs
    - Length in meters
    - Mass in kg
"""
import os
import sys
import xml.etree.ElementTree as etree
import pymeshlab


from typing import Dict, List, Tuple

def calcInertia(mesh_filename: str, mass_value: float) -> Dict[str, float]:
    """ Recalculates Inertias of Links with mass and STL file using Meshlab
        Modifies the given xml tree with the values
        Based on: https://github.com/vonunwerth/MeshLabInertiaToURDF/blob/master/main.py
         and the description of https://www.hamzamerzic.info/mesh_cleaner/
    """
    ms = pymeshlab.MeshSet()

    ms.load_new_mesh(mesh_filename)

    # We removed duplicate vertices, duplicate faces and faces with non manifold edges from your 3D model. 
    ms.meshing_remove_duplicate_faces()
    ms.meshing_remove_duplicate_vertices()
    ms.meshing_repair_non_manifold_edges(method=0)

    # generate first values
    geo = ms.get_geometric_measures()
    if 'inertia_tensor' not in geo.keys():
        # mesh is not watertight
        ms.generate_convex_hull()           # turn into convex hull
        geo = ms.get_geometric_measures()   # reevaluate inertia tensor

    com = geo['center_of_mass']
    volume = geo['mesh_volume']
    tensor = geo['inertia_tensor'] / volume * mass_value
    
    """ use for debugging
    ptxt = f"<pose> {com[0]} {com[1]} {com[2]} </pose>\n" + \
        f"<ixx> {tensor[0, 0]:.10e} </ixx>\n" + \
        f"<ixy> {tensor[1, 0]:.10e} </ixy>\n" + \
        f"<ixz> {tensor[2, 0]:.10e} </ixz>\n" + \
        f"<iyy> {tensor[1, 1]:.10e} </iyy>\n" + \
        f"<iyz> {tensor[1, 2]:.10e} </iyz>\n" + \
        f"<izz> {tensor[2, 2]:.10e} </izz>\n" + \
        f"<mass> {mass_value} </mass>\n" + \
        f"<volume> {volume} </volume>"

    print(ptxt)
    """

    return {
        'x': com[0],
        'y': com[1],
        'z': com[2],
        'ixx': tensor[0, 0], 
        'ixy': tensor[1, 0], 
        'ixz': tensor[2, 0], 
        'iyy': tensor[1, 1], 
        'iyz': tensor[1, 2], 
        'izz': tensor[2, 2], 
        'mass': mass_value, 
        'volume': volume
    }

def overrideInertias(tree: etree.ElementTree, mesh_dir: str) -> None:
    """ Recalculates Inertias of Links with mass and STL file using Meshlab
        Modifies the given xml tree with the values
    """
    ms = pymeshlab.MeshSet()
    for link in tree.getroot().findall("link"):
        if link.find("inertial") is None:
            # if no inertial there will be no mass value
            # if no visual there will be no stl mesh
            print(f"Skipping link: {link.get("name")}, no inertial tag found")
            continue

        print(f"Calculating inertia of link: {link.get("name")}")

        inertial_element = link.find("inertial") 
        mass_value = float(inertial_element.find("mass").get("value").strip())
        origin_element = inertial_element.find("origin")
        inertia_element = inertial_element.find("inertia")

        # assume each mesh has the same name as its link
        mesh_filename = os.path.join(mesh_dir, link.get("name") + ".stl")
        if not os.path.isfile(mesh_filename):
            print(f"Error: Could not find file of {link.get("name")}")
            continue

        try:
            output = calcInertia(mesh_filename, mass_value)
        except pymeshlab.pmeshlab.PyMeshLabException as e:
            print(f"Error: {e}")
            continue

        origin_element.set("xyz", f"{output['x']:.10e} {output['y']:.10e} {output['z']:.10e}")
        inertia_element.set("ixx", f"{output['ixx']:.10e}")
        inertia_element.set("ixy", f"{output['ixy']:.10e}")
        inertia_element.set("ixz", f"{output['ixz']:.10e}")
        inertia_element.set("iyy", f"{output['iyy']:.10e}")
        inertia_element.set("iyz", f"{output['iyz']:.10e}")
        inertia_element.set("izz", f"{output['izz']:.10e}")



def main():
    if len(sys.argv) > 1:
        xml_filename = sys.argv[1]

        mesh_dir = ""
        if len(sys.argv) > 2:
            mesh_dir = sys.argv[2]

        tree = etree.parse(xml_filename)

        # functions here to modify xml tree
        overrideInertias(tree, mesh_dir)
        #meshRelink(tree)
        #removeContinuous(tree)

        # write tree to file
        tree.write(f"{xml_filename}+out.urdf")

    else:
        print(f"Usage: {os.path.basename(__file__)} <urdf_file_path>")


if __name__ == "__main__":
    # manual debugging
    # print(calcInertia("/home/nova/urdf/ee.stl",0.768))
    main()


"""
Other useful functions you may want to use...
"""
def autoInertia(tree: etree.ElementTree) -> None:
    """ Adds auto inertial tags to urdf 
        Could be useful for AUTO calculating inertias if we update to gazebo 9.1
    """
    for link in tree.getroot().findall("link"):
        if link.find("inertial") is None or link.find("visual") is None:
            # if no inertial there will be no mass value
            # if no visual there will be no stl mesh
            print(f"Skipping link: {link.get("name")}")
            continue
        link.remove(link.find("inertial"))
        link.append(etree.Element("inertial", attrib={'auto':"true"}))


def meshRelink(tree: etree.ElementTree) -> None:
    """ Changes all mesh filenames from package:// to file://
        Modifies the given xml tree with the values!
        Note this script does not expect meshes in collision tags, 
            if you have meshes in your collision tags please use scads to replace them.
    """
    for link in tree.getroot().findall("link"):
        for visual in link.findall("visual"):
            mesh_element = visual.find("geometry").find("mesh")
            if visual.find("geometry").find("mesh") is None:
                continue

            filename = mesh_element.get("filename")
            filename = "file" + filename[7:]    # package is 7 letters
            mesh_element.set("filename", filename)


def removeContinuous(tree: etree.ElementTree) -> None:
    """ Removes all _continuous from joint names """
    for joint in tree.getroot().findall("joint"):
        joint_name = joint.get("name")
        if joint_name.endswith("_continuous"):
            joint.set("name", joint_name[:-11])


    