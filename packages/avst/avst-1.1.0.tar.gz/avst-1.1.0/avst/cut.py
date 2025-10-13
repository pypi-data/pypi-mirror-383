import argparse
from pathlib import Path
import subprocess
from avst.io import get_video_length_sec


def cut_video(input_path, output_path, start_time=None, end_time=None, target_fps=60):
    """
    Cut a video between start_time and end_time (in seconds).
    If start_time is None, starts from the beginning.
    If end_time is None, goes to the end of the video.
    """
    print(f'[Cutting video] {Path(input_path).name} from {start_time}s to {end_time}s')
    
    # Build the ffmpeg command
    cmd = [
        'ffmpeg',
        '-hide_banner',
        '-loglevel', 'error',
        '-y',  # Overwrite output file if it exists
        '-i', str(input_path)
    ]
    
    # Add start time if specified
    if start_time is not None:
        cmd.extend(['-ss', str(start_time)])
    
    # Add end time if specified
    if end_time is not None:
        if start_time is not None and end_time <= start_time:
            raise ValueError("end_time must be greater than start_time")
        cmd.extend(['-to', str(end_time)])
    
    # Add output options
    cmd.extend([
        '-c:v', 'libx264',
        '-preset', 'fast',
        '-crf', '18',  # Good quality setting
        '-pix_fmt', 'yuv420p',
        '-movflags', '+faststart',  # For better web streaming
        '-r', str(target_fps),  # Set output FPS
        '-c:a', 'aac',
        '-b:a', '192k',  # Audio bitrate
        '-shortest',  # Finish encoding when the shortest input stream ends
        str(output_path)
    ])
    
    # Run the command
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error cutting video: {e}")
        raise


def main():
    """Entry point for avst-cut command."""
    parser = argparse.ArgumentParser(description='Cut a video between specified times.')
    parser.add_argument('--input', type=str, required=True, help='Path to the input video file')
    parser.add_argument('--output', type=str, default='cut_video.mp4', help='Path to save the cut video')
    parser.add_argument('--start', type=float, help='Start time in seconds (omit to start from beginning)')
    parser.add_argument('--end', type=float, help='End time in seconds (omit to cut to end)')
    parser.add_argument('--fps', type=int, default=60, help='Target FPS for the output video')
    args = parser.parse_args()

    if not Path(args.input).exists():
        raise FileNotFoundError(f"Input video {args.input} does not exist")

    cut_video(
        input_path=args.input,
        output_path=args.output,
        start_time=args.start,
        end_time=args.end,
        target_fps=args.fps
    )
    
    print(f"[Cut video] saved to {args.output}")
    print(f"[Duration] {get_video_length_sec(args.output):.2f} seconds")


if __name__ == "__main__":
    main()
