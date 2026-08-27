# TerminalModManager
A no-nonsense mod manager written in Python, only through CLI and Linux currently.

Use Linux symlinking to put mods inside a game folder without actually moving files, you can disable/restore original files automatically without having to save/backup them manually.

My main use case was [BBLauncher](https://github.com/rainmakerv3/BB_Launcher) conflicting with Shadnet Bloodborne network code and BBLauncher was the only mod manager available for this game, now I can use ShadPS4 with my mod manager.
Please backup your game files anyway before using this tool, I programmed it in like 3 hours.

## Configuration
Create a file called `games_setup.json` (or use the one I provide, or just create a new one using the program itself, there's a small wizard to help adding new games), this json contains a list of games you want to handle, for Bloodborne on shadPS4 this is the content of `games_setup.json`

```
[
    {
        "name": "Bloodborne ShadPS4 Mods",
        "gameroot_path": "/home/francesco/Games/EmulationLibrary/ROMs/ps4/CUSA03173/dvdroot_ps4",
        "backup_path": "/home/francesco/Games/EmulationLibrary/ROMs/ps4/CUSA03173-backup",
        "mods_path": "/home/francesco/Games/EmulationLibrary/ROMs/ps4/CUSA03173-mods"
    }
]
```

- **name**: a custom name you decided to identify the game to handle
- **gameroot_path**: your game root path, this where the symlinking will start
- **backup_path**: this is a backup folder you choose, every symlinking that overwrites existing game files will first save the original file in this folder
- **mods_path**: this is your mods folder, put your mods folders here, each mod will have a separate folder contained in mods_path

## Example
The main use case here is Bloodborne PC, but you can easily extend this tool behaviour for every game.

Let's say `mods_path` is `/home/francesco/Games/EmulationLibrary/ROMs/ps4/CUSA03173-mods` and it contains:
- Hidden AA
- Nightreign AA Drawparams darker

Now these folders content will be symlinked using as root folder the `gameroot_path`. 
The CLI allows you enable/disable specific mods, the prompt will show you:

```
0 ❌: BBEnhanced
1 ❌: Bloodborne Boss Arena (Sandbox 1.0.3)
2 ❌: Elden Ring Style - Modern Xbox prompts
3 ❌: Hidden AA - (WARNING - This disabled mod has some conflicting files with other enabled mods, enabling it will overwrite the previous linking)
4 ✅: MOAL
5 ✅: Nightreign AA Drawparams darker
6 ✅: Pointlight Removal (fixes excessive brightness)
7 ✅: Vertex Explosion fix - modloader friendly
Select which mods to edit (example: 0 2 4, or -1 for all of them) and press Enter: 
```

As you can see ❌ means the mod is not symlinked (disabled), ✅ means the mod is symlinked (enabled). I even added an alert to check if enabling specific disabled mods will conflict other enabled mods. In this case `Hidden AA` could cause conflicts with `Nightreign AA Drawparam darker`.
