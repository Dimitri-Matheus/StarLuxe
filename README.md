<h1 align="center">HSR+Script</h1>

<h3 align="center">
	<img src="https://raw.githubusercontent.com/catppuccin/catppuccin/main/assets/misc/transparent.png" height="30px" width="0px"/>
Simply visit the release section or click here to get the most recent version
	<img src="https://raw.githubusercontent.com/catppuccin/catppuccin/main/assets/misc/transparent.png" height="30px" width="0px"/>
</h3>

---

## Preview
<p align="center">
	<img src=""  alt="image_preview"/>
</p>

## How to use

Extraia o arquivo e execute `HSR+Script.exe` e após abrir clique **ENTER** para ir a próxima página. Coloque o caminho do seu jogo e depois selecione o pack de reshade desejado, após você passar por todas as etapas o aplicativo irá criar um arquivo na pasta `script -> HSR+.bat`

Execute o `HSR+.bat` e divirta-se!

---

## Features
1. Cria um script totalmente personalizado
2. Facilita o uso de reshade no **Honkai Star Rail**
3. Instala os presets de reshade
4. Serve como instalador de seu pack reshade

---

## Development

- Clone the [repository]() the application.
   - Install the required libraries with the following commands:

![terminal 1]()

> [!NOTE]
> O instalador foi desenvolvido para ter o suporte a temas personlizados e presets de reshade

<details>
<summary>🤔 Como anexar o seu pack reshade</summary>
   
   - Abra o arquivo `data`
   
   - Dentro da lista `config` modifique para informar as pasta que se encontre os seus presets

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

---

> [!WARNING]
> Fique ciente que o uso de reshade pode fazer você ser banido ainda que a probabilidade seja baixa mas use pela sua conta em risco!
> Compartilhar seu UID pode aumentar o risco de ser banido no jogo.

#

## Contributing

If you want to contribute to this project, open a new issue to discuss your idea or submit a pull request with the proposed changes.

## Credits

This project was developed by **me**
