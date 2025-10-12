"""Region - ported from Qontinui framework.

Represents a rectangular area on the screen.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from .location import Location


@dataclass
class Region:
    """Represents a rectangular area on the screen.

    Port of Region from Qontinui framework class.

    A Region is a fundamental data type that defines a rectangular area using x,y coordinates
    for the top-left corner and width,height dimensions. It serves as the spatial foundation for
    GUI element location and interaction in the model-based approach.

    In the context of model-based GUI automation, Regions are used to:
    - Define search areas for finding GUI elements (images, text, patterns)
    - Represent the boundaries of matched GUI elements
    - Specify areas for mouse and keyboard interactions
    - Create spatial relationships between GUI elements in States
    """

    x: int = 0
    """X coordinate of top-left corner."""

    y: int = 0
    """Y coordinate of top-left corner."""

    width: int = 0
    """Width of the region."""

    height: int = 0
    """Height of the region."""

    name: str | None = None
    """Optional name for this region."""

    def __post_init__(self) -> None:
        """Initialize with screen dimensions if width/height are 0."""
        if self.width == 0 and self.height == 0:
            # Try to get screen dimensions
            self.width, self.height = self._get_screen_dimensions()

    @property
    def right(self) -> int:
        """Get the right edge x-coordinate.

        Returns:
            X coordinate of right edge
        """
        return self.x + self.width

    @property
    def bottom(self) -> int:
        """Get the bottom edge y-coordinate.

        Returns:
            Y coordinate of bottom edge
        """
        return self.y + self.height

    @staticmethod
    def _get_screen_dimensions() -> tuple[int, int]:
        """Get screen dimensions.

        Returns:
            (width, height) tuple
        """
        # Try environment variables first
        width = int(os.environ.get("SCREEN_WIDTH", 0))
        height = int(os.environ.get("SCREEN_HEIGHT", 0))

        if width > 0 and height > 0:
            return width, height

        # Try tkinter
        try:
            import tkinter as tk

            root = tk.Tk()
            root.withdraw()
            width = root.winfo_screenwidth()
            height = root.winfo_screenheight()
            root.destroy()
            if width > 0 and height > 0:
                return width, height
        except Exception:
            pass

        # Default fallback
        return 1920, 1080

    @classmethod
    def from_xywh(cls, x: int, y: int, w: int, h: int) -> Region:
        """Create Region from x, y, width, height.

        Args:
            x: X coordinate
            y: Y coordinate
            w: Width
            h: Height

        Returns:
            New Region instance
        """
        return cls(x=x, y=y, width=w, height=h)

    @classmethod
    def from_bounds(cls, x1: int, y1: int, x2: int, y2: int) -> Region:
        """Create Region from bounding coordinates.

        Args:
            x1: Left x coordinate
            y1: Top y coordinate
            x2: Right x coordinate
            y2: Bottom y coordinate

        Returns:
            New Region instance
        """
        return cls(x=x1, y=y1, width=x2 - x1, height=y2 - y1)

    @classmethod
    def from_locations(cls, loc1: Location, loc2: Location) -> Region:
        """Create Region as bounding box of two locations.

        Args:
            loc1: First location
            loc2: Second location

        Returns:
            New Region containing both locations
        """
        x1 = min(loc1.x, loc2.x)
        y1 = min(loc1.y, loc2.y)
        x2 = max(loc1.x, loc2.x)
        y2 = max(loc1.y, loc2.y)
        return cls.from_bounds(x1, y1, x2, y2)

    @property
    def w(self) -> int:
        """Alias for width (Brobot compatibility)."""
        return self.width

    @w.setter
    def w(self, value: int) -> None:
        self.width = value

    @property
    def h(self) -> int:
        """Alias for height (Brobot compatibility)."""
        return self.height

    @h.setter
    def h(self, value: int) -> None:
        self.height = value

    @property
    def center(self) -> Location:
        """Get center location of this region.

        Returns:
            Center location
        """
        from .location import Location

        return Location(x=self.x + self.width // 2, y=self.y + self.height // 2)

    @property
    def top_left(self) -> Location:
        """Get top-left corner location.

        Returns:
            Top-left location
        """
        from .location import Location

        return Location(x=self.x, y=self.y)

    @property
    def top_right(self) -> Location:
        """Get top-right corner location.

        Returns:
            Top-right location
        """
        from .location import Location

        return Location(x=self.x + self.width, y=self.y)

    @property
    def bottom_left(self) -> Location:
        """Get bottom-left corner location.

        Returns:
            Bottom-left location
        """
        from .location import Location

        return Location(x=self.x, y=self.y + self.height)

    @property
    def bottom_right(self) -> Location:
        """Get bottom-right corner location.

        Returns:
            Bottom-right location
        """
        from .location import Location

        return Location(x=self.x + self.width, y=self.y + self.height)

    @property
    def area(self) -> int:
        """Get area of the region.

        Returns:
            Area in pixels
        """
        return self.width * self.height

    def contains(self, point: Location | tuple[int, int]) -> bool:
        """Check if a point is inside this region.

        Args:
            point: Location or (x, y) tuple

        Returns:
            True if point is inside
        """
        if isinstance(point, tuple):
            px, py = point
        else:
            px, py = point.x, point.y

        return self.x <= px <= self.x + self.width and self.y <= py <= self.y + self.height

    def overlaps(self, other: Region) -> bool:
        """Check if this region overlaps with another.

        Args:
            other: Other region

        Returns:
            True if regions overlap
        """
        return not (
            self.x + self.width < other.x
            or other.x + other.width < self.x
            or self.y + self.height < other.y
            or other.y + other.height < self.y
        )

    def intersection(self, other: Region) -> Region | None:
        """Get intersection with another region.

        Args:
            other: Other region

        Returns:
            Intersection region or None if no overlap
        """
        if not self.overlaps(other):
            return None

        x1 = max(self.x, other.x)
        y1 = max(self.y, other.y)
        x2 = min(self.x + self.width, other.x + other.width)
        y2 = min(self.y + self.height, other.y + other.height)

        return Region.from_bounds(x1, y1, x2, y2)

    def union(self, other: Region) -> Region:
        """Get union with another region.

        Args:
            other: Other region

        Returns:
            Union region containing both
        """
        x1 = min(self.x, other.x)
        y1 = min(self.y, other.y)
        x2 = max(self.x + self.width, other.x + other.width)
        y2 = max(self.y + self.height, other.y + other.height)

        return Region.from_bounds(x1, y1, x2, y2)

    def grow(self, pixels: int) -> Region:
        """Grow region by specified pixels in all directions.

        Args:
            pixels: Number of pixels to grow

        Returns:
            New grown region
        """
        return Region(
            x=self.x - pixels,
            y=self.y - pixels,
            width=self.width + 2 * pixels,
            height=self.height + 2 * pixels,
            name=self.name,
        )

    def shrink(self, pixels: int) -> Region:
        """Shrink region by specified pixels in all directions.

        Args:
            pixels: Number of pixels to shrink

        Returns:
            New shrunk region
        """
        return self.grow(-pixels)

    def offset(self, dx: int, dy: int) -> Region:
        """Create new region with offset.

        Args:
            dx: X offset
            dy: Y offset

        Returns:
            New offset region
        """
        return Region(
            x=self.x + dx, y=self.y + dy, width=self.width, height=self.height, name=self.name
        )

    def split_horizontal(self, parts: int) -> list[Region]:
        """Split region horizontally into equal parts.

        Args:
            parts: Number of parts

        Returns:
            List of regions
        """
        regions = []
        part_height = self.height // parts

        for i in range(parts):
            y = self.y + i * part_height
            h = part_height if i < parts - 1 else self.height - i * part_height
            regions.append(Region(x=self.x, y=y, width=self.width, height=h))

        return regions

    def split_vertical(self, parts: int) -> list[Region]:
        """Split region vertically into equal parts.

        Args:
            parts: Number of parts

        Returns:
            List of regions
        """
        regions = []
        part_width = self.width // parts

        for i in range(parts):
            x = self.x + i * part_width
            w = part_width if i < parts - 1 else self.width - i * part_width
            regions.append(Region(x=x, y=self.y, width=w, height=self.height))

        return regions

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation
        """
        return {
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "name": self.name,
        }

    def __str__(self) -> str:
        """String representation."""
        if self.name:
            return f"Region({self.name} at {self.x},{self.y} size {self.width}x{self.height})"
        return f"Region({self.x},{self.y},{self.width}x{self.height})"

    def __repr__(self) -> str:
        """Detailed representation."""
        return f"Region(x={self.x}, y={self.y}, width={self.width}, height={self.height})"

    def __eq__(self, other) -> bool:
        """Check equality."""
        if not isinstance(other, Region):
            return False
        return (
            self.x == other.x
            and self.y == other.y
            and self.width == other.width
            and self.height == other.height
        )

    def __lt__(self, other) -> bool:
        """Compare regions by area."""

        return cast(bool, self.area < other.area)

    def contains_point(self, x: int, y: int) -> bool:
        """Check if a point is inside this region.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            True if point is inside region
        """
        return self.x <= x < self.x + self.width and self.y <= y < self.y + self.height

    def is_defined(self) -> bool:
        """Check if region is defined (has non-zero area).

        Returns:
            True if region has non-zero width and height
        """
        return self.width > 0 and self.height > 0

    def get_center(self) -> Location:
        """Get center location (method version of center property).

        Returns:
            Center location
        """
        return self.center

    def distance_to(self, other: Region) -> float:
        """Calculate distance between this region and another.

        Args:
            other: Other region

        Returns:
            Distance between closest edges, 0 if overlapping
        """
        import math

        # If regions overlap, distance is 0
        if self.overlaps(other):
            return 0.0

        # Calculate horizontal distance
        if self.x + self.width < other.x:
            dx = other.x - (self.x + self.width)
        elif other.x + other.width < self.x:
            dx = self.x - (other.x + other.width)
        else:
            dx = 0

        # Calculate vertical distance
        if self.y + self.height < other.y:
            dy = other.y - (self.y + self.height)
        elif other.y + other.height < self.y:
            dy = self.y - (other.y + other.height)
        else:
            dy = 0

        return math.sqrt(dx * dx + dy * dy)

    def distance_from_center(self, x: int, y: int) -> float:
        """Calculate distance from center of this region to a point.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            Distance from center to point
        """
        import math

        center = self.center
        dx = center.x - x
        dy = center.y - y
        return math.sqrt(dx * dx + dy * dy)

    @property
    def left(self) -> int:
        """Get the left edge x-coordinate (alias for x).

        Returns:
            X coordinate of left edge
        """
        return self.x

    @property
    def top(self) -> int:
        """Get the top edge y-coordinate (alias for y).

        Returns:
            Y coordinate of top edge
        """
        return self.y

    def above(self, distance: int) -> Region:
        """Create a region above this one.

        Args:
            distance: Height of the new region

        Returns:
            New region above this one
        """
        return Region(
            x=self.x,
            y=self.y - distance,
            width=self.width,
            height=distance,
        )

    def below(self, distance: int) -> Region:
        """Create a region below this one.

        Args:
            distance: Height of the new region

        Returns:
            New region below this one
        """
        return Region(
            x=self.x,
            y=self.y + self.height,
            width=self.width,
            height=distance,
        )

    def left_of(self, distance: int) -> Region:
        """Create a region to the left of this one.

        Args:
            distance: Width of the new region

        Returns:
            New region to the left of this one
        """
        return Region(
            x=self.x - distance,
            y=self.y,
            width=distance,
            height=self.height,
        )

    def right_of(self, distance: int) -> Region:
        """Create a region to the right of this one.

        Args:
            distance: Width of the new region

        Returns:
            New region to the right of this one
        """
        return Region(
            x=self.x + self.width,
            y=self.y,
            width=distance,
            height=self.height,
        )
