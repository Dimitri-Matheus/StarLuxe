<h1 align="center">StarLuxe Launcher</h1>

<p align="center">
	<img width="1024" height="1024" src="https://github.com/user-attachments/assets/1a7ee5a5-b672-4b08-b90d-ce36272a675c"  alt="image"/>
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
- **Launcher:** Allows applying ReShade to selected games
- **Custom Themes & Preset Packs:** Provides support for custom themes and predefined Reshade preset packs
- **GitHub Integration:** Enables downloading your own Reshade presets directly from GitHub.

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
   - In the `settings.json` file, set the `preset_folder` value to match the folder name you configured in your GitHub repository.
 	Don’t forget to set your **GitHub username** and **repository name** as well:

    ```json
    "Account": {
      "github_name": "your-username",
      "preset_folder": "Presets/",
      "repository_name": "your-repo"
     }
     ```
   - Also, define the names of the preset packages you added:
    ```json
    "Packages": {
        "available": [
            "Name_preset_1",
            "Name_preset_2"
	],
     }
     ```
2. Restart `StarLuxe.exe` and download your preset from the Preset section
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

Did this project help you?

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://buymeacoffee.com/dimitrimath)

**✦ Thanks for your support! ✦**

## Credits
<p>
	<b>ReShade</b> developer for developing ReShade
	<br>
	<b>SweetFX</b> developer for creating SweetFX shaders collection/set/pack
	<br>
</p>

***This project was developed by me***
