import sys
from .script import calcInertia

def main():
    if len(sys.argv) > 1:
        stl_path = sys.argv[1]
        mass = float(sys.argv[2])
        format_type = sys.argv[3] if len(sys.argv) > 3 else "urdf"

        vals = calcInertia(stl_path, mass)

        header = f"Using {stl_path} of {mass} kg with {format_type} format:\n"
        o = [header] if format_type == "sdf" else [header, "<inertia "]
        for k, v in vals.items():
            if k in ["mass", "volume"]:
                continue
            if format_type == "sdf":
                o.append(f"<{k}>{v}</{k}>\n")
            else:

                o.append(f"{k}=\"{v}\" ")
        o.append("/>") if format_type != "sdf" else None
        print(''.join(o))

    else:
        print(f"Usage: {os.path.basename(__file__)} <stl_file_path> <mass_in_kg> [urdf|sdf]")

if __name__ == "__main__":
    main()

"""
<x>2.2730923034962195e-20</x>
<y>-2.545863379915766e-18</y>
<z>-0.08068086184488206</z>
<ixx>0.017670542003119606</ixx>
<ixy>-1.6880057143163227e-08</ixy>
<ixz>5.23434120494016e-21</ixz>
<iyy>0.01691343657012847</iyy>
<iyz>3.295826741253291e-19</iyz>
<izz>0.0011246971086764758</izz>
<mass>1.36</mass>
<volume>0.0005822416353481113</volume>
"""