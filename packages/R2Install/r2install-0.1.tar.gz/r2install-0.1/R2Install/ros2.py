import subprocess
from .utils import update, upgrade

def install():
    commands = {
                    "installing ros jazzy desktop": "sudo apt install ros-jazzy-desktop",
                    "installing ros jazzy base": "sudo apt install ros-jazzy-ros-base",

                }

    update()
    upgrade()

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

            
        print()
        print("#################### DONE ####################")
        print()

          
        