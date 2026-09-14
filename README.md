# Comic-Days Downloader

Download the freely readable pages of a [comic-days.com](https://comic-days.com) manga episode as
PNG images, in one command.

## How it works

comic-days.com serves the "free to read" pages of an episode as scrambled image tiles, reassembled
client-side in the browser. This tool:

1. Loads the episode page and reads the embedded page-structure JSON.
2. Downloads each page's scrambled image.
3. Rearranges the tiles back into the correct order (reproducing the same tile layout the site's
   own viewer draws).
4. Saves each page as a numbered PNG into an output folder.

Only pages available in the site's free/public viewer can be downloaded — this does not bypass any
paywall or subscription gating.

## Requirements

- Python 3.9+
- pip

## Install

Clone the repo and install it as a package:

```bash
git clone https://github.com/codewithbalaji/comic-days-downloader.git
cd comic-days-downloader
pip install .
```

This installs a `comic-days-downloader` command. Alternatively, to run it from source without
installing the package:

```bash
pip install -r requirements.txt
python -m comic_days_downloader <url>
```

## Usage

```bash
comic-days-downloader https://comic-days.com/episode/316190247012627365
```

If you omit the URL, you'll be prompted for it interactively.

Free episodes on comic-days.com rotate/expire on a schedule, so an example URL here may 404 later —
grab a current "free to read" episode link from the site itself.

Options:

| Flag | Description | Default |
|---|---|---|
| `-o`, `--output-dir` | Directory to save pages into | a timestamped folder in the current directory |
| `-w`, `--workers` | Max pages to download/process in parallel | `8` |
| `--version` | Print the installed version | — |

Example with options:

```bash
comic-days-downloader https://comic-days.com/episode/316190247012627365 -o ./output -w 4
```

## Output

Pages are saved as `1.png`, `2.png`, `3.png`, ... in the output folder, in reading order.

## Contributing

Issues and pull requests are welcome. If comic-days.com changes its page format and downloads start
failing, please open an issue with the episode URL (if it's public) and any error output.

## License

[MIT](LICENSE)
