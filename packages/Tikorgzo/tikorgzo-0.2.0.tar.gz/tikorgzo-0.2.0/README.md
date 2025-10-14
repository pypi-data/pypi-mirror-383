# Tikorgzo

**Tikorgzo** is a TikTok video downloader written in Python that downloads videos in the highest available quality and saves them to your Downloads folder, organized by username. The project utilizes Playwright to obtain download links from the <b>[TikWM](https://www.tikwm.com/)</b> API. The project supports both Windows and Linux distributions.

Some of the key features include:

- Download TikTok video from command-line just by supplying the ID or video link.
- Supports multiple links to be downloaded.
- Set max number of simultaneous downloads.
- Supports link extraction from a text file.
- Customize the filename of downloaded videos.
- Extracts downloads link asynchronously for faster link extraction.

## Installation

### Requirements
- Windows, or any Linux distros
- Python `v3.10` or greater
- uv

### Steps
1. Install Python 3.10.0 or above. For Windows users, ensure `Add Python x.x to PATH` is checked.
2. Open your command-line.
3. Install uv through `pip` command or via [Standalone installer](https://docs.astral.sh/uv/getting-started/installation/#standalone-installer).

    ```console
    pip install uv
    ```

4. Install the latest published stable release into your system.

    ```
    uv tool install tikorgzo
    ```

    Or if you want to get the latest features without having to wait for official release, choose this one instead:

    ```console
    uv tool install git+https://github.com/Scoofszlo/Tikorgzo
    ```

5. For Windows users, if `warning: C:\Users\$USERNAME\.local\bin is not on your PATH...` appears, add the specified directory to your [user or system PATH](https://www.architectryan.com/2018/03/17/add-to-the-path-on-windows-10/), then reopen your command-line.

6. Install the Playwright browser. This is needed to allow download link extraction from the API.

    ```console
    uvx playwright install
    ```

7. For Linux users, Playwright might display a message containing `sudo playwright install-deps`. Follow the instructions, but replace the command with:

    ```console
    uvx playwright install-deps
    ```

8. To download a TikTok video, run the following command (replace the number with your actual video ID or link):
  
    ```console
    tikorgzo -l 7123456789109876543
    ```

9. Wait for the program to do it's thing. The downloaded video should appear in your Downloads folder.

## Usage

### Downloading a video

To download a TikTok video, simply put the video ID, or the video link:

```console
tikorgzo -l 7123456789109876543
```

### Downloading multiple videos

The program supports multiple video links to download. Simply separate those links by spaces:

```console
tikorgzo -l 7123456789109876543 7023456789109876544 "https://www.tiktok.com/@username/video/7123456789109876540"
```
It is recommended to enclose video links with double quotation marks to handle special characters properly.

### Downloading multiple links from a `.txt` file

Alternatively, you can also use a `.txt` file containing multiple video links and use it to download those. Ensure that each link are separated by newline.

To do this, just simply put the path to the `.txt` file.

```console
tikorgzo -f "C:\path\to\txt.file"
```

### Customizing the filename of the downloaded video

By default, downloaded videos are saved with their video ID as the filename (e.g., `1234567898765432100.mp4`). If you want to change how your files are named, you can use the `--filename-template` arg.

You can use the following placeholders in your template:

- **`{video_id}`** (required): The unique ID of the video.
- **`{username}`**: The TikTok username who posted the video.
- **`{date}`**: The upload date in UTC, formatted as `YYYYMMDD_HHMMSS` (for example: `20241230_235901`); or
- **`{date:<date_fmt>}`**: An alternative to `{date}` where you can customized the date in your preferred format. Working formats for `<date_fmt>` are available here: https://strftime.org/.

#### Examples

- Save as just the video ID (you don't really need to do this as this is the default naming):
    ```console
    tikorgzo -l 1234567898765432100 --filename-template "{video_id}"
    # Result: 1234567898765432100.mp4
    ```

- Save as username and video ID:
    ```console
    tikorgzo -l 1234567898765432100 --filename-template "{username}-{video_id}"
    # Result: myusername-1234567898765432100.mp4
    ```

- Save as username, date, and video ID:
    ```console
    tikorgzo -l 1234567898765432100 --filename-template "{username}-{date}-{video_id}"
    # Result: myusername-20241230_235901-1234567898765432100.mp4
    ```

- Save with a custom date format (e.g., `YYMMDD_HHMMSS`):
    ```console
    tikorgzo -l 1234567898765432100 --filename-template "{username}-{date:%y%m%d_%H%M%S}-{video_id}"
    # Result: myusername-241230_235901-1234567898765432100.mp4
    ```


### Setting the maximum number of simultaneous downloads

When downloading many videos, the program limits downloads to 4 at a time by default.

To change the maximum number of simultaneous downloads, use the `--max-concurrent-downloads <value>` arg, where `<value>` must be in range of 1 to 16:

```console
tikorgzo -f "C:\path\to\100_video_files.txt" --max-concurrent-downloads 10
```

### Using lazy duplicate checking

The program checks if the video you are attempting to download has already been downloaded. By default, duplicate checking is based on the 19-digit video ID in the filename. This means that even if the filenames are different, as long as both contain the same video ID, the program will detect them as duplicates.

For example, if you previously downloaded `250101-username-1234567898765432100.mp4` and now attempt to download `username-1234567898765432100.mp4`, the program will detect it as a duplicate since both filenames contain the same video ID.

If you want to change this behavior so that duplicate checking is based on filename similarity instead, use the `--lazy-duplicate-check` option.

### Upgrading and uninstalling the app

To upgrade the app, just run `uv tool upgrade tikorgzo` and wait for uv to fetch updates from the source.

To uninstall the app, just run `uv tool uninstall tikorgzo` to remove the app. Take note that this doesn't remove the Tikorgzo folder generated in your Downloads directory.

## Reminders
- Source/high-quality videos may not always be available, depending on the source. If not available, the downloaded videos are usually 1080p or 720p.
- The program may be a bit slow during download link extraction (Stage 2), as it runs a browser in the background to extract the actual download link.
- For this reason, the program is much more aligned to those who want to download multiple videos at once. However, you can still use it to download any number of videos you want.
- The program has been thoroughly tested on Windows 11 and is expected to work reliably on Windows systems. For Linux, testing was performed using Ubuntu through WSL so it should generally work fine on most Linux distributions, but compatibility is not guaranteed.

## License

Tikorgzo is an open-source program licensed under the [MIT](LICENSE) license.

If you can, please contribute to this project by suggesting a feature, reporting issues, or make code contributions!

## Legal Disclaimer

The use of this software to download content without the permission may violate copyright laws or TikTok's terms of service. The author of this project is not responsible for any misuse or legal consequences arising from the use of this software. Use it at your own risk and ensure compliance with applicable laws and regulations.

This project is not affiliated, endorsed, or sponsored by TikTok or its affiliates. Use this software at your own risk.

## Acknowledgements

Special thanks to <b>[TikWM](https://www.tikwm.com/)</b> for providing free API service, which serves as a way for this program to extract high quality TikTok videos.

## Contact

For questions or concerns, feel free to contact me via the following!:
- [Gmail](mailto:scoofszlo@gmail.com) - scoofszlo@gmail.com
- Discord - @scoofszlo
- [Reddit](https://www.reddit.com/user/Scoofszlo/) - u/Scoofszlo
- [Twitter](https://twitter.com/Scoofszlo) - @Scoofszlo
