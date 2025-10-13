import os
import argparse
import tempfile
from pathlib import Path
import cv2
import soundfile as sf
from avst.io import (
    extract_audio,
    load_audio,
    get_video_fps,
    get_video_length_sec,
    get_video_frame_size,
    pad_audio,
    mux_audio_video,
    save_synced_video,
)
from avst.sync_algorithm import compute_audio_sync_offset


def validate_videos_for_stacking(video1_path, video2_path):
    """
    Validate that two videos have the same resolution, FPS, and length.
    Raises ValueError if they don't match.
    """
    # Get video1 properties
    w1, h1 = get_video_frame_size(video1_path)
    fps1 = get_video_fps(video1_path)
    length1 = get_video_length_sec(video1_path)
    
    # Get video2 properties
    w2, h2 = get_video_frame_size(video2_path)
    fps2 = get_video_fps(video2_path)
    length2 = get_video_length_sec(video2_path)
    
    errors = []
    
    # Check resolution
    if (w1, h1) != (w2, h2):
        errors.append(f"Resolution mismatch: Video1 is {w1}x{h1}, Video2 is {w2}x{h2}")
    
    # Check FPS (allow small tolerance for floating point comparison)
    if abs(fps1 - fps2) > 0.1:
        errors.append(f"FPS mismatch: Video1 is {fps1:.1f} FPS, Video2 is {fps2:.1f} FPS")
    
    ## Check length (allow 1 second tolerance)
    #if abs(length1 - length2) > 1.0:
    #    errors.append(f"Length mismatch: Video1 is {length1:.2f}s, Video2 is {length2:.2f}s")
    
    if errors:
        error_msg = "Cannot stack videos due to the following mismatches:\n" + "\n".join(f"  - {e}" for e in errors)
        raise ValueError(error_msg)
    
    print(f"[Validation passed] Videos are compatible for stacking")
    return True


def sync_to_reference(video1_path, video2_path, output2_path, synced_session_path, target_fps=60, target_sr=48000, stack_audio_source=1, visualize: bool = False):
    """
    Sync video2 to video1 (reference). Video1 remains untouched.
    Only video2 is modified (padded or cut) to match video1's timing.
    Also creates a stacked session video.
    
    Args:
        stack_audio_source: Which audio to use in stacked video (1 for video1, 2 for video2). Default is 1.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        audio1_path = Path(tmpdir) / 'audio1.wav'
        audio2_path = Path(tmpdir) / 'audio2.wav'

        # Extract audio from videos
        extract_audio(video1_path, audio1_path, target_sr)
        extract_audio(video2_path, audio2_path, target_sr)

        audio1, sr1 = load_audio(audio1_path)
        audio2, sr2 = load_audio(audio2_path)
        assert sr1 == sr2, "Sampling rates must match"
        sr = sr1

        lag, ms_offset = compute_audio_sync_offset(audio1, audio2, sr)
        
        # Calculate delay in seconds and frames
        delay_seconds = lag / sr
        delay_frames = int(round(abs(delay_seconds) * target_fps))
        
        # Print sync analysis
        print(f"\n[Sync Analysis]")
        print(f"  Video2 offset: {ms_offset:.2f} ms ({delay_seconds:.3f}s, {delay_frames} frames @ {target_fps}fps)")
        
        if lag > 0:
            print(f"  Video2 starts LATER → Padding Video2 start with {delay_frames} black frames\n")
            pad_video2_start = delay_frames
            pad_video2_end = 0
        elif lag < 0:
            print(f"  Video2 starts EARLIER → Cutting first {delay_frames} frames from Video2\n")
            pad_video2_start = 0
            pad_video2_end = 0
            # We'll handle cutting by skipping frames during save
        else:
            print(f"  Videos are already in sync!\n")
            pad_video2_start = 0
            pad_video2_end = 0

        # Get video1 length to match
        cap1 = cv2.VideoCapture(video1_path)
        n_frames1 = int(cap1.get(cv2.CAP_PROP_FRAME_COUNT))
        cap1.release()
        
        # Save video2 with adjustments (no audio)
        tmp_video2_path = Path(tmpdir) / 'tmp_video2.mp4'
        
        if lag < 0:
            # Cut frames from the beginning
            save_synced_video(video2_path, tmp_video2_path, 0, 0, target_fps, skip_start_frames=delay_frames)
        else:
            # Pad frames at the beginning
            save_synced_video(video2_path, tmp_video2_path, pad_video2_start, pad_video2_end, target_fps)

        # Adjust audio2 accordingly
        if lag > 0:
            padded_audio2 = pad_audio(audio2, pad_video2_start, 0, target_fps, sr)
        elif lag < 0:
            # Cut audio from the beginning
            cut_samples = int(abs(delay_seconds) * sr)
            padded_audio2 = audio2[cut_samples:]
        else:
            padded_audio2 = audio2

        padded_audio2_path = Path(tmpdir) / 'padded_audio2.wav'
        sf.write(padded_audio2_path, padded_audio2, sr)

        # Mux audio and video for synced video2
        mux_audio_video(tmp_video2_path, padded_audio2_path, output2_path)

        print(f"[Synced video2] saved to {output2_path}")
        print(f"[Synced video2] length: {get_video_length_sec(output2_path):.2f} seconds, {get_video_fps(output2_path):.1f} FPS")
        
        if visualize:
            # Validate videos before stacking
            print(f"\n[Validating videos for stacking]")
            try:
                validate_videos_for_stacking(video1_path, output2_path)
            except ValueError as e:
                print(f"\n[ERROR] {e}")
                print(f"\n[Synced video2] saved to {output2_path}")
                print(f"[Synced video2] length: {get_video_length_sec(output2_path):.2f} seconds, {get_video_fps(output2_path):.1f} FPS")
                print(f"\n[Skipping stacked session video creation due to validation errors]")
                return
            
            # Create stacked session video with video1 (original) and synced video2
            audio_map = "0:a" if stack_audio_source == 1 else "1:a"
            audio_source_name = "Video1" if stack_audio_source == 1 else "Video2"
            
            cmd_stack = (
                f'ffmpeg -hide_banner -loglevel error -y -i "{video1_path}" -i "{output2_path}" '
                f'-filter_complex "[0:v][1:v]vstack=inputs=2[v]" -map "[v]" -map {audio_map} '
                f'-c:v libx264 -pix_fmt yuv420p -c:a aac -b:a 192k "{synced_session_path}"'
            )
            print(f"[Stacking videos]: {Path(synced_session_path).name} (using {audio_source_name} audio)")
            os.system(cmd_stack)

            print(f"[Synced session] saved to {synced_session_path}")
            print(f"[Synced session] length: {get_video_length_sec(synced_session_path):.2f} seconds, {get_video_fps(synced_session_path):.1f} FPS")

        return ms_offset


def sync_videos(video1_path, video2_path, output1_path, output2_path, synced_session_path, target_fps=60, target_sr=48000, visualize: bool = False):
    with tempfile.TemporaryDirectory() as tmpdir:
        audio1_path = Path(tmpdir) / 'audio1.wav'
        audio2_path = Path(tmpdir) / 'audio2.wav'

        # Extract audio from videos
        extract_audio(video1_path, audio1_path, target_sr)
        extract_audio(video2_path, audio2_path, target_sr)

        audio1, sr1 = load_audio(audio1_path)
        audio2, sr2 = load_audio(audio2_path)
        assert sr1 == sr2, "Sampling rates must match"
        sr = sr1

        lag, ms_offset = compute_audio_sync_offset(audio1, audio2, sr)

        delay_seconds = lag / sr
        delay_frames = int(round(abs(delay_seconds) * target_fps))

        # Print sync analysis
        print(f"\n[Sync Analysis]")
        print(f"  Video2 offset: {ms_offset:.2f} ms ({delay_seconds:.3f}s, {delay_frames} frames @ {target_fps}fps)")

        pad_video1_start = 0
        pad_video2_start = 0

        if lag > 0:
            print(f"  Video2 starts LATER → Padding Video2 start with {delay_frames} black frames")
            pad_video2_start = int(round((lag / sr) * target_fps))
        elif lag < 0:
            print(f"  Video2 starts EARLIER → Padding Video1 start with {delay_frames} black frames")
            pad_video1_start = int(round((-lag / sr) * target_fps))
        else:
            print(f"  Videos are already in sync!")
        print()

        cap1 = cv2.VideoCapture(video1_path)
        cap2 = cv2.VideoCapture(video2_path)
        n_frames1 = int(cap1.get(cv2.CAP_PROP_FRAME_COUNT)) + pad_video1_start
        n_frames2 = int(cap2.get(cv2.CAP_PROP_FRAME_COUNT)) + pad_video2_start
        max_frames = max(n_frames1, n_frames2)
        cap1.release()
        cap2.release()

        pad_video1_end = max_frames - n_frames1
        pad_video2_end = max_frames - n_frames2

        # Save videos with black frame padding (no audio)
        tmp_video1_path = Path(tmpdir) / 'tmp_video1.mp4'
        tmp_video2_path = Path(tmpdir) / 'tmp_video2.mp4'
        save_synced_video(video1_path, tmp_video1_path, pad_video1_start, pad_video1_end, target_fps)
        save_synced_video(video2_path, tmp_video2_path, pad_video2_start, pad_video2_end, target_fps)

        # Pad audios accordingly
        padded_audio1 = pad_audio(audio1, pad_video1_start, pad_video1_end, target_fps, sr)
        padded_audio2 = pad_audio(audio2, pad_video2_start, pad_video2_end, target_fps, sr)

        padded_audio1_path = Path(tmpdir) / 'padded_audio1.wav'
        padded_audio2_path = Path(tmpdir) / 'padded_audio2.wav'
        sf.write(padded_audio1_path, padded_audio1, sr)
        sf.write(padded_audio2_path, padded_audio2, sr)

        # Mux padded audio and video for each synced video
        mux_audio_video(tmp_video1_path, padded_audio1_path, output1_path)
        mux_audio_video(tmp_video2_path, padded_audio2_path, output2_path)

        print(f"[Synced video1] length: {get_video_length_sec(output1_path):.2f} seconds, {get_video_fps(output1_path):.1f} FPS")
        print(f"[Synced video2] length: {get_video_length_sec(output2_path):.2f} seconds, {get_video_fps(output2_path):.1f} FPS")
        
        if visualize:
            # Create stacked session video with audio1 original (unpadded) audio for sync session video
            cmd_stack = (
                f'ffmpeg -hide_banner -loglevel error -y -i "{output1_path}" -i "{output2_path}" -i "{padded_audio2_path}" '
                f'-filter_complex "[0:v][1:v]vstack=inputs=2[v]" -map "[v]" -map 2:a '
                f'-c:v libx264 -pix_fmt yuv420p -c:a aac -b:a 192k "{synced_session_path}"'
            )
            print(f"[Stacking videos]: {Path(synced_session_path).name}")
            os.system(cmd_stack)
            print(f"[Synced session] length: {get_video_length_sec(synced_session_path):.2f} seconds, {get_video_fps(synced_session_path):.1f} FPS")

        return ms_offset


def main():
    parser = argparse.ArgumentParser(description='Sync two videos based on audio.')
    parser.add_argument('--video1_path', type=str, required=True, help='Path to the first video file (reference)')
    parser.add_argument('--video2_path', type=str, required=True, help='Path to the second video file')
    parser.add_argument('--output_video1_path', type=str, default='synced_video1.mp4', help='Path to the first synced video file')
    parser.add_argument('--output_video2_path', type=str, default='synced_video2.mp4', help='Path to the second synced video file')
    parser.add_argument('--output_session_path', type=str, default='synced_session.mp4', help='Path to the synced session video file')
    parser.add_argument('--fps', type=int, default=60, help='Target FPS for the videos')
    parser.add_argument('--sr', type=int, default=48000, help='Target sampling rate for the audio')
    parser.add_argument('--reference', action='store_true', help='Sync only video2 to video1 (reference). Video1 remains untouched, only video2 is saved.')
    args = parser.parse_args()

    for video_file in [args.video1_path, args.video2_path]:
        if not Path(video_file).exists():
            raise FileNotFoundError(f"Video file {video_file} does not exist")

    if args.reference:
        print(f"[Reference Mode] Video1 is the reference, syncing Video2 to it...\n")
        sync_to_reference(
            args.video1_path,
            args.video2_path,
            args.output_video2_path,
            args.output_session_path,
            args.fps,
            args.sr
        )
    else:
        sync_videos(
            args.video1_path, 
            args.video2_path, 
            args.output_video1_path, 
            args.output_video2_path, 
            args.output_session_path, 
            args.fps, 
            args.sr
        )


if __name__ == "__main__":
    main()
