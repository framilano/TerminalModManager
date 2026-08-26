import json
import os

def load_games_setup():
    f = open("games_setup.json", "r")
    links = json.load(f)
    f.close()
    
    # Removing trailing slashes from paths
    for mod in links:
        if (mod["gameroot_path"][-1] == '/'): mod["gameroot_path"] = mod["gameroot_path"][:-1]
        if (mod["backup_path"][-1] == '/'): mod["backup_path"] = mod["backup_path"][:-1]
        if (mod["mods_path"][-1] == '/'): mod["mods_path"] = mod["mods_path"][:-1]
    
    return links

def link_files_recursively(gameroot_path, backup_path, mod_root, current_root):
    for filename in os.listdir(mod_root + current_root):
        
        mod_subpath = current_root + "/"
        mod_file_subpath = mod_subpath + filename
        mod_file_abs_path = mod_root + mod_file_subpath
        
        #print("Checking: ", mod_file_abs_path)
        if (os.path.isfile(mod_file_abs_path)):
            
            vanilla_file_path = gameroot_path + mod_file_subpath
            
            if (os.path.islink(vanilla_file_path)):
                print(f"File {filename} is already being symlinked, skipping backup, removing current link and replacing it")
                os.system(f'rm "{vanilla_file_path}"')

            elif (os.path.exists(vanilla_file_path)):
                print("Backing up file " + vanilla_file_path)
                #Backing up existing file
                os.system(f'mkdir -p "{backup_path + mod_subpath}" && mv "{vanilla_file_path}" "{backup_path + mod_subpath}"')

            print(f"Linking file {filename}...")
            #Linking new file
            os.system(f'ln -s "{mod_file_abs_path}" "{vanilla_file_path}"')
        else:
            link_files_recursively(gameroot_path, backup_path, mod_root, mod_file_subpath)

def restore_files_recursively(gameroot_path, backup_path, mod_root, current_root):
    for filename in os.listdir(mod_root + current_root):
        
        mod_subpath = current_root + "/"
        mod_file_subpath = mod_subpath + filename
        mod_file_abs_path = mod_root + mod_file_subpath
        
        #print("Checking: ", mod_file_abs_path)
        if (os.path.isfile(mod_file_abs_path)):
            
            vanilla_path = gameroot_path + mod_subpath
            vanilla_file_path = gameroot_path + mod_file_subpath
            backup_file_path = backup_path + mod_subpath + filename

            if (os.path.islink(vanilla_file_path)):
                print(f"Found symlink {filename}, removing it...")
                os.system(f'rm "{vanilla_file_path}"')
                if (os.path.exists(backup_file_path)):
                    print(f"Found backup for {filename}, restoring it...")
                    os.system(f'mv "{backup_file_path}" "{vanilla_path}"')
            else:
                print(f"File {filename} is already in its original state")

        else:
            restore_files_recursively(gameroot_path, backup_path, mod_root, mod_file_subpath)

def mod_symlinking_status(gameroot_path, backup_path, mod_root, current_root):
    """
    Returns the specified mod linking status
    @param gameroot_path: this is the original game folder path
    @param backup_path: this is the backup folder path where linked files are being copied
    @param mod_root: this is the current mod being linked folder path
    @param current_root: this is the current subfolder of the mod being checked for symlinking

    @return: 0 if symlinking is enabled, 1 if disabled, 2 if disabled with of conflicting mods if enabled
    """
    for filename in os.listdir(mod_root + current_root):
            
        mod_subpath = current_root + "/"
        mod_file_subpath = mod_subpath + filename
        mod_file_abs_path = mod_root + mod_file_subpath
        
        #print("Checking: ", mod_file_abs_path)
        if (os.path.isfile(mod_file_abs_path)):
            
            vanilla_file_path = gameroot_path + mod_file_subpath
            
            if (os.path.islink(vanilla_file_path)):
                if (os.readlink(vanilla_file_path).strip() == mod_file_abs_path.strip()):
                    #print(f"File {filename} is already being symlinked, mod is symlinked")
                    return 0
                else:
                    #print(f"File {filename} is already being symlinked, but not for mod {mod_root}")
                    return 2
            else: return 1
                
        else: return mod_symlinking_status(gameroot_path, backup_path, mod_root, mod_file_subpath)
    
def handle_current_games():
    games_setup = load_games_setup()

    # Clearing screen
    os.system('clear')

    for (index, game) in zip(range(0, len(games_setup)), games_setup):
        print(f"{index}: {game["name"]}")

    answer = input("Select which game to handle: ")
    print("\n")
    index = int(answer.strip())

    gameroot_path = games_setup[index]["gameroot_path"]
    backup_path = games_setup[index]["backup_path"]
    # Mods paths are read at runtime looking at current_link.json mods path
    mods_paths = [games_setup[index]["mods_path"] + "/" + mod_name for mod_name in os.listdir(games_setup[index]["mods_path"])]
    mods_paths.sort()
    
    # Clearing screen
    os.system('clear')
    
    # Showing the mods status, if they're already linked or not
    for (index, mod_root) in zip(range(0, len(mods_paths)), mods_paths):
        symlink_status = mod_symlinking_status(gameroot_path, backup_path, mod_root, "")
        if (symlink_status == 0): print(f"{index} {'✅'}: {mod_root.split("/")[-1]}")
        elif (symlink_status == 1): print(f"{index} {'❌'}: {mod_root.split("/")[-1]}")
        else: print(f"{index} {'❌'}: {mod_root.split("/")[-1]} - (WARNING - This disabled mod has some conflicting files with other enabled mods, enabling it will overwrite the previous linking)")
    
    answer = input("Select which mods to edit (example: 0 2 4, or -1 for all of them) and press Enter: ")
    
    mods_indexes = [int(index) for index in answer.strip().split(" ")]

    answer = input("Should I (e)nable linking or (d)isable linking? e/d ")
    print("\n")

    if (answer.strip() == 'e'): 
        for (index, mod_path) in zip(range(0, len(mods_paths)), mods_paths):
            if (index in mods_indexes or mods_indexes[0] == -1): 
                link_files_recursively(gameroot_path, backup_path, mod_path, "")
    else: 
        for (index, mod_path) in zip(range(0, len(mods_paths)), mods_paths):
            if (index in mods_indexes or mods_indexes[0] == -1): 
                restore_files_recursively(gameroot_path, backup_path, mod_path, "")




def main():
    print("Welcome to Terminal Mod Manager")
    while(True):
        answer = input("Do you (h)andle existing games' mods, (a)dd a new game or exit? h/a/e ")
        if (answer.strip() == 'h'): handle_current_games()
        if (answer.strip() == 'e'): break



if (__name__ == '__main__'): main()