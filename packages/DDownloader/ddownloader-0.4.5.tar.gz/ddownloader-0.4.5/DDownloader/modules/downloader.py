import os, requests
import subprocess
import logging
import platform
import coloredlogs
from tqdm import tqdm
from colorama import Fore

logger = logging.getLogger(Fore.RED + "+ DDOWNLOADER + ")
coloredlogs.install(level='DEBUG', logger=logger)

class DOWNLOADER:
    def __init__(self):
        self.manifest_url = None
        self.output_name = None
        self.proxy = None
        self.decryption_keys = []
        self.headers = []
        self.cookies = None
        self.binary_path = None
        self.auto_select = False

# =========================================================================================================== #

    def _get_binary_path(self, binary_type):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(base_dir)
        bin_dir = os.path.join(project_root, 'bin')

        if binary_type == 'N_m3u8DL-RE':
            binary_name = 'N_m3u8DL-RE.exe' if platform.system() == 'Windows' else 'N_m3u8DL-RE'
        elif binary_type == 'ffmpeg':
            binary_name = 'ffmpeg.exe' if platform.system() == 'Windows' else 'ffmpeg'
        elif binary_type == 'yt-dlp':
            binary_name = 'yt-dlp.exe' if platform.system() == 'Windows' else 'yt-dlp'
        else:
            raise ValueError(f"Unknown binary type: {binary_type}")

        # First check project's bin directory
        binary_path = os.path.join(bin_dir, binary_name)
        
        # For ffmpeg on Linux, fall back to system path if not found in project
        if binary_type == 'ffmpeg' and platform.system() == 'Linux' and not os.path.isfile(binary_path):
            system_ffmpeg = '/usr/bin/ffmpeg'
            if os.path.isfile(system_ffmpeg):
                binary_path = system_ffmpeg
                logger.info(Fore.YELLOW + f"Using system ffmpeg at: {binary_path}" + Fore.RESET)
            else:
                logger.error(f"ffmpeg not found in project bin or system path")
                raise FileNotFoundError(f"ffmpeg not found in project bin or system path")

        if not os.path.isfile(binary_path):
            logger.error(f"Binary not found: {binary_path}")
            raise FileNotFoundError(f"Binary not found: {binary_path}")

        if platform.system() == 'Linux' and not binary_path.startswith('/usr/bin/'):
            chmod_command = ['chmod', '+x', binary_path]
            try:
                subprocess.run(chmod_command, check=True)
                logger.info(Fore.CYAN + f"Set executable permission for: {binary_path}" + Fore.RESET)
            except subprocess.CalledProcessError as e:
                logger.error(Fore.RED + f"Failed to set executable permissions for: {binary_path}" + Fore.RESET)
                raise RuntimeError(f"Could not set executable permissions for: {binary_path}") from e

        return binary_path

# =========================================================================================================== #

    def drm_downloader(self):
        if not self.manifest_url:
            logger.error("Manifest URL is not set.")
            return
        command = self._build_command()
        self._execute_command(command)

# =========================================================================================================== #

    def _build_command(self):
        command = [
            self._get_binary_path("N_m3u8DL-RE"),
            f'"{self.manifest_url}"',
            '-mt',
            '-M', 'format=mp4',
            '--save-dir', '"downloads"',
            '--tmp-dir', '"downloads"',
            '--del-after-done',
            '--decryption-engine', '"FFMPEG"',
            '--decryption-binary-path', f'"{self._get_binary_path("ffmpeg")}"',
            '--save-name', f'"{self.output_name}"'
        ]

        for key in self.decryption_keys:
            command.extend(['--key', f'"{key}"'])

        if self.proxy:
            if not self.proxy.startswith("http://"):
                self.proxy = f"http://{self.proxy}"
            command.extend(['--custom-proxy', f'"{self.proxy}"'])
            
        if self.auto_select:
            command.extend(['--auto-select'])

        for header in self.headers:
            command.extend(['-H', f'"{header}"'])

        return command

# =========================================================================================================== #

    def _execute_command(self, command):
        """
        Execute a command using subprocess.run with proper return handling.
        """
        try:
            command_str = ' '.join(command)
            logger.debug(f"Executing: {command_str}")

            # Use shell=True on Windows for better path handling
            shell = platform.system() == 'Windows'
            subprocess.run(command, check=True, shell=shell)

            logger.info(Fore.GREEN + "Downloaded successfully. Bye!" + Fore.RESET)
            print(Fore.RED + "═" * 100 + Fore.RESET + "\n")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed with exit code: {e.returncode}")
            return False
        except Exception as e:
            logger.error(Fore.RED + f"An unexpected error occurred: {e}" + Fore.RESET)
            return False

# =========================================================================================================== #

    def iq_downloader(self, url, output_file, download_type="mp4", quality="best"):
        """
        Download a video from IQ.com using yt-dlp.
        """
        try:
            # Input validation
            if not url or not url.strip():
                logger.error(Fore.RED + "URL cannot be empty." + Fore.RESET)
                return None
                
            if not output_file or not output_file.strip():
                logger.error(Fore.RED + "Output file path cannot be empty." + Fore.RESET)
                return None

            if download_type not in ("mp4", "mp3"):
                logger.error(Fore.RED + f"Invalid download type: {download_type}. Use 'mp4' or 'mp3'." + Fore.RESET)
                return None

            # Get yt-dlp binary
            yt_dlp_path = self._get_binary_path("yt-dlp")
            if not yt_dlp_path or not os.path.exists(yt_dlp_path):
                logger.error(Fore.RED + "yt-dlp binary not found." + Fore.RESET)
                return None

            # Prepare output file path
            base_name = os.path.splitext(output_file)[0]
            output_file = base_name + (".mp3" if download_type == "mp3" else ".mp4")
            output_file = os.path.abspath(output_file)
            
            # Create output directory
            output_dir = os.path.dirname(output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)

            # Build command with proper quoting for paths and URLs
            command = [f'"{yt_dlp_path}"', "-o", f'"{output_file}"']

            # Basic options only (remove problematic ones)
            command.extend([
                "--no-warnings",
                "--ignore-errors",
            ])

            # Include cookies if available
            if self.cookies:
                cookies_path = self._resolve_cookies_path(self.cookies)
                if cookies_path and os.path.exists(cookies_path):
                    command.extend(["--cookies", f'"{cookies_path}"'])
                    logger.info(f"Using cookies file: {cookies_path}")

            # Audio options
            if download_type == "mp3":
                command.extend([
                    "--extract-audio",
                    "--audio-format", "mp3",
                    "--audio-quality", "0",
                ])
            # Video options
            else:
                command.extend([
                    "-f", "bestvideo[ext=mp4][height<=720]+bestaudio[ext=m4a]/best[ext=mp4][height<=720]/best",
                    "--merge-output-format", "mp4",
                ])

            command.append(f'"{url}"')

            # Log the full command for debugging
            full_command = ' '.join(command)
            logger.info(f"Full command: {full_command}")
            
            # Execute command
            logger.info(f"Starting download: {url}")
            logger.debug(f"Executing: {command_str}")

            try:
                subprocess.run(command, check=True)
                logger.info(Fore.GREEN + "Downloaded successfully. Bye!" + Fore.RESET)
                print(Fore.RED + "═" * 100 + Fore.RESET + "\n")
                success = True
            except subprocess.CalledProcessError as e:
                logger.error(f"Command failed with exit code: {e.returncode}")
                success = False
            except Exception as e:
                logger.error(Fore.RED + f"An unexpected error occurred: {e}" + Fore.RESET)
                success = False

            # Verify result
            if success and os.path.isfile(output_file):
                file_size = os.path.getsize(output_file)
                if file_size > 1024:  # At least 1KB
                    size_mb = file_size / (1024 * 1024)
                    logger.info(f"✅ Download completed: {output_file} ({size_mb:.2f} MB)")
                    return output_file
                else:
                    logger.error(f"Downloaded file is too small: {output_file}")
                    if os.path.exists(output_file):
                        os.remove(output_file)
            else:
                logger.error(f"Download failed: {output_file}")
                if output_file and os.path.exists(output_file):
                    try:
                        os.remove(output_file)
                    except OSError:
                        pass

            return None

        except Exception as e:
            logger.error(Fore.RED + f"Download failed: {e}" + Fore.RESET)
            # Cleanup on error
            if 'output_file' in locals() and output_file and os.path.exists(output_file):
                try:
                    os.remove(output_file)
                except OSError:
                    pass
            return None

    def _resolve_cookies_path(self, cookies_path):
        """Resolve cookies file path to absolute path."""
        try:
            # If it's already an absolute path, use it directly
            if os.path.isabs(cookies_path):
                return cookies_path
            
            # Try multiple possible locations
            possible_paths = []
            
            # 1. Relative to current working directory
            possible_paths.append(os.path.abspath(cookies_path))
            
            # 2. Relative to script directory
            script_dir = os.path.dirname(os.path.abspath(__file__))
            possible_paths.append(os.path.join(script_dir, cookies_path))
            
            # 3. Relative to project root (go up one level from modules)
            project_root = os.path.dirname(script_dir)
            possible_paths.append(os.path.join(project_root, cookies_path))
            
            # 4. Just the filename in current directory
            possible_paths.append(os.path.abspath(os.path.basename(cookies_path)))
            
            # Check each possible path
            for path in possible_paths:
                if os.path.exists(path):
                    logger.info(f"Found cookies file at: {path}")
                    return path
            
            # If not found, log all attempted paths for debugging
            logger.warning(f"Cookies file not found. Searched in: {possible_paths}")
            return None
            
        except Exception as e:
            logger.error(f"Error resolving cookies path: {e}")
            return None

# =========================================================================================================== #

    def re_encode_content(self, input_file, quality, codec="libx265", crf=23, preset="superfast", audio_bitrate="256k", fps=60):
        resolutions = {
            "HD": "1280:720",
            "FHD": "1920:1080",
            "UHD": "3840:2160"
        }

        quality = quality.upper()
        if quality not in resolutions:
            logger.error(f"Invalid quality '{quality}'. Choose from: HD, FHD, UHD.")
            return None

        input_file = os.path.abspath(input_file)
        if not os.path.isfile(input_file):
            logger.error(f"Input file does not exist: {input_file}")
            return None

        resolution = resolutions[quality]
        base_name, ext = os.path.splitext(input_file)
        output_file = os.path.abspath(f"{base_name}_{quality.lower()}{ext}")

        self.binary_path = self._get_binary_path("ffmpeg")

        logger.info(f"Re-encoding {input_file} to {quality} ({resolution}) at {fps} FPS using codec {codec}...")
        logger.info(f"Output file: {output_file}")

        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        # Build the ffmpeg command with multi-threading & FPS increase
        command = [
            self.binary_path,
            "-i", input_file,
            "-r", str(fps),  # Increase FPS
            "-vf", f"scale={resolution}:flags=lanczos,unsharp=5:5:1.0:5:5:0.0,hqdn3d=1.5:1.5:6:6",  # Scaling + Sharpening + Denoising
            "-c:v", codec,
            "-b:v", "25M",  # Video bitrate set to 25 Mbps for better quality
            "-crf", str(crf),  # CRF still included for quality control
            "-preset", preset,
            "-threads", "0",  # Enables multi-threading (uses all available CPU cores)
            "-c:a", "aac",
            "-b:a", audio_bitrate,
            "-movflags", "+faststart",
            "-pix_fmt", "yuv444p",  # Ensures compatibility
            output_file
        ]

        # Execute the command using `_execute_command`
        self._execute_command(command)

        # Check if output file exists to confirm success
        if os.path.isfile(output_file):
            logger.info(f"Re-encoding to {quality} at {fps} FPS completed successfully. Output saved to: {output_file}")
            return output_file
        else:
            logger.error(f"Re-encoding failed. Output file not created: {output_file}")
            return None
        
# =========================================================================================================== #

    def normal_downloader(self, url, output_file):
        """
        Download a video file from a given URL with a progress bar.
        Automatically adds .mp4 extension if missing.

        Args:
            url (str): The video URL to download.
            output_file (str): The output file path to save the video.
        """
        try:
            # Add .mp4 extension if not already present
            if not output_file.lower().endswith(".mp4"):
                output_file += ".mp4"

            # Send a GET request to the URL with stream=True
            response = requests.get(url, stream=True)
            response.raise_for_status()  # Raise an exception for HTTP errors

            # Get the total file size from the headers
            total_size = int(response.headers.get('content-length', 0))

            # Open the output file in binary write mode
            with open(output_file, 'wb') as file:
                # Use tqdm to show a progress bar
                with tqdm(
                    total=total_size,
                    unit='B',
                    unit_scale=True,
                    unit_divisor=1024,
                    desc=f"Downloading {os.path.basename(output_file)}",
                ) as progress:
                    # Write the content in chunks
                    for chunk in response.iter_content(chunk_size=1024):
                        file.write(chunk)
                        progress.update(len(chunk))

            print(f"Download complete: {output_file}")

        except requests.exceptions.RequestException as e:
            print(f"Error during download: {e}")
            
# =========================================================================================================== #

    def youtube_downloader(self, url, output_file, download_type="mp4", playlist=False):
        """
        Download a video, audio, or playlist from YouTube using yt-dlp.

        Args:
            url (str): The YouTube video or playlist URL.
            output_file (str): The output file path to save the video or audio.
            download_type (str): The type of download ("mp4" for video, "mp3" for audio).
            playlist (bool): Whether the URL is a playlist.
        """
        try:
            # Get the yt-dlp binary path
            yt_dlp_path = self._get_binary_path("yt-dlp")

            # Determine the output file extension based on download type
            if download_type == "mp3":
                output_file = os.path.splitext(output_file)[0] + ".mp3"
            elif download_type == "mp4":
                output_file = os.path.splitext(output_file)[0] + ".mp4"
            else:
                logger.error(Fore.RED + f"Invalid download type: {download_type}. Use 'mp4' or 'mp3'." + Fore.RESET)
                return

            # Build the yt-dlp command
            command = [
                yt_dlp_path,
                "-o", f"\"{output_file}\"",  # Output file
                "--no-check-certificate",  # Bypass certificate verification
                "--extractor-args", "youtube:player_client=android",  # Force a specific extractor
                "--ignore-errors",  # Ignore errors and continue downloading
            ]

            # Add cookies if provided
            if self.cookies:
                command.extend(["--cookies", f"\"{self.cookies}\""])

            # Add playlist-specific options if the URL is a playlist
            if playlist:
                command.extend([
                    "--yes-playlist",  # Force downloading the playlist
                    "--output", f"\"{output_file}/%(playlist_index)s - %(title)s.%(ext)s\"",  # Organize files in a folder
                ])
            else:
                command.extend([
                    "--no-playlist",  # Ignore playlists if the URL is a single video
                ])

            # Add audio extraction options if downloading MP3
            if download_type == "mp3":
                command.extend([
                    "--extract-audio",  # Extract audio
                    "--audio-format", "mp3",  # Convert to MP3
                    "--audio-quality", "0",  # Best quality
                ])
            else:
                # For MP4, download the best video and audio formats and merge them
                command.extend([
                    "-f", "bv*+ba/b",  # Download best video + best audio, or fallback to best combined format
                    "--merge-output-format", "mp4",  # Merge into MP4
                ])

            # Add the YouTube URL
            command.append(url)

            # Execute the command
            self._execute_command(command)

            # Check if output file(s) exist to confirm success
            if playlist:
                if os.path.exists(output_file) and os.listdir(output_file):
                    logger.info(f"Playlist download completed successfully. Files saved to: {output_file}")
                    return output_file
                else:
                    logger.error(f"Playlist download failed. No files were created in: {output_file}")
                    return None
            else:
                if os.path.isfile(output_file):
                    logger.info(f"Download from YouTube completed successfully. Output saved to: {output_file}")
                    return output_file
                else:
                    logger.error(f"Download from YouTube failed. Output file not created: {output_file}")
                    return None

        except Exception as e:
            logger.error(Fore.RED + f"An unexpected error occurred: {e}" + Fore.RESET)