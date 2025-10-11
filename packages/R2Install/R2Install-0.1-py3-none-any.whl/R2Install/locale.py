import subprocess
import sys

def check_locale() -> bool :
    locale_check =subprocess.check_output("locale | grep UTF-8", shell=True)

    return "UTF-8" in locale_check.decode("utf-8")


def setlocale():   
    
    if check_locale():
        return {'success': True}
    else :
        commands = {
                    "installing locales": "sudo apt update && sudo apt install locales",
                    "generating US English locales": "sudo locale-gen en_US en_US.UTF-8",
                    "updating locale settings": "sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8",
                    "exporting LANG variable": "export LANG=en_US.UTF-8"
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

        if check_locale():
            return {'success': True}  
        else :
            return {'success': True, 'message': 'something went wrong'}
            
        