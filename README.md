# DDS-club-BS

**This code is now deprecated and also not clean at all: huge disclaimer!**

In order to improve our club in the mobile game BrawlStar, with [Mathieu](https://github.com/mathieugrasland) we created a front end to keep a track of our game. This gave us many informations :

- weakness and strenght of every player with every brawlers
- best teamworks
- best composition of brawler per map
- challenge other player to do their best
- and so on

## Data

Data available in BrawlStars API, using of GCP to pull informations of every player. This repo just get back all data from GCP every 3 days and preprocess it to create the final csv file used by the front.

## Front 

Developped in Dash in one night, this is pretty ugly but it worked for us. The app was heberged by https://www.pythonanywhere.com/. The actual adress is: http://ddsclub.pythonanywhere.com/ (down every 3 months).

Pulling info done also by pythonanywhere with a scheduled job.

## Thanks

Thanks to [Mathieu](https://github.com/mathieugrasland) for his work with the game API.

Also thanks to [Ulysse](https://github.com/odysseu) who helped us in the quick conception.

Finally thanks to brawlstar, we had fun playing and thinking of this little project.
