from .steps import get_steps

def main():
    steps = get_steps()


    for name, func in steps.items():
        print()
        print("######## "+ name + " ########")
        print()

        try:
            func()
        except Exception as e:
            print(str(e))
        
            
            


main()