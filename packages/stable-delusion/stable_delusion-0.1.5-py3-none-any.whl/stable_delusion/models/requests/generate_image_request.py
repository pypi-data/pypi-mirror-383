"""Image generation request model."""

__author__ = "Lene Preuss <lene.preuss@gmail.com>"

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from stable_delusion.exceptions import ValidationError
from stable_delusion.config import SUPPORTED_MODELS
from stable_delusion.models.requests.validation import validate_image_size


@dataclass
class GenerateImageRequest:
    """Request DTO for image generation endpoint."""

    prompt: str
    images: List[Path]
    project_id: Optional[str] = None
    location: Optional[str] = None
    output_dir: Optional[Path] = None
    output_filename: Optional[str] = None
    scale: Optional[int] = None
    image_size: Optional[str] = None
    storage_type: Optional[str] = None
    model: Optional[str] = None

    def _validate_basic_fields(self) -> None:
        if not self.prompt or not self.prompt.strip():
            raise ValidationError("Prompt cannot be empty", field="prompt", value=self.prompt)

        # Allow empty images for Seedream text-to-image generation
        if not self.images and self.model != "seedream":
            raise ValidationError("At least one image is required", field="images")

        # Validate scale if provided
        if self.scale is not None and self.scale not in [2, 4]:
            raise ValidationError("Scale must be 2 or 4", field="scale", value=str(self.scale))

    def _validate_model_specific_parameters(self) -> None:
        # Validate that scale and image_size are mutually exclusive
        if self.scale is not None and self.image_size is not None:
            raise ValidationError(
                "Scale and image_size are mutually exclusive. Use scale for "
                "Gemini model or image_size for Seedream model.",
                field="scale",
            )

        # Validate that scale is only used with Gemini model
        if self.scale is not None and self.model == "seedream":
            raise ValidationError(
                "Scale parameter is only available for Gemini model",
                field="scale",
                value=str(self.scale),
            )

        # Validate that image_size is only used with Seedream model
        if self.image_size is not None and self.model == "gemini":
            raise ValidationError(
                "Image size parameter is only available for Seedream model",
                field="image_size",
                value=self.image_size,
            )

    def _validate_format_and_enums(self) -> None:
        # Validate image_size format if provided
        if self.image_size is not None and not validate_image_size(self.image_size):
            raise ValidationError(
                "Image size must be '1K', '2K', '4K', or '{width}x{height}' "
                "where width is 1280-4096 and height is 720-4096",
                field="image_size",
                value=self.image_size,
            )

        # Validate storage_type if provided
        if self.storage_type is not None and self.storage_type not in ["local", "s3"]:
            raise ValidationError(
                "Storage type must be 'local' or 's3'",
                field="storage_type",
                value=self.storage_type,
            )

        # Validate model if provided
        if self.model is not None and self.model not in SUPPORTED_MODELS:
            raise ValidationError(
                f"Model must be one of {SUPPORTED_MODELS}", field="model", value=self.model
            )

    def _validate_business_rules(self) -> None:
        # Validate that Seedream with images requires S3 storage
        seedream_with_images = self.model == "seedream" and self.images
        if seedream_with_images and self.storage_type != "s3":
            raise ValidationError(
                "Seedream model with input images requires S3 storage type. "
                "Use --storage-type s3 when providing images with Seedream.",
                field="storage_type",
                value=self.storage_type or "None",
            )

    def __post_init__(self) -> None:
        self._validate_basic_fields()
        self._validate_model_specific_parameters()
        self._validate_format_and_enums()
        self._validate_business_rules()

        # Ensure output_dir is Path object if provided as string
        if isinstance(self.output_dir, str):
            self.output_dir = Path(self.output_dir)
