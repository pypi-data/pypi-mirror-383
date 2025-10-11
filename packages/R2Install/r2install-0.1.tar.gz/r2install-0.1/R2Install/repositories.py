import subprocess

def enable_repositories():
    commands = {
                    "installing software-properties-common": "sudo apt install software-properties-common",
                    "adding universe repository": "sudo add-apt-repository universe"
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

          
        