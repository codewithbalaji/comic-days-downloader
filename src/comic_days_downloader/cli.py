import argparse
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

from comic_days_downloader import __version__
from comic_days_downloader.image import descramble_page
from comic_days_downloader.scraper import fetch_episode_pages


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="comic-days-downloader",
        description=(
            "Download the freely readable pages of a comic-days.com manga episode."
        ),
    )

    parser.add_argument(
        "url",
        nargs="?",
        help="URL of a public comic-days.com episode "
             "(e.g. https://comic-days.com/episode/1393201648003094410). "
             "If omitted, you'll be prompted for it.",
    )

    parser.add_argument(
        "-o", "--output-dir",
        help="Directory to save pages into (default: a timestamped folder "
             "in the current directory).",
    )

    parser.add_argument(
        "-w", "--workers",
        type=int,
        default=8,
        help="Maximum number of pages to download/process in parallel (default: 8).",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    return parser.parse_args(argv)


def main(argv=None) -> None:
    args = parse_args(argv)

    url = args.url or input(
        "Please, insert a manga link with public viewing of comic-days website:\n> "
    ).strip()

    if not url:
        print("No URL provided.")
        return

    print("\nLoading Comic Days page...")

    pages_dict = fetch_episode_pages(url)

    files_dir = args.output_dir or os.path.join(
        os.getcwd(),
        datetime.now().strftime("%Y-%m-%d-%H-%M-%S"),
    )

    os.makedirs(files_dir, exist_ok=True)

    print()
    print("=" * 60)
    print(f"Pages found : {len(pages_dict)}")
    print(f"Output      : {files_dir}")
    print("=" * 60)
    print()

    max_workers = min(args.workers, len(pages_dict))

    if max_workers == 0:
        print("No pages found.")
        return

    failed_pages = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:

        futures = {
            executor.submit(descramble_page, page_number, image_data, files_dir): page_number
            for page_number, image_data in pages_dict.items()
        }

        for future in as_completed(futures):
            page_number = futures[future]

            try:
                future.result()
            except Exception as error:
                failed_pages.append(page_number)
                print(f"ERROR: Page {page_number:02d} failed: {error}")

    print()
    print("=" * 60)

    if failed_pages:
        failed_pages.sort()
        print("Completed with errors.")
        print(f"Failed pages: {', '.join(map(str, failed_pages))}")
    else:
        print("All pages processed successfully!")

    print(f"Saved to: {files_dir}")
    print("=" * 60)


if __name__ == "__main__":
    main()
