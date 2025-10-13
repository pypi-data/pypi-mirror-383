class NoIntersectionAreaFoundError(Exception):
    """Raised when no intersection area is found between two polygons"""


class BoundingBoxFaceError(Exception):
    pass


class IfcFileNotFoundError(FileNotFoundError):
    pass


class SpaceSurfaceAreaNullError(Exception):
    pass


class NoIfcSpaceFoundError(Exception):
    pass


class NoSpaceBoundariesError(Exception):
    pass


class InvalidLibraryError(Exception):
    pass


class VectorWithNansError(Exception):
    pass


class HasWindowsWithoutWallsError(Exception):
    pass
