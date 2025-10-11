import subprocess

def install_dev_tools():
    commands = {
                    "installing ros-dev-tools": "sudo apt update && sudo apt install ros-dev-tools",
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

            
        print()
        print("#################### DONE ####################")
        print()

          
        