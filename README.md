<h1 align="center">StarLuxe</h1>

<h3 align="center">
	<img src="https://raw.githubusercontent.com/catppuccin/catppuccin/main/assets/misc/transparent.png" height="30px" width="0px"/>
The best ReShade Launcher
	<img src="https://raw.githubusercontent.com/catppuccin/catppuccin/main/assets/misc/transparent.png" height="30px" width="0px"/>
</h3>

<p align="center">
	<img src="https://github.com/Dimitri-Matheus/HSR-Script/assets/121637762/be586150-fa5a-447b-b82a-dcd717827fd1"  alt="image"/>
</p>

## How to use
Download the [latest version](https://github.com/Dimitri-Matheus/HSR-Script/releases) and extract the file. Then, run `StarLuxe.exe`

Once open, fill in the necessary information and download the ReShade presets if you wish to use them. 
On the main screen, press the **Start** button
<p align="center">
	<b>✧ Select the game you want to use ReShade and enjoy ✧</b>
</p>


---

## Attributes
- **Launcher** — Allows applying ReShade to selected games
- **Custom Themes & Preset Packs** — Provides support for custom themes and predefined Reshade preset packs
- **GitHub Integration** — Enables downloading your own Reshade presets directly from GitHub.

---

## Development

- Clone this [repository](https://github.com/Dimitri-Matheus/HSR-Script.git)
   - Install the required libraries with the following command

<img width="1460" height="614" alt="terminal" src="https://github.com/user-attachments/assets/edf80a22-b281-43f0-a8ca-38ff2bad2ac9" />

<details>
<summary><strong>How to create Custom Themes?</strong></summary>
   
1. Download [CTkThemeMaker](https://github.com/Akascape/CTkThemeMaker?tab=readme-ov-file)
2. Navigate to the `theme/` directory, copy `default.json` and rename the copy (e.g. `custom_theme.json`)  
3. Launch **CTkThemeMaker**, load `custom_theme.json` and edit each section according to your preference  
   - Once your theme is saved, open the `settings.json` file and update the **Launcher** section to point to your new theme:

     ```json
     "Launcher": {
       "gui_theme": "theme\\custom_theme.json",
       "last_played_game": ""
     }
     ```
4. Check the [documentation](https://customtkinter.tomschimansky.com/documentation/color/) to learn more!
</details>

<details>
<summary><strong>How to add your ReShade Pack?</strong></summary>

1. Create a GitHub repo and add a `Presets/` folder with your .ini files
   - In the `settings.json` file, set the preset_folder value to match the name of that folder:

    ```json
    "Account": {
      "github_name": "your-username",
      "preset_folder": "Presets/",
      "repository_name": "your-repo"
     }
     ```
2. Restart `StarLuxe.exe` and download your preset from the Settings section
</details>

---

> [!IMPORTANT]
> Your antivirus might block the application from running. 
> This happens because the build created by PyInstaller can cause a false positive. To learn more, click [HERE](https://nitratine.net/blog/post/issues-when-using-auto-py-to-exe/#my-antivirus-detected-the-exe-as-a-virus)
> The application is safe and contains no viruses. To prevent interference, it is recommended to add the program to your antivirus exclusion or whitelist before running it, rather than disabling your antivirus entirely.

> [!WARNING]
> The use of Reshade may result in a ban, although the likelihood is low.
> Use at your own risk! Sharing your UID may increase the risk of being banned in the game.


#

## Support this Project ☕

Did this project help you? Support me by buying a coffee!

[![Buy Me a Coffee]()

**✦ Thanks for your support! ✦**

## Credits
<p>
	<b>ReShade</b> developer for developing ReShade
	<br>
	<b>SweetFX</b> developer for creating SweetFX shaders collection/set/pack
	<br>
</p>

***This project was developed by me***
