import os
import time
import base64
import uuid
import subprocess
import replicate
import requests
from runwayml import RunwayML
from dotenv import load_dotenv
from database.models import db
from database.video_cache import VideoCache

# Load environment variables
load_dotenv()

# Configure Runway
client = RunwayML()


def generate_first_frame(first_frame_prompt):
    """
    Generate the first frame image using Replicate.

    Args:
        first_frame_prompt: The prompt to generate the image

    Returns:
        URL to the generated image
    """

    try:
        # Generate image using Replicate's Flux model
        output = replicate.run(
            "black-forest-labs/flux-1.1-pro",  # try flux-1.1-pro
            input={
                "prompt": first_frame_prompt,
                "prompt_upsampling": True,
                "output_format": "webp",
            },
        )

        # Save the generated image to a temporary file
        static_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "static", "images"
        )
        os.makedirs(static_dir, exist_ok=True)

        image_filename = f"{uuid.uuid4()}.webp"
        image_path = os.path.join(static_dir, image_filename)

        # Replicate returns an iterator, save the first item
        # Add for loop for flux-schnell, not for flux-1.1-pro
        with open(image_path, "wb") as file:
            file.write(output.read())

        print("First frame generated")

        # Return the URL to the image
        return f"/static/images/{image_filename}"

    except Exception as e:
        print(f"Error generating first frame: {e}")
        # Return placeholder if generation fails
        return "/static/images/placeholder.jpg"


def image_to_data_uri(image_path):
    """
    Convert an image file to a data URI.

    Args:
        image_path: Path to the image file

    Returns:
        Data URI string
    """
    with open(image_path, "rb") as img_file:
        base64_data = base64.b64encode(img_file.read()).decode("utf-8")
    return f"data:image/webp;base64,{base64_data}"


def generate_video(first_frame_url, video_prompt):
    """
    Generate a video using Runway.

    Args:
        first_frame_url: URL to the first frame image
        video_prompt: The prompt to generate the video

    Returns:
        URL to the generated video
    """

    try:
        # Check if we already have a video with this prompt
        cached_video = VideoCache.get_video_by_prompt(video_prompt)
        if cached_video:
            print(f"Using cached video for prompt: {video_prompt[:50]}...")
            return cached_video.url_path

        # Get the absolute path to the first frame image
        image_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), first_frame_url.lstrip("/")
        )

        # Convert the image to a data URI
        image_data_uri = image_to_data_uri(image_path)

        print("Generating video...")

        # Generate video using Runway
        task = client.image_to_video.create(
            model="gen3a_turbo",
            prompt_image=image_data_uri,
            prompt_text=video_prompt,
            duration=5,  # 5 seconds for each clip
        )

        # Wait for the video generation to complete
        while True:
            output = client.tasks.retrieve(id=task.id)
            if output.status in {"SUCCEEDED", "FAILED", "CANCELLED", "THROTTLED"}:
                break
            time.sleep(0.5)
            print(".", end="", flush=True)

        print("\nVideo generated")

        if output.status == "SUCCEEDED":
            # Save the video to a local file
            video_dir = VideoCache.get_static_video_dir()
            video_filename = VideoCache.generate_unique_filename()
            video_path = os.path.join(video_dir, video_filename)

            # Format handling for the output URL
            output_url = output.output
            if isinstance(output_url, list):
                output_url = output_url[0] if output_url else None

            if not output_url:
                print("No valid URL returned from Runway API")
                return "/static/videos/placeholder.mp4"

            # Download and save the video
            try:
                response = requests.get(output_url, stream=True)
                with open(video_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"Video saved to {video_path}")

                # Delete the first frame image after successful video generation
                try:
                    if os.path.exists(image_path):
                        os.remove(image_path)
                        print(f"Deleted first frame image: {image_path}")
                except Exception as del_err:
                    print(f"Error deleting first frame image {image_path}: {del_err}")

                # Register the video in our cache
                video_obj = VideoCache.save_video(
                    f"/static/videos/{video_filename}",
                    is_combined=False,
                    original_prompt=video_prompt,
                )

                return video_obj.url_path
            except Exception as download_error:
                print(f"Error downloading video: {download_error}")
                return "/static/videos/placeholder.mp4"
        else:
            print(f"Video generation failed: {output}")
            return "/static/videos/placeholder.mp4"

    except Exception as e:
        print(f"Error generating video: {e}")
        return "/static/videos/placeholder.mp4"


def generate_scene_videos(scene_prompts):
    """
    Generate videos for each scene and return their URLs.

    Args:
        scene_prompts: Scene prompts from the Producer Agent

    Returns:
        List of video URLs
    """
    video_urls = []

    for scene in scene_prompts["scenes"]:
        # Generate the first frame
        first_frame_url = generate_first_frame(scene["first_frame_prompt"])

        # Generate the video
        video_url = generate_video(first_frame_url, scene["video_prompt"])

        video_urls.append({"scene_id": scene["scene_id"], "video_url": video_url})

    return video_urls


def concatenate_videos(video_urls):
    """
    Concatenate multiple videos into a single video file.

    Args:
        video_urls: List of dictionaries containing scene_id and video_url

    Returns:
        URL to the concatenated video
    """
    if not video_urls:
        return "/static/videos/placeholder.mp4"

    # If there's only one video, just return it
    if len(video_urls) == 1:
        return video_urls[0]["video_url"]

    # Create a unique concatenation signature based on sorted video URLs
    sorted_urls = sorted([v["video_url"] for v in video_urls])
    concat_signature = f"concat:{'|'.join(sorted_urls)}"

    # Check if we've already concatenated these exact videos
    from database.models import Video

    existing_videos = Video.query.filter_by(
        is_combined=True, original_prompt=concat_signature
    ).first()

    if existing_videos:
        print("Using cached concatenated video")
        return existing_videos.url_path

    # Sort videos by scene_id
    video_urls.sort(key=lambda x: x["scene_id"])

    try:
        # Create temp directory for FFmpeg files
        video_dir = VideoCache.get_static_video_dir()

        # Create a file list for FFmpeg
        file_list_path = os.path.join(video_dir, f"filelist_{uuid.uuid4()}.txt")

        # Get absolute paths for all videos
        video_paths = []
        for video in video_urls:
            video_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                video["video_url"].lstrip("/"),
            )
            video_paths.append(video_path)

        # Create file list for FFmpeg
        with open(file_list_path, "w") as f:
            for path in video_paths:
                f.write(f"file '{path}'\n")

        # Output path for concatenated video
        output_filename = VideoCache.generate_unique_filename()
        output_path = os.path.join(video_dir, output_filename)

        # Run FFmpeg to concatenate videos
        try:
            print("Concatenating videos with FFmpeg...")
            # Check if FFmpeg is installed
            ffmpeg_cmd = [
                "ffmpeg",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                file_list_path,
                "-c",
                "copy",
                output_path,
            ]
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)

            if result.returncode != 0:
                print(f"FFmpeg error: {result.stderr}")
                # If FFmpeg fails, fall back to the first video
                return video_urls[0]["video_url"]

            print(f"Videos concatenated successfully to {output_path}")

            # Delete individual videos after successful concatenation
            for video_path in video_paths:
                try:
                    if os.path.exists(video_path):
                        os.remove(video_path)
                        print(f"Deleted individual video: {video_path}")
                except Exception as del_err:
                    print(f"Error deleting individual video {video_path}: {del_err}")

            # Clean up the file list
            os.remove(file_list_path)

            # Register the concatenated video in our cache
            video_obj = VideoCache.save_video(
                f"/static/videos/{output_filename}",
                is_combined=True,
                original_prompt=concat_signature,
            )

            return video_obj.url_path

        except Exception as e:
            print(f"Error concatenating videos: {e}")
            # Fall back to the first video if concatenation fails
            return video_urls[0]["video_url"]

    except Exception as e:
        print(f"Error in concatenate_videos: {e}")
        # Fall back to the first video
        return video_urls[0]["video_url"]
