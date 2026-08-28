# Public IPTV Channels

A single merged IPTV playlist that aggregates channels from multiple public playlist sources into one file, refreshed automatically every 30 minutes.

## How to use

Load this URL in any IPTV player (Kodi, TiviMate, VLC, etc.):

```
https://raw.githubusercontent.com/azamstv00-cpu/Public_Iptv_Channels/main/playlist.m3u8
```

The file is regenerated every 30 minutes by GitHub Actions, so it always reflects the latest state of the source playlists.

## How it works

- Every 30 minutes, a GitHub Actions workflow downloads each source playlist in `sources.txt`.
- Channels are **deduplicated by URL** — the same channel appearing in multiple sources is kept only once.
- Channels are **grouped by source** using the `group-title` attribute, so you always know which source a channel came from.
- The merged result is written to `playlist.m3u8` and committed only when it actually changes.

Your own channels can be added via `personal.m3u8`, which is merged first and grouped as `Personal-Collection`.

## Source playlists and credits

All playlist credit belongs to the original creators. This repository only aggregates and merges their public playlists and claims no ownership of any of them.

| Playlist | GitHub Repo | Owner / Creator | Telegram |
|---|---|---|---|
| Tapmad (1) | [srhady/tapmad-bd](https://github.com/srhady/tapmad-bd) | Md Sohanur Rahman Hady | [@livesportsplay](https://t.me/livesportsplay) |
| Fancode (1) | [srhady/Fancode-bd](https://github.com/srhady/Fancode-bd) | Md Sohanur Rahman Hady | [@livesportsplay](https://t.me/livesportsplay) |
| Sony Liv | [srhady/SonyLiv](https://github.com/srhady/SonyLiv) | Md Sohanur Rahman Hady | [@livesportsplay](https://t.me/livesportsplay) |
| Sony Liv (2) | [sm-monirulislam/SonyLiv_Event_Playlist](https://github.com/sm-monirulislam/SonyLiv_Event_Playlist) | Monirul Islam | [@monirul_Islam_SM](https://t.me/monirul_Islam_SM) |
| Tapmad (2) | [sm-monirulislam/Tapmad_Auto_Update_Playlist](https://github.com/sm-monirulislam/Tapmad_Auto_Update_Playlist) | Monirul Islam | [@monirul_Islam_SM](https://t.me/monirul_Islam_SM) |
| Willow Events | [srhady/willow-event](https://github.com/srhady/willow-event) | Md Sohanur Rahman Hady | [@livesportsplay](https://t.me/livesportsplay) |
| Prime Video | [srhady/willow-event](https://github.com/srhady/willow-event) | Md Sohanur Rahman Hady | [@livesportsplay](https://t.me/livesportsplay) |
| HimelOp | [sn4-edge.pages.dev](https://sn4-edge.pages.dev/playlist.m3u8) | HimelOp | - |

### Playlist credits

- **Sony Liv (2), Tapmad (2)** — credit: **Monirul Islam** ([GitHub](https://github.com/sm-monirulislam) · [Telegram](https://t.me/monirul_Islam_SM))
- **Tapmad (1), Fancode (1), Sony Liv, Willow Events, Prime Video** — credit: **Md Sohanur Rahman Hady** ([GitHub](https://github.com/srhady) · [Telegram](https://t.me/livesportsplay))
- **HimelOp** — credit: **HimelOp** ([sn4-edge.pages.dev](https://sn4-edge.pages.dev))

## Attribution and copyright

- All IPTV channels and streams belong to their respective rights holders.
- This repository **does not host, produce, or own** any stream content.
- It simply aggregates and merges the **public playlists listed above**.
- Full credit for each playlist goes to its original creator, as named in the table.
- If you are a source creator and want your playlist removed from this repository, please open an issue or contact the repository maintainer and it will be removed.

## License

No license. All rights to the source playlists belong to their respective creators, credited above. This repository holds no copyright over any playlist, channel, or stream content.
