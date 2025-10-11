import os

def post_install():
        
    home = os.path.expanduser("~")
    files_and_lines = {
        ".bashrc": "source /opt/ros/jazzy/setup.bash",
        ".bash_profile": "source /opt/ros/jazzy/setup.bash",
        ".zshrc": "source /opt/ros/jazzy/setup.zsh",
        ".profile": "source /opt/ros/jazzy/setup.sh",
    }

    for filename, line in files_and_lines.items():
        full_path = os.path.join(home, filename)
        append_if_missing(full_path, line)
            

def append_if_missing(file_path, line):
    if os.path.exists(file_path):
        with open(file_path) as f:
            if line not in f.read():
                with open(file_path, "a") as fa:
                    fa.write(f"\n{line}\n")
