import subprocess
import pytube


# download video and audio, and extract video information
def dl_video_audio(url, filename):
    try:
        ### Download the video
        # download_command = f'yt-dlp -o "{filename}.%(ext)s" {url}'

        ### download the video and audio separately
        download_command = f'yt-dlp -f bestaudio -o "{filename}_audio.%(ext)s" {url} && yt-dlp -f bestvideo -o "{filename}.%(ext)s" {url}'
        subprocess.run(download_command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to download video: {e}")
        return None


def extract_vid_info(url):
    # extract video information
    yt = pytube.YouTube(url)

    # Getting the video title
    video_title = yt.title

    # Getting the video author/channel
    video_author = yt.author

    # Getting the video length in seconds
    video_length = yt.length

    # Getting the video description
    video_description = yt.description

    return {
        "title": video_title,
        "author": video_author,
        "length": video_length,
        "desc": video_description,
        "url": url,
    }
