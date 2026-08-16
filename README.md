# LowDing
### A simple pygame game about loading screens! 
<img width="896" height="645" alt="image" src="https://github.com/user-attachments/assets/7c4ed13a-d17d-47b8-9ad3-2d7ba4db2e69" />

## Idea
#### The main idea here is you want to make loops! The Loading ring gives you missions to do -inside or outside the game- to earn percentage to be loaded

## Features
- 7 unique levels!
- It's easy to add new levels!
- Real-time SFX!

## Run & Install
(you can skip this part and get the game from [here](https://github.com/timodev96-alt/LowDing/releases/tag/Main)!)
### 1.Clone the repo
```
git clone https://github.com/timodev96-alt/LowDing.git
cd LowDing
```
### 2.Build the game
(or you just can run `python main.py` to run from source code)
#### Now Run this which pack everything in one `.exe` file
```
pyinstaller --onefile --noconsole --add-data "photos;photos" --add-data "bg.mp3;." --name "LowDing" main.py
```
#### Your game will be in `/dist` Folder!
