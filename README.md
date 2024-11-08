# MusicId

Main music id repository

## What is MusicId

MusicId is a service that  can identify and fill metadata of music files.
MusicId is using ShazamIO to listen to the contents of mp3 files inside 

## How to use

Preferred way of deployment is docker.
Clone this repository.
Edit the `Docker/dokcer-compose.yaml` to point to the right directory.
Run `docker compose up` from the `Docker` folder and everything should work fine.
There are two parameters: `cron` and `rate`.

 - `cron` - specifies how often should be the source directory traversed. Default value is once every 12 hours.
 - `rate` - specifies how many times per minute may the shazamio API be used. Default value is 4 (times a minute).

## FAQ

> __Q: What formats are supported?__
> 
> A: mp3

> __Q: Will it try to identify every mp3 file?__
> 
> A: No, only the files that are missing any of these properties: "Title", "Artist" or "Album".

> __Q: Will it work perfectly?__
> 
> A: No, it will try its best. But some songs might be recognized wrongfully or not at all. Also, the album might be not recognized correctly as one song can appear on many albums. __Beware: the metadata are overwritten by the values returned by ShazamIO. USE AT YOUR OWN RISK__

> __Q: I see some errors in the logs.__
> 
> A: There is nothing to worry about. Important part is the 

> __Q: If I have an issue, what should I do?__
> 
> A: Ideally, fix it and make a PR 😉

## Disclaimer

__The metadata of affected mp3 files are overwritten by the values returned by ShazamIO. USE AT YOUR OWN RISK__


## How to contribute

Fork, commit, make a PR.