import subprocess
from .utils import get_version_and_codename

def install_ros2_apt_source():

    (version, codename )= get_version_and_codename()
    ros_apt_source_version = "1.1.0"

    print(f"""curl -L -o /tmp/ros2-apt-source.deb "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ros_apt_source_version}/ros2-apt-source_{ros_apt_source_version}.{version if codename is None else codename}_all.deb" """)


    if version is None and codename is None:
        raise Exception("could not get the codename or the version")
    
    commands = {
        "installing curl": "sudo apt update && sudo apt install curl -y",
        "setting ROS apt source version variable": """export ROS_APT_SOURCE_VERSION=$(curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest | grep -F "tag_name" | awk -F\\" '{print $4}')""",
        "downloading ros2 apt source package": f"""curl -L -o /tmp/ros2-apt-source.deb "https://github.com/ros-infrastructure/ros-apt-source/releases/download/{ros_apt_source_version}/ros2-apt-source_{ros_apt_source_version}.{version if codename is None else codename}_all.deb" """,
        "installing ros2 apt source package": "sudo dpkg -i /tmp/ros2-apt-source.deb"
    }


    for description, cmd in commands.items():
        try:
            print()
            print("#################### "+description+" ####################")
            print("#################### "+cmd+" ####################")
            print()
            subprocess.run(cmd, shell=True, check=True)
        except FileNotFoundError as invalid_command:
            raise Exception(str(invalid_command))

                
        except subprocess.CalledProcessError as failed:
            raise Exception( str(failed))


        except Exception as e:
            raise Exception(str(e))