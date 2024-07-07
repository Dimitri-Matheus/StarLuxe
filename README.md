<h1 align="center">HSR+Script</h1>

<h3 align="center">
	<img src="https://raw.githubusercontent.com/catppuccin/catppuccin/main/assets/misc/transparent.png" height="30px" width="0px"/>
The best Reshade installer for this Honkai Star Rail
	<img src="https://raw.githubusercontent.com/catppuccin/catppuccin/main/assets/misc/transparent.png" height="30px" width="0px"/>
</h3>

<p align="center">
	<img src="https://github.com/Dimitri-Matheus/HSR-Script/assets/121637762/be586150-fa5a-447b-b82a-dcd717827fd1"  alt="image"/>
</p>

## How to use

Extract the file and run `HSR+.exe` Once open, press **enter** to proceed to the next page. 
Enter your game's path and select the desired Reshade pack. 

After completing all the steps, the application will create a file in the ***script/folder***
<p align="center">
	<b>✧ Run HSR+.bat and enjoy ✧</b>
</p>


---

## Attributes
1. Facilitating Reshade integration into _Honkai Star Rail_
2. Support for custom themes and Reshade presets
3. Custom script creation

---

## Development

- Clone this [repository](https://github.com/Dimitri-Matheus/HSR-Script.git)
   - Install the required libraries with the following command

![terminal](https://github.com/Dimitri-Matheus/HSR-Script/assets/121637762/a7bec06c-6823-4183-978d-58cc3b2d119a)


<details>
<summary>How to add your Reshade pack?</summary>
   
   - Open the file `data.py`
      - Change the properties of the list to indicate the folder:

<p>

```python
config = [
    ("assets/icon", "Presets"),
    ("assets/fonts", "Presets"),
    ("assets/sound", "Presets"),
    ("css", "Presets")
]

thread = threading.Thread(target=download_from_github, args=("YOUR-GITHUB-NAME", "REPOSITORY", c[0], c[1]))

```

</details>
</p>

### Support Playnite
> Open **Playnite** and add HSR+Playnite.bat to the Path tab to open it

![image](https://github.com/Dimitri-Matheus/HSR-Script/assets/121637762/0c2e29cd-91b6-40e7-8c06-f88d9bc2711d)


```
✦ Run commands coming soon...
```

---

> [!IMPORTANT]
> Your antivirus might block the application from running. 
> This happens because the build created by PyInstaller can cause a false positive. To learn more, click [HERE](https://nitratine.net/blog/post/issues-when-using-auto-py-to-exe/#my-antivirus-detected-the-exe-as-a-virus)
> However, the application does not contain any viruses. Therefore, it is recommended to disable your antivirus before running the program.

> [!WARNING]
> The use of Reshade may result in a ban, although the likelihood is low.
> Use at your own risk! Sharing your UID may increase the risk of being banned in the game.



#

## Contributing

If you want to contribute to this project, open a new issue to discuss your idea or submit a pull request with the proposed changes

## Credits
<p>
	<b>ReShade</b> developer for developing ReShade
	<br>
	<b>SweetFX</b> developer for creating SweetFX shaders collection/set/pack
	<br>
	<b>shirooo39</b> developer for commands
	<br>
</p>

***This project was developed by me***
