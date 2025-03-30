import os
import uuid

from flask import current_app

from .models import Video, db


class VideoCache:
    """
    A class to manage video caching within the application.
    Ensures videos are properly stored and retrieved.
    """

    @staticmethod
    def save_video(file_path, scene_id=None, is_combined=False, original_prompt=None):
        """
        Register a video file in the database for caching.

        Args:
            file_path: The relative path to the video file (e.g., '/static/videos/xyz.mp4')
            scene_id: Optional scene ID associated with the video
            is_combined: Whether this is a combined video (multiple scenes)
            original_prompt: The prompt used to generate the video

        Returns:
            The database Video object
        """
        # Clean the path to ensure consistent format
        clean_path = file_path.lstrip("/")
        if clean_path.startswith("static/"):
            url_path = f"/{clean_path}"
        else:
            url_path = f"/static/videos/{os.path.basename(clean_path)}"

        # Extract the filename from the path
        filename = os.path.basename(clean_path)

        # Check if this video already exists in the database
        existing_video = Video.query.filter_by(filename=filename).first()
        if existing_video:
            return existing_video

        # Create a new video record
        video = Video(
            filename=filename,
            url_path=url_path,
            scene_id=scene_id,
            is_combined=is_combined,
            original_prompt=original_prompt,
        )

        db.session.add(video)
        db.session.commit()
        return video

    @staticmethod
    def get_video_by_prompt(prompt):
        """
        Find a video by its original prompt.
        Useful for retrieving previously generated videos for the same prompt.

        Args:
            prompt: The prompt used to generate the video

        Returns:
            The Video object if found, None otherwise
        """
        return Video.query.filter_by(original_prompt=prompt).first()

    @staticmethod
    def get_video_path(video_id):
        """
        Get the full filesystem path to a video by its ID.

        Args:
            video_id: The database ID of the video

        Returns:
            The full filesystem path to the video file
        """
        video = Video.query.get(video_id)
        if not video:
            return None

        # Strip leading slash if present
        relative_path = video.url_path.lstrip("/")

        # Get the root directory of the Flask app
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(root_dir, relative_path)

    @staticmethod
    def generate_unique_filename(extension=".mp4"):
        """
        Generate a unique filename for a new video.

        Args:
            extension: The file extension (default: .mp4)

        Returns:
            A unique filename string
        """
        return f"{uuid.uuid4()}{extension}"

    @staticmethod
    def get_static_video_dir():
        """
        Get the absolute path to the videos directory.
        Creates the directory if it doesn't exist.

        Returns:
            Absolute path to the videos directory
        """
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        video_dir = os.path.join(root_dir, "static", "videos")

        if not os.path.exists(video_dir):
            os.makedirs(video_dir, exist_ok=True)

        return video_dir

    @staticmethod
    def clean_unused_videos(age_in_days=7):
        """
        Remove video files that are older than the specified age and not associated with any session.

        Args:
            age_in_days: Age threshold in days (default: 7)

        Returns:
            Number of videos removed
        """
        # Implementation to be added based on app requirements
        pass
