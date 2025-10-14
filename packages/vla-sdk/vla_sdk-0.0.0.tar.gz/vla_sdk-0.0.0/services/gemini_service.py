import os
import base64
import io
import asyncio
import json
from pathlib import Path
from typing import Optional, Dict, Any, List, Union
from PIL import Image
import cv2
import numpy as np
from google import genai
from google.genai import types
from services.bounding_boxes import (
    BoundingBox,
    plot_bounding_boxes_on_image,
    create_bounding_box_prompt,
    extract_frame_from_video_at_timestamp,
)

MODEL = "gemini-2.5-flash"


class GeminiVideoService:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("Gemini API key is required")

        self.client = genai.Client(api_key=api_key)

        self.config = types.GenerateContentConfig(
            temperature=0.7,
            top_p=0.95,
            top_k=40,
            candidate_count=1,
            max_output_tokens=2048,
        )

    async def upload_file(self, file_path: Path) -> Dict[str, Any]:
        """Upload a file to Gemini Files API following the documentation pattern"""
        try:
            # Upload file to Gemini using the same pattern as the documentation
            uploaded_file = await self.client.aio.files.upload(file=file_path)

            # Wait for file to be processed
            while uploaded_file.state == "PROCESSING":
                await asyncio.sleep(1)
                uploaded_file = await self.client.aio.files.get(name=uploaded_file.name)

            if uploaded_file.state == "FAILED":
                raise Exception(f"File upload failed: {uploaded_file.error}")

            return {
                "name": uploaded_file.name,
                "uri": uploaded_file.uri,
                "mime_type": uploaded_file.mime_type,
                "size_bytes": uploaded_file.size_bytes,
                "state": uploaded_file.state,
                "display_name": uploaded_file.display_name,
                "create_time": uploaded_file.create_time.isoformat()
                if uploaded_file.create_time
                else None,
                "update_time": uploaded_file.update_time.isoformat()
                if uploaded_file.update_time
                else None,
                "file_object": uploaded_file,  # Store the actual file object for later use
            }

        except Exception as e:
            raise Exception(f"Failed to upload file to Gemini: {str(e)}")

    async def list_files(self) -> List[Dict[str, Any]]:
        """List all files uploaded to Gemini"""
        try:
            files = []
            files_response = await self.client.aio.files.list()
            for file in files_response:
                files.append(
                    {
                        "name": file.name,
                        "uri": file.uri,
                        "mime_type": file.mime_type,
                        "size_bytes": file.size_bytes,
                        "state": file.state,
                        "display_name": file.display_name,
                        "create_time": file.create_time.isoformat()
                        if file.create_time
                        else None,
                    }
                )
            return files
        except Exception as e:
            raise Exception(f"Failed to list files: {str(e)}")

    async def delete_file(self, file_name: str) -> bool:
        """Delete a file from Gemini"""
        try:
            await self.client.aio.files.delete(name=file_name)
            return True
        except Exception as e:
            raise Exception(f"Failed to delete file: {str(e)}")

    async def get_file(self, file_name: str) -> Dict[str, Any]:
        """Get file details from Gemini"""
        try:
            file = await self.client.aio.files.get(name=file_name)
            return {
                "name": file.name,
                "uri": file.uri,
                "mime_type": file.mime_type,
                "size_bytes": file.size_bytes,
                "state": file.state,
                "display_name": file.display_name,
                "create_time": file.create_time.isoformat()
                if file.create_time
                else None,
                "update_time": file.update_time.isoformat()
                if file.update_time
                else None,
                "file_object": file,
            }
        except Exception as e:
            raise Exception(f"Failed to get file: {str(e)}")

    async def query_video_with_file(self, file_name: str, prompt: str) -> str:
        """Query a video using its Gemini file name, following documentation pattern"""
        try:
            # Get the file object
            file = await self.client.aio.files.get(name=file_name)

            # Generate content using the same pattern as the documentation
            response = await self.client.aio.models.generate_content(
                model=MODEL,
                contents=[
                    file,
                    "\n\n",
                    prompt,
                ],
            )

            return response.text

        except Exception as e:
            return f"Error processing video: {str(e)}"

    async def find_timestamp_with_file(
        self, file_name: str, query: str
    ) -> Dict[str, Any]:
        """Find a timestamp in video using its Gemini file name"""
        try:
            # Get the file object
            file = await self.client.aio.files.get(name=file_name)

            prompt = f"""Analyze this video and find the timestamp that best matches the following query: {query}

Return ONLY a JSON object with these fields:
- timestamp: the time in seconds (number)
- confidence: confidence score between 0 and 1 (number)
- description: brief description of what happens at that timestamp (string)

Example response:
{{"timestamp": 45.5, "confidence": 0.85, "description": "Person waves at the camera"}}"""

            # Generate content using the same pattern as the documentation
            response = await self.client.aio.models.generate_content(
                model=MODEL,
                contents=[
                    file,
                    "\n\n",
                    prompt,
                ],
            )

            response_text = response.text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]

            try:
                result = json.loads(response_text)
                return result
            except json.JSONDecodeError:
                return {
                    "timestamp": 0,
                    "confidence": 0,
                    "description": response_text,
                }

        except Exception as e:
            return {"error": str(e)}

    async def find_multiple_timestamps_with_file(
        self, file_name: str, query: str
    ) -> Dict[str, Any]:
        """Find multiple timestamps in video that match the query"""
        try:
            # Get the file object
            file = await self.client.aio.files.get(name=file_name)

            prompt = f"""Analyze this video and find ALL timestamps that match the following query: {query}

Return ONLY a JSON object with these fields:
- timestamps: an array of matching timestamps, where each item has:
  - timestamp: the time in seconds (number)
  - confidence: confidence score between 0 and 1 (number)
  - description: brief description of what happens at that timestamp (string)
- total_found: the total number of matching timestamps found (number)

Example response:
{{
  "timestamps": [
    {{"timestamp": 12.5, "confidence": 0.95, "description": "First occurrence of person waving"}},
    {{"timestamp": 45.5, "confidence": 0.85, "description": "Person waves again at the camera"}},
    {{"timestamp": 78.0, "confidence": 0.75, "description": "Brief wave before leaving"}}
  ],
  "total_found": 3
}}

If only one match is found, still return it in an array format.
If no matches are found, return an empty timestamps array with total_found: 0."""

            # Generate content using the same pattern as the documentation
            response = await self.client.aio.models.generate_content(
                model=MODEL,
                contents=[
                    file,
                    "\n\n",
                    prompt,
                ],
            )

            response_text = response.text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]

            try:
                result = json.loads(response_text)
                # Ensure the response has the expected structure
                if "timestamps" not in result:
                    result = {"timestamps": [], "total_found": 0}
                if "total_found" not in result:
                    result["total_found"] = len(result.get("timestamps", []))
                return result
            except json.JSONDecodeError:
                return {
                    "timestamps": [],
                    "total_found": 0,
                    "error": "Failed to parse response",
                    "raw_response": response_text,
                }

        except Exception as e:
            return {"error": str(e), "timestamps": [], "total_found": 0}

    async def query_video_at_timestamps(
        self, file_name: str, timestamps: list[str], prompt: str
    ) -> str:
        """Query a video at specific timestamps, following documentation pattern"""
        try:
            # Get the file object
            file = await self.client.aio.files.get(name=file_name)

            # Format timestamps for the prompt
            timestamp_list = ", ".join(timestamps)

            # Create the prompt with timestamps
            formatted_prompt = f"""Please analyze this video at the following specific timestamps: {timestamp_list}

{prompt}

Focus specifically on what happens at the mentioned timestamps."""

            # Generate content using the same pattern as the documentation
            response = await self.client.aio.models.generate_content(
                model=MODEL,
                contents=[
                    file,
                    "\n\n",
                    formatted_prompt,
                ],
            )

            return response.text

        except Exception as e:
            return f"Error processing video at timestamps: {str(e)}"

    async def analyze_video_range(
        self, file_name: str, start_timestamp: str, end_timestamp: str, prompt: str
    ) -> str:
        """Analyze a video between two timestamps"""
        try:
            # Get the file object
            file = await self.client.aio.files.get(name=file_name)

            # Create the prompt for range analysis
            formatted_prompt = f"""Please analyze this video between {start_timestamp} and {end_timestamp}.

{prompt}

Focus specifically on what happens during this time period from {start_timestamp} to {end_timestamp}."""

            # Generate content using the same pattern as the documentation
            response = await self.client.aio.models.generate_content(
                model=MODEL,
                contents=[
                    file,
                    "\n\n",
                    formatted_prompt,
                ],
            )

            return response.text

        except Exception as e:
            return f"Error analyzing video range: {str(e)}"

    async def detect_objects_at_timestamps(
        self, file_name: str, timestamps: list[str], query: str, video_path: Optional[Path] = None
    ) -> List[Dict[str, Any]]:
        """Detect objects with bounding boxes at specific timestamps"""
        try:
            # Get the file object
            file = await self.client.aio.files.get(name=file_name)

            results = []

            for timestamp in timestamps:
                # Create object detection prompt
                prompt = create_bounding_box_prompt(query, timestamp)

                # Configure for bounding box detection
                config = types.GenerateContentConfig(
                    system_instruction="""
                    Return bounding boxes as an array with labels.
                    Never return masks. Limit to 25 objects.
                    If an object is present multiple times, give each object a unique label
                    according to its distinct characteristics (colors, size, position, etc.).
                    """,
                    temperature=0.5,
                    response_mime_type="application/json",
                    response_schema=list[BoundingBox],
                )

                # Generate content with bounding box detection
                response = await self.client.aio.models.generate_content(
                    model="gemini-2.5-flash",  # Use standard model for vision tasks
                    contents=[
                        file,
                        f"\n\nAt timestamp {timestamp}: {prompt}",
                    ],
                    config=config,
                )

                # Parse bounding boxes
                try:
                    bounding_boxes = [
                        BoundingBox(**box) for box in json.loads(response.text)
                    ]

                    result = {
                        "timestamp": timestamp,
                        "objects_detected": len(bounding_boxes),
                        "bounding_boxes": [bbox.dict() for bbox in bounding_boxes],
                        "raw_response": response.text,
                    }

                    # If we have a video path and bounding boxes, extract frame and create annotated image
                    if video_path and bounding_boxes:
                        try:
                            # Extract frame at timestamp
                            frame_data = extract_frame_from_video_at_timestamp(video_path, timestamp)

                            # Create annotated image with bounding boxes (returns base64)
                            annotated_image_base64 = plot_bounding_boxes_on_image(frame_data, bounding_boxes)

                            # Add base64 image to result
                            result["annotated_image_base64"] = annotated_image_base64
                            result["annotated_image_mime_type"] = "image/jpeg"

                        except Exception as e:
                            result["image_error"] = f"Failed to create annotated image: {str(e)}"
                    elif bounding_boxes and not video_path:
                        result["image_note"] = "No annotated image generated. Re-upload the video to enable image generation."

                    results.append(result)

                except (json.JSONDecodeError, Exception) as e:
                    results.append(
                        {
                            "timestamp": timestamp,
                            "error": f"Failed to parse bounding boxes: {str(e)}",
                            "raw_response": response.text,
                        }
                    )

            return results

        except Exception as e:
            return [{"error": f"Error detecting objects at timestamps: {str(e)}"}]

    async def find_objects_in_video(self, file_name: str, query: str) -> Dict[str, Any]:
        """Find objects throughout the video and return when they appear with bounding boxes"""
        try:
            # Get the file object
            file = await self.client.aio.files.get(name=file_name)

            # Create prompt to find objects throughout the video
            prompt = f"""
            Analyze this entire video to find: {query}

            For each occurrence of the objects:
            1. Identify the timestamp when they appear
            2. Provide bounding box coordinates
            3. Describe their characteristics

            Return a detailed analysis with timestamps and object descriptions.
            If you can identify specific frames where bounding boxes would be most useful,
            mention those timestamps.
            """

            # First, get general information about when objects appear
            response = await self.client.aio.models.generate_content(
                model=MODEL,
                contents=[
                    file,
                    "\n\n",
                    prompt,
                ],
                config=self.config,
            )

            return {
                "query": query,
                "analysis": response.text,
                "note": "Use the /search/boxes endpoint with specific timestamps for bounding box detection",
                "suggested_action": "Extract key timestamps from this analysis and call /search/boxes again with timestamps parameter",
            }

        except Exception as e:
            return {"error": f"Error finding objects in video: {str(e)}"}

    # Compatibility methods using URI (kept for backwards compatibility)
    async def query_video_with_uri(self, file_uri: str, prompt: str) -> str:
        """Query a video using its Gemini file URI (compatibility method)"""
        # Extract file name from URI
        file_name = file_uri.split("/")[-1] if "/" in file_uri else file_uri
        return await self.query_video_with_file(file_name, prompt)

    async def find_timestamp_with_uri(
        self, file_uri: str, query: str
    ) -> Dict[str, Any]:
        """Find a timestamp in video using its Gemini file URI (compatibility method)"""
        # Extract file name from URI
        file_name = file_uri.split("/")[-1] if "/" in file_uri else file_uri
        return await self.find_timestamp_with_file(file_name, query)

    # Legacy methods for local file processing (kept for backwards compatibility)
    def extract_frames_from_video(
        self, video_path: Path, sample_rate: int = 1
    ) -> List[Dict[str, str]]:
        frames = []
        cap = cv2.VideoCapture(str(video_path))

        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = 0
        sample_interval = int(fps * sample_rate)

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_count % sample_interval == 0:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                img.thumbnail([1024, 1024])

                image_io = io.BytesIO()
                img.save(image_io, format="JPEG")
                image_io.seek(0)

                timestamp = frame_count / fps
                frames.append(
                    {
                        "mime_type": "image/jpeg",
                        "data": base64.b64encode(image_io.read()).decode(),
                        "timestamp": timestamp,
                    }
                )

            frame_count += 1

        cap.release()
        return frames

    async def query_video(self, video_path: Path, prompt: str) -> str:
        try:
            frames = self.extract_frames_from_video(video_path, sample_rate=2)

            if not frames:
                return "Could not extract frames from video"

            contents = []

            contents.append(
                f"This video has {len(frames)} sampled frames over time. Each frame represents approximately 2 seconds of video."
            )

            for i, frame in enumerate(frames[:30]):
                contents.append(
                    types.Part(
                        inline_data=types.Blob(
                            mime_type=frame["mime_type"], data=frame["data"]
                        )
                    )
                )
                contents.append(
                    f"Frame {i + 1} at timestamp {frame['timestamp']:.2f} seconds"
                )

            contents.append(f"\nUser query: {prompt}")

            response = await self.client.aio.models.generate_content(
                model=MODEL,
                contents=contents,
                config=self.config,
            )

            return response.text

        except Exception as e:
            return f"Error processing video: {str(e)}"

    async def find_timestamp(self, video_path: Path, query: str) -> Dict[str, Any]:
        try:
            frames = self.extract_frames_from_video(video_path, sample_rate=2)

            if not frames:
                return {"error": "Could not extract frames from video"}

            contents = []

            contents.append(
                f"Analyze this video and find the timestamp that best matches the following query: {query}"
            )
            contents.append(
                "Return ONLY a JSON object with 'timestamp' (in seconds), 'confidence' (0-1), and 'description' fields."
            )

            for i, frame in enumerate(frames[:30]):
                contents.append(
                    types.Part(
                        inline_data=types.Blob(
                            mime_type=frame["mime_type"], data=frame["data"]
                        )
                    )
                )
                contents.append(f"Timestamp: {frame['timestamp']:.2f} seconds")

            response = await self.client.aio.models.generate_content(
                model=MODEL,
                contents=contents,
                config=self.config,
            )

            response_text = response.text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]

            try:
                result = json.loads(response_text)
                return result
            except json.JSONDecodeError:
                return {
                    "timestamp": 0,
                    "confidence": 0,
                    "description": response_text,
                }

        except Exception as e:
            return {"error": str(e)}
