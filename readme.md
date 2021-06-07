
![AnimDL Cover](https://raw.githubusercontent.com/justfoolingaround/animdl/master/assets/cover.png)

<h1><center> AnimDL - Download & Stream Your Favorite Anime </center></h1>

**AnimDL** is an incredibly powerful tool for downloading and streaming anime.

### Core features

- Abuses the developer's knowledge of internal streaming mechanisms in various different sites to hunt down high quality stream links.
- Doesn't make a single unnecessary request; the official site may make 1k requests, this tool makes 3~5.
- Doesn't use any heavy dependencies such as Selenium or Javascript Evaluators.
- Effectively bypasses DRMs in several streaming sites.
- Integrates AnimeFillerList so that the user can filter out any fillers from downloading or streaming.
- Integrates powerful, fast and efficient internal HLS downloader.
- Only tool in existence to bypass [9Anime](https://9anime.to)'s cloudflare protection.
- Operates with full efficiency and speed by using Python's generator functions to their full capacity.
- Supports streaming with [`mpv`](https://github.com/mpv-player/mpv/), an incredibly efficient, fast and light-weight dependency.

### Usage

```
animdl.py [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.       

Commands:
  continue  Continue your downloads or stream from where t'was left.
  download  Download your favorite anime by query.
  grab      Stream the stream links to the stdout stream for external usage.
  stream    Stream your favorite anime by query.
```

**Examples:**

1. Streaming **One Piece** on [**9Anime**](https://9anime.to/) from episode 1 by placing a search forehand:

-
    ```
    animdl.py stream -q "one piece" -s 1
    ```


2. Streaming **One Piece** on [**4Anime**](https://4anime.to/) from episode 1 by placing a search forehand.

-
    ```
    animdl.py stream -q "4anime:one piece" -s 1
    ```

3. Streaming **One Piece** on [**9Anime**](https://9anime.to/) with anime url from episode 1.

-
    ```
    animdl.py stream -q "https://9anime.to/watch/one-piece.ov8" -s 1
    ```

4. Streaming with the setting of **3** with **AnimeFillerList** integration that filters out fillers.

- 
    ```
    animdl.py stream -q "https://9anime.to/watch/one-piece.ov8" -s 1 -fl "https://animefillerlist.com/shows/one-piece" --fillers
    ```
    
5. Continuing a previous stream / download session without worrying about the command.

- 
    ```
    animdl.py continue
    ```

6. Scraping the episode stream links of **One Piece** from **[9Anime](https://9anime.to/)** to **stdout** without downloading:

- 
    ```
    animdl.py grab -q "https://9anime.to/watch/one-piece.ov8" -s 1
    ```

**Downloading** is the same as the examples 1-4, except the `download` command is used.

### Installation

Clone / download the repository and simply run the following command in the working directory:

```
pip install -r requirements.txt
```

**Support:** Python 3.6 and higher

### Supported Sites


| Website | Searcher Prefix | Available Qualities | Status | Content Extension |
| ------- | ---------------- | ------------------- | ------ | ----------------- |
| [4Anime](https://4anime.to/) | `4anime` | 720p, 1080p | Working | MP4 |
| [9Anime](https://9anime.to/) | `9anime `| 720p, 1080p | Working | MP4 / TS  | 
| [AnimeFreak](https://www.animefreak.tv/) | `animefreak` | 720p, 1080p | Working | MP4 | 
| [AnimePahe](https://www.animepahe.com/) | `animepahe` | 720p, 1080p | Working | TS | 
| [Animixplay](https://www.animixplay.to/) | `animix` | 480p, 720p, 1080p | Working | MP4 / TS |
| [GogoAnime](https://www1.gogoanime.ai/) | `gogoanime` | 480p, 720p, 1080p | Working | MP4 / TS |
| [Twist](https://www.twist.moe/) | `twist` | 720p, 1080p | Working| MP4 |

### More sites?

Currently, there are no plans to add more sites as **AnimDL** supports top sites that stream anime. However, this does not mean that this is it for the sites. You can raise as many issues as possible for requesting a new site.

**Note:** Your request may be denied in case of Cloudflare protections and powerful anti-bot scripts in the site.

### Streaming

Streaming needs an additional dependency known as `mpv`, you can download it from [here.](https://github.com/mpv-player/mpv/releases/)

If you're having issues with the installation of mpv, you can make an issue to recieve full help on its installation and usage.

### Disclaimer

Downloading or streaming copyrighted materials might be illegal in your country.