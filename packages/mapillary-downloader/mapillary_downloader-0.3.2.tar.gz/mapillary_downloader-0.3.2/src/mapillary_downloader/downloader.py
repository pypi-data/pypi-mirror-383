"""Main downloader logic."""

import json
import logging
import os
import time
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from mapillary_downloader.utils import format_size, format_time
from mapillary_downloader.ia_meta import generate_ia_metadata
from mapillary_downloader.worker import download_and_convert_image
from mapillary_downloader.tar_sequences import tar_sequence_directories
from mapillary_downloader.logging_config import add_file_handler

logger = logging.getLogger("mapillary_downloader")


class MapillaryDownloader:
    """Handles downloading Mapillary data for a user."""

    def __init__(self, client, output_dir, username=None, quality=None, workers=None, tar_sequences=True):
        """Initialize the downloader.

        Args:
            client: MapillaryClient instance
            output_dir: Base directory to save downloads
            username: Mapillary username (for collection directory)
            quality: Image quality (for collection directory)
            workers: Number of parallel workers (default: half of cpu_count)
            tar_sequences: Whether to tar sequence directories after download (default: True)
        """
        self.client = client
        self.base_output_dir = Path(output_dir)
        self.username = username
        self.quality = quality
        self.workers = workers if workers is not None else max(1, os.cpu_count() // 2)
        self.tar_sequences = tar_sequences

        # If username and quality provided, create collection directory
        if username and quality:
            collection_name = f"mapillary-{username}-{quality}"
            self.output_dir = self.base_output_dir / collection_name
        else:
            self.output_dir = self.base_output_dir

        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Set up file logging for archival
        log_file = self.output_dir / "download.log"
        add_file_handler(log_file)
        logger.info(f"Logging to: {log_file}")

        self.metadata_file = self.output_dir / "metadata.jsonl"
        self.progress_file = self.output_dir / "progress.json"
        self.downloaded = self._load_progress()

    def _load_progress(self):
        """Load previously downloaded image IDs."""
        if self.progress_file.exists():
            with open(self.progress_file) as f:
                return set(json.load(f).get("downloaded", []))
        return set()

    def _save_progress(self):
        """Save progress to disk atomically."""
        temp_file = self.progress_file.with_suffix(".json.tmp")
        with open(temp_file, "w") as f:
            json.dump({"downloaded": list(self.downloaded)}, f)
            f.flush()
            os.fsync(f.fileno())
        temp_file.replace(self.progress_file)

    def download_user_data(self, bbox=None, convert_webp=False):
        """Download all images for a user.

        Args:
            bbox: Optional bounding box [west, south, east, north]
            convert_webp: Convert images to WebP format after download
        """
        if not self.username or not self.quality:
            raise ValueError("Username and quality must be provided during initialization")

        quality_field = f"thumb_{self.quality}_url"

        logger.info(f"Downloading images for user: {self.username}")
        logger.info(f"Output directory: {self.output_dir}")
        logger.info(f"Quality: {self.quality}")
        logger.info(f"Using {self.workers} parallel workers")

        processed = 0
        downloaded_count = 0
        skipped = 0
        total_bytes = 0
        failed_count = 0

        start_time = time.time()

        # Track which image IDs we've seen in metadata to avoid re-fetching
        seen_ids = set()

        # Collect images to download from existing metadata
        images_to_download = []

        if self.metadata_file.exists():
            logger.info("Processing existing metadata file...")
            with open(self.metadata_file) as f:
                for line in f:
                    if line.strip():
                        image = json.loads(line)
                        image_id = image["id"]
                        seen_ids.add(image_id)
                        processed += 1

                        if image_id in self.downloaded:
                            skipped += 1
                            continue

                        # Queue for download
                        if image.get(quality_field):
                            images_to_download.append(image)

        # Download images from existing metadata in parallel
        if images_to_download:
            logger.info(f"Downloading {len(images_to_download)} images from existing metadata...")
            downloaded_count, total_bytes, failed_count = self._download_images_parallel(
                images_to_download, convert_webp
            )

        # Always check API for new images (will skip duplicates via seen_ids)
        logger.info("Checking for new images from API...")
        new_images = []

        with open(self.metadata_file, "a") as meta_f:
            for image in self.client.get_user_images(self.username, bbox=bbox):
                image_id = image["id"]

                # Skip if we already have this in our metadata file
                if image_id in seen_ids:
                    continue

                seen_ids.add(image_id)
                processed += 1

                # Save new metadata
                meta_f.write(json.dumps(image) + "\n")
                meta_f.flush()

                # Skip if already downloaded
                if image_id in self.downloaded:
                    skipped += 1
                    continue

                # Queue for download
                if image.get(quality_field):
                    new_images.append(image)

        # Download new images in parallel
        if new_images:
            logger.info(f"Downloading {len(new_images)} new images...")
            new_downloaded, new_bytes, new_failed = self._download_images_parallel(new_images, convert_webp)
            downloaded_count += new_downloaded
            total_bytes += new_bytes
            failed_count += new_failed

        self._save_progress()
        elapsed = time.time() - start_time
        logger.info(
            f"Complete! Processed {processed} images, downloaded {downloaded_count} ({format_size(total_bytes)}), "
            f"skipped {skipped}, failed {failed_count}"
        )
        logger.info(f"Total time: {format_time(elapsed)}")

        # Tar sequence directories for efficient IA uploads
        if self.tar_sequences:
            tar_sequence_directories(self.output_dir)

        # Generate IA metadata
        generate_ia_metadata(self.output_dir)

    def _download_images_parallel(self, images, convert_webp):
        """Download images in parallel using worker pool.

        Args:
            images: List of image metadata dicts
            convert_webp: Whether to convert to WebP

        Returns:
            Tuple of (downloaded_count, total_bytes, failed_count)
        """
        downloaded_count = 0
        total_bytes = 0
        failed_count = 0

        with ProcessPoolExecutor(max_workers=self.workers) as executor:
            # Submit all tasks
            future_to_image = {}
            for image in images:
                future = executor.submit(
                    download_and_convert_image,
                    image,
                    str(self.output_dir),
                    self.quality,
                    convert_webp,
                    self.client.access_token,
                )
                future_to_image[future] = image["id"]

            # Process results as they complete
            for future in as_completed(future_to_image):
                image_id, bytes_dl, success, error_msg = future.result()

                if success:
                    self.downloaded.add(image_id)
                    downloaded_count += 1
                    total_bytes += bytes_dl

                    if downloaded_count % 10 == 0:
                        logger.info(f"Downloaded: {downloaded_count}/{len(images)} ({format_size(total_bytes)})")
                        self._save_progress()
                else:
                    failed_count += 1
                    logger.warning(f"Failed to download {image_id}: {error_msg}")

        return downloaded_count, total_bytes, failed_count
