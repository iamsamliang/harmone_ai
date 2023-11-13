import subprocess


def extract_frames(video_path, output_dir):
    # command = f"ffmpeg -ss {timestamp} -i {input_video} -vframes 1 -y {output_image}"

    # Convert to jpg for speed at the cost of a little accuracy
    # command = f"ffmpeg -i {input_video} -r 1 -frames:v 10 frames/image_%04d.jpg"

    # this command is more accurate
    command = f"ffmpeg -i {video_path} -vf fps=1 {output_dir}/image_%04d.jpg"
    subprocess.run(command, shell=True, check=True)
