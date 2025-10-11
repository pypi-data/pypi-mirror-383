from .repositories import enable_repositories
from .ros2_apt_source import install_ros2_apt_source
from .ros_dev_tools import install_dev_tools
from .ros2 import install
from .post_install import post_install
from .locale import setlocale

def get_steps():
    return {
                "set_locale": setlocale,
                "enable_repositories": enable_repositories,
                "ros2_apt_source": install_ros2_apt_source,
                "install dev tools": install_dev_tools,
                "install ros2": install,
                "post installation": post_install

    }