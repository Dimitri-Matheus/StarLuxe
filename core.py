import os
import sys
import subprocess

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


injector_path = resource_path("script\\Injector.exe")

# Function to gui.py
def verification(impact_path, text):
    missing_file = "Injector.exe" if not os.path.isfile(injector_path) else f"The specified file was not found!"
    if not os.path.isfile(injector_path) or not os.path.isfile(impact_path):
        text.configure(text=f"{missing_file}")
        raise FileNotFoundError("The files were not found!")
    
    elif os.path.isfile(injector_path) and os.path.isfile(impact_path):
        print("All necessary files were found!")
    else:
        print("Failed to read the files!")

def run_command(impact_path, mode):
    bat_file_path = os.path.join(resource_path("script\\"), "HSR+.bat")
    bat_file_path_playnite = os.path.join(resource_path("script\\"), "HSR+Playnite.bat")
    bat_content = f"""@echo off
    powershell -Command "Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy Unrestricted"
    powershell -Command "Start-Process -FilePath Injector.exe -ArgumentList 'StarRail.exe' -Verb RunAs"
    powershell -Command "Start-Process -FilePath '{impact_path}' -Verb RunAs"
    powershell -Command "Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy Restricted"
    exit
    """
    
    bat_content_playnite = f"""@echo off
    powershell -ExecutionPolicy Bypass -Command "Start-Process -FilePath Injector.exe -ArgumentList 'StarRail.exe' -Verb RunAs"
    powershell -ExecutionPolicy Bypass -Command "Start-Process -FilePath '{impact_path}' -Verb RunAs"
    exit
    """
    
    try:
        #if not os.path.exists(bat_file_path):
        with open(bat_file_path, "w") as bat_file, open(bat_file_path_playnite, "w") as bat_file_playnite:
            bat_file.write(bat_content)
            bat_file_playnite.write(bat_content_playnite)
            subprocess.run(['explorer', os.path.dirname(bat_file_path)])
            print(f"Batch file created or updated at: {bat_file_path} and {bat_file_path_playnite}")

    except (OSError, IOError, subprocess.CalledProcessError, Exception) as e:
        print(f"An error occurred: {e}")

    #else:
        #print(f"{os.path.basename(bat_file_path)} already exists")

    #if mode == True:
            #os.startfile(bat_file_path)
            #subprocess.run([bat_file_path], check=True)

    #else:
        #print(f"An error occurred while executing the command: {e}")

# Test
#verification(r"C:\Games\Star Rail\Games")
#run_command(r"C:\Games\Star Rail\Games\StarRail.exe", False)