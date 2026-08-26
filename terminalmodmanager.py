from json import dump, load
from os import path, system, listdir, readlink
import sys

def load_games_setup():
    """
    Loads games_setup.json and cleans up the game paths
    @return: the list of game setups
    """
    base_path = path.dirname(path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))
    json_path = base_path + "/games_setup.json"
    if (not path.exists(json_path)): 
        system('echo "[]" > \"' + json_path + '\"')
        print("Created games_setup.json file")
        return
    f = open(json_path, "r")
    links = load(f)
    f.close()
    
    # Removing trailing slashes from paths
    for mod in links:
        if (mod["gameroot_path"][-1] == '/'): mod["gameroot_path"] = mod["gameroot_path"][:-1]
        if (mod["backup_path"][-1] == '/'): mod["backup_path"] = mod["backup_path"][:-1]
        if (mod["mods_path"][-1] == '/'): mod["mods_path"] = mod["mods_path"][:-1]
    
    return links

def link_files_recursively(gameroot_path, backup_path, mod_root, current_root):
    """
    Recursively symlinks the mod files into the game root, backing up any replaced files
    @param gameroot_path: this is the original game folder path
    @param backup_path: this is the backup folder path where replaced files are moved
    @param mod_root: this is the mod folder path being linked
    @param current_root: this is the current subfolder of the mod being processed
    """
    for filename in listdir(mod_root + current_root):
        
        mod_subpath = current_root + "/"
        mod_file_subpath = mod_subpath + filename
        mod_file_abs_path = mod_root + mod_file_subpath
        
        #print("Checking: ", mod_file_abs_path)
        if (path.isfile(mod_file_abs_path)):
            
            vanilla_file_path = gameroot_path + mod_file_subpath
            vanilla_path = gameroot_path + mod_subpath

            if (path.islink(vanilla_file_path)):
                print(f"File {filename} is already being symlinked, skipping backup, removing current link and replacing it")
                system(f'rm "{vanilla_file_path}"')

            elif (path.exists(vanilla_file_path)):
                print("Backing up file " + vanilla_file_path)
                #Backing up existing file
                system(f'mkdir -p "{backup_path + mod_subpath}" && mv "{vanilla_file_path}" "{backup_path + mod_subpath}"')

            print(f"Linking file {filename}...")
            # Create folder if not exists and link new file
            if (not path.exists(vanilla_path)): system(f'mkdir -p "{vanilla_path}"')
            system(f'ln -s "{mod_file_abs_path}" "{vanilla_file_path}"')
        else:
            link_files_recursively(gameroot_path, backup_path, mod_root, mod_file_subpath)

def restore_files_recursively(gameroot_path, backup_path, mod_root, current_root):
    """
    Recursively removes the mod's symlinks and restores the backed-up files
    @param gameroot_path: this is the original game folder path
    @param backup_path: this is the backup folder path where files are restored from
    @param mod_root: this is the mod folder path being unlinked
    @param current_root: this is the current subfolder of the mod being processed
    """
    for filename in listdir(mod_root + current_root):
        
        mod_subpath = current_root + "/"
        mod_file_subpath = mod_subpath + filename
        mod_file_abs_path = mod_root + mod_file_subpath
        
        #print("Checking: ", mod_file_abs_path)
        if (path.isfile(mod_file_abs_path)):
            
            vanilla_path = gameroot_path + mod_subpath
            vanilla_file_path = gameroot_path + mod_file_subpath
            backup_file_path = backup_path + mod_subpath + filename

            if (path.islink(vanilla_file_path)):
                print(f"Found symlink {filename}, removing it...")
                system(f'rm "{vanilla_file_path}"')
                if (path.exists(backup_file_path)):
                    print(f"Found backup for {filename}, restoring it...")
                    system(f'mv "{backup_file_path}" "{vanilla_path}"')
                if (len(listdir(vanilla_path)) == 0): 
                    print(f"Removing empty mod directory {vanilla_path}...")
                    system(f'rmdir "{vanilla_path}"')
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
    for filename in listdir(mod_root + current_root):
            
        mod_subpath = current_root + "/"
        mod_file_subpath = mod_subpath + filename
        mod_file_abs_path = mod_root + mod_file_subpath
        
        #print("Checking: ", mod_file_abs_path)
        if (path.isfile(mod_file_abs_path)):
            
            vanilla_file_path = gameroot_path + mod_file_subpath
            
            if (path.islink(vanilla_file_path)):
                if (readlink(vanilla_file_path).strip() == mod_file_abs_path.strip()):
                    #print(f"File {filename} is already being symlinked, mod is symlinked")
                    return 0
                else:
                    #print(f"File {filename} is already being symlinked, but not for mod {mod_root}")
                    return 2
            else: return 1
                
        else: return mod_symlinking_status(gameroot_path, backup_path, mod_root, mod_file_subpath)
    
def handle_current_games():
    """
    Lists the configured games, shows the mods' linking status and links or restores the selected mods
    """
    games_setup = load_games_setup()

    if (games_setup is None or len(games_setup) == 0):
        print("First you need to add games, then you can handle their mods")
        return

    # Clearing screen
    #system('clear')

    for (index, game) in zip(range(0, len(games_setup)), games_setup):
        print(f"{index}: {game["name"]}")

    answer = input("Select which game to handle: ")
    print("\n")
    index = int(answer.strip())

    gameroot_path = games_setup[index]["gameroot_path"]
    backup_path = games_setup[index]["backup_path"]
    # Mods paths are read at runtime looking at current_link.json mods path
    mods_paths = [games_setup[index]["mods_path"] + "/" + mod_name for mod_name in listdir(games_setup[index]["mods_path"])]
    mods_paths.sort()
    
    # Clearing screen
    system('clear')
    
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

def add_new_game():
    """
    Asks for the details of a new game and appends it to games_setup.json
    """
    games_setup = load_games_setup()

    name = input("Enter a custom name for this game handler: ").strip()
    gameroot_path = input("Enter the path of the game itself, this will be the base path where mods will be symlinked: ").strip().rstrip('/')
    backup_path = input("Enter the backup path where to store original vanilla files: ").strip().rstrip('/')
    mods_path = input("Enter the mods path where the mods are actually stored: ").strip().rstrip('/')

    games_setup.append({
        "name": name,
        "gameroot_path": gameroot_path,
        "backup_path": backup_path,
        "mods_path": mods_path
    })

    base_path = path.dirname(path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))
    json_path = base_path + "/games_setup.json"
    f = open(json_path, "w")
    dump(games_setup, f, indent=4)
    f.close()

    print(f"Added {name} to games_setup.json")


def main():
    """
    Entry point: runs the interactive menu loop until the user exits
    """
    print("Welcome to Terminal Mod Manager")
    while(True):
        answer = input("Do you (h)andle existing games' mods, (a)dd a new game or exit? h/a/e ")
        if (answer.strip() == 'h'): handle_current_games()
        if (answer.strip() == 'a'): add_new_game()
        if (answer.strip() == 'e'): break



if (__name__ == '__main__'): main()