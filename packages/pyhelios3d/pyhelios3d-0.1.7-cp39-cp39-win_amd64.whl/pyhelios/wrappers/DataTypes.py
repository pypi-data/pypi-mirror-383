import ctypes
import math
from typing import Any, List
from enum import IntEnum


class PrimitiveType(IntEnum):
    """Helios primitive type enumeration."""
    Patch = 0
    Triangle = 1
    Disk = 2
    Tile = 3
    Sphere = 4
    Tube = 5
    Box = 6
    Cone = 7
    Polymesh = 8

class int2(ctypes.Structure):
    _fields_ = [('x', ctypes.c_int32), ('y', ctypes.c_int32)]

    def __repr__(self) -> str:
        return f'int2({self.x}, {self.y})'
    
    def __str__(self) -> str:
        return f'int2({self.x}, {self.y})'
    
    def __init__(self, x:int=0, y:int=0):
        # Validate integer inputs
        if not isinstance(x, int):
            raise ValueError(f"int2.x must be an integer, got {type(x).__name__}: {x}")
        if not isinstance(y, int):
            raise ValueError(f"int2.y must be an integer, got {type(y).__name__}: {y}")
        
        self.x = x
        self.y = y

    def from_list(self, input_list:List[int]):
        self.x = input_list[0]
        self.y = input_list[1]

    def to_list(self) -> List[int]:
        return [self.x, self.y]

    
    
class int3(ctypes.Structure):
    _fields_ = [('x', ctypes.c_int32), ('y', ctypes.c_int32), ('z', ctypes.c_int32)]

    def __repr__(self) -> str:
        return f'int3({self.x}, {self.y}, {self.z})'
    
    def __str__(self) -> str:
        return f'int3({self.x}, {self.y}, {self.z})'
    
    def __init__(self, x:int=0, y:int=0, z:int=0):
        # Validate integer inputs
        if not isinstance(x, int):
            raise ValueError(f"int3.x must be an integer, got {type(x).__name__}: {x}")
        if not isinstance(y, int):
            raise ValueError(f"int3.y must be an integer, got {type(y).__name__}: {y}")
        if not isinstance(z, int):
            raise ValueError(f"int3.z must be an integer, got {type(z).__name__}: {z}")
        
        self.x = x
        self.y = y
        self.z = z

    def from_list(self, input_list:List[int]):
        self.x = input_list[0]
        self.y = input_list[1]
        self.z = input_list[2]

    def to_list(self) -> List[int]:
        return [self.x, self.y, self.z]
    
    
    
class int4(ctypes.Structure):
    _fields_ = [('x', ctypes.c_int32), ('y', ctypes.c_int32), ('z', ctypes.c_int32), ('w', ctypes.c_int32)]

    def __repr__(self) -> str:
        return f'int4({self.x}, {self.y}, {self.z}, {self.w})'
    
    def __str__(self) -> str:
        return f'int4({self.x}, {self.y}, {self.z}, {self.w})'
    
    def __init__(self, x:int=0, y:int=0, z:int=0, w:int=0):
        # Validate integer inputs
        if not isinstance(x, int):
            raise ValueError(f"int4.x must be an integer, got {type(x).__name__}: {x}")
        if not isinstance(y, int):
            raise ValueError(f"int4.y must be an integer, got {type(y).__name__}: {y}")
        if not isinstance(z, int):
            raise ValueError(f"int4.z must be an integer, got {type(z).__name__}: {z}")
        if not isinstance(w, int):
            raise ValueError(f"int4.w must be an integer, got {type(w).__name__}: {w}")
        
        self.x = x
        self.y = y
        self.z = z
        self.w = w

    def from_list(self, input_list:List[int]):
        self.x = input_list[0]
        self.y = input_list[1]
        self.z = input_list[2]
        self.w = input_list[3]

    def to_list(self) -> List[int]:
        return [self.x, self.y, self.z, self.w]
    
   
    
class vec2(ctypes.Structure):
    _fields_ = [('x', ctypes.c_float), ('y', ctypes.c_float)]

    def __repr__(self) -> str:
        return f'vec2({self.x}, {self.y})'
    
    def __str__(self) -> str:
        return f'vec2({self.x}, {self.y})'
    
    def __init__(self, x:float=0, y:float=0):
        # Validate finite numeric inputs
        if not self._is_finite_numeric(x):
            raise ValueError(f"vec2.x must be a finite number, got {type(x).__name__}: {x}. "
                           f"Vector components must be finite (not NaN or infinity).")
        if not self._is_finite_numeric(y):
            raise ValueError(f"vec2.y must be a finite number, got {type(y).__name__}: {y}. "
                           f"Vector components must be finite (not NaN or infinity).")
        
        self.x = float(x)
        self.y = float(y)

    def from_list(self, input_list:List[float]):
        self.x = input_list[0]
        self.y = input_list[1]

    def to_list(self) -> List[float]:
        return [self.x, self.y]
    
    @staticmethod
    def _is_finite_numeric(value) -> bool:
        """Check if value is a finite number (not NaN or inf)."""
        try:
            float_value = float(value)
            return math.isfinite(float_value)
        except (ValueError, TypeError, OverflowError):
            return False
    
class vec3(ctypes.Structure):
    _fields_ = [('x', ctypes.c_float), ('y', ctypes.c_float), ('z', ctypes.c_float)]

    def __repr__(self) -> str:
        return f'vec3({self.x}, {self.y}, {self.z})'
    
    def __str__(self) -> str:
        return f'vec3({self.x}, {self.y}, {self.z})'
    
    def __init__(self, x:float=0, y:float=0, z:float=0):
        # Validate finite numeric inputs
        if not self._is_finite_numeric(x):
            raise ValueError(f"vec3.x must be a finite number, got {type(x).__name__}: {x}. "
                           f"Vector components must be finite (not NaN or infinity).")
        if not self._is_finite_numeric(y):
            raise ValueError(f"vec3.y must be a finite number, got {type(y).__name__}: {y}. "
                           f"Vector components must be finite (not NaN or infinity).")
        if not self._is_finite_numeric(z):
            raise ValueError(f"vec3.z must be a finite number, got {type(z).__name__}: {z}. "
                           f"Vector components must be finite (not NaN or infinity).")
        
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def from_list(self, input_list:List[float]):
        self.x = input_list[0]
        self.y = input_list[1]
        self.z = input_list[2]

    def to_list(self) -> List[float]:
        return [self.x, self.y, self.z]
    
    def to_tuple(self) -> tuple:
        return (self.x, self.y, self.z)
    
    @staticmethod
    def _is_finite_numeric(value) -> bool:
        """Check if value is a finite number (not NaN or inf)."""
        try:
            float_value = float(value)
            return math.isfinite(float_value)
        except (ValueError, TypeError, OverflowError):
            return False
    
    
class vec4(ctypes.Structure):
    _fields_ = [('x', ctypes.c_float), ('y', ctypes.c_float), ('z', ctypes.c_float), ('w', ctypes.c_float)]

    def __repr__(self) -> str:
        return f'vec4({self.x}, {self.y}, {self.z}, {self.w})'
    
    def __str__(self) -> str:
        return f'vec4({self.x}, {self.y}, {self.z}, {self.w})'
    
    def __init__(self, x:float=0, y:float=0, z:float=0, w:float=0):
        # Validate finite numeric inputs
        if not self._is_finite_numeric(x):
            raise ValueError(f"vec4.x must be a finite number, got {type(x).__name__}: {x}. "
                           f"Vector components must be finite (not NaN or infinity).")
        if not self._is_finite_numeric(y):
            raise ValueError(f"vec4.y must be a finite number, got {type(y).__name__}: {y}. "
                           f"Vector components must be finite (not NaN or infinity).")
        if not self._is_finite_numeric(z):
            raise ValueError(f"vec4.z must be a finite number, got {type(z).__name__}: {z}. "
                           f"Vector components must be finite (not NaN or infinity).")
        if not self._is_finite_numeric(w):
            raise ValueError(f"vec4.w must be a finite number, got {type(w).__name__}: {w}. "
                           f"Vector components must be finite (not NaN or infinity).")
        
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.w = float(w)

    def from_list(self, input_list:List[float]):
        self.x = input_list[0]
        self.y = input_list[1]
        self.z = input_list[2]
        self.w = input_list[3]

    def to_list(self) -> List[float]:
        return [self.x, self.y, self.z, self.w]
    
    @staticmethod
    def _is_finite_numeric(value) -> bool:
        """Check if value is a finite number (not NaN or inf)."""
        try:
            float_value = float(value)
            return math.isfinite(float_value)
        except (ValueError, TypeError, OverflowError):
            return False
    
    
    
class RGBcolor(ctypes.Structure):
    _fields_ = [('r', ctypes.c_float), ('g', ctypes.c_float), ('b', ctypes.c_float)]

    def __repr__(self) -> str:
        return f'RGBcolor({self.r}, {self.g}, {self.b})'
    
    def __str__(self) -> str:
        return f'RGBcolor({self.r}, {self.g}, {self.b})'
    
    def __init__(self, r:float=0, g:float=0, b:float=0):
        # Validate color components are finite and in range [0,1]
        self._validate_color_component(r, 'r')
        self._validate_color_component(g, 'g')
        self._validate_color_component(b, 'b')
        
        self.r = float(r)
        self.g = float(g)
        self.b = float(b)

    def from_list(self, input_list:List[float]):
        self.r = input_list[0]
        self.g = input_list[1]
        self.b = input_list[2]

    def to_list(self) -> List[float]:
        return [self.r, self.g, self.b]
    
    @staticmethod
    def _is_finite_numeric(value) -> bool:
        """Check if value is a finite number (not NaN or inf)."""
        try:
            float_value = float(value)
            return math.isfinite(float_value)
        except (ValueError, TypeError, OverflowError):
            return False
    
    def _validate_color_component(self, value, component_name):
        """Validate a color component is finite and in range [0,1]."""
        if not self._is_finite_numeric(value):
            raise ValueError(f"RGBcolor.{component_name} must be a finite number, "
                           f"got {type(value).__name__}: {value}. "
                           f"Color components must be finite values between 0 and 1.")
        
        if not (0.0 <= value <= 1.0):
            raise ValueError(f"RGBcolor.{component_name}={value} is outside valid range [0,1]. "
                           f"Color components must be normalized values between 0 and 1.")

    
    
    
class RGBAcolor(ctypes.Structure):
    _fields_ = [('r', ctypes.c_float), ('g', ctypes.c_float), ('b', ctypes.c_float), ('a', ctypes.c_float)]

    def __repr__(self) -> str:
        return f'RGBAcolor({self.r}, {self.g}, {self.b}, {self.a})'
    
    def __str__(self) -> str:
        return f'RGBAcolor({self.r}, {self.g}, {self.b}, {self.a})'
    
    def __init__(self, r:float=0, g:float=0, b:float=0, a:float=0):
        # Validate color components are finite and in range [0,1]
        self._validate_color_component(r, 'r')
        self._validate_color_component(g, 'g')
        self._validate_color_component(b, 'b')
        self._validate_color_component(a, 'a')
        
        self.r = float(r)
        self.g = float(g)
        self.b = float(b)
        self.a = float(a)

    def from_list(self, input_list:List[float]):
        self.r = input_list[0]
        self.g = input_list[1]
        self.b = input_list[2]
        self.a = input_list[3]
    
    def to_list(self) -> List[float]:
        return [self.r, self.g, self.b, self.a]
    
    @staticmethod
    def _is_finite_numeric(value) -> bool:
        """Check if value is a finite number (not NaN or inf)."""
        try:
            float_value = float(value)
            return math.isfinite(float_value)
        except (ValueError, TypeError, OverflowError):
            return False
    
    def _validate_color_component(self, value, component_name):
        """Validate a color component is finite and in range [0,1]."""
        if not self._is_finite_numeric(value):
            raise ValueError(f"RGBAcolor.{component_name} must be a finite number, "
                           f"got {type(value).__name__}: {value}. "
                           f"Color components must be finite values between 0 and 1.")
        
        if not (0.0 <= value <= 1.0):
            raise ValueError(f"RGBAcolor.{component_name}={value} is outside valid range [0,1]. "
                           f"Color components must be normalized values between 0 and 1.")
    
    
    
class SphericalCoord(ctypes.Structure):
    _fields_ = [
        ('radius', ctypes.c_float),
        ('elevation', ctypes.c_float),
        ('zenith', ctypes.c_float),
        ('azimuth', ctypes.c_float)
    ]

    def __repr__(self) -> str:
        return f'SphericalCoord({self.radius}, {self.elevation}, {self.zenith}, {self.azimuth})'
    
    def __str__(self) -> str:
        return f'SphericalCoord({self.radius}, {self.elevation}, {self.zenith}, {self.azimuth})'
    
    def __init__(self, radius:float=1, elevation:float=0, azimuth:float=0):
        """
        Initialize SphericalCoord matching C++ constructor.
        
        Args:
            radius: Radius (default: 1)
            elevation: Elevation angle in radians (default: 0)  
            azimuth: Azimuthal angle in radians (default: 0)
            
        Note: zenith is automatically computed as (π/2 - elevation) to match C++ behavior
        """
        # Validate inputs
        if not self._is_finite_numeric(radius) or radius <= 0:
            raise ValueError(f"SphericalCoord.radius must be a positive finite number, "
                           f"got {type(radius).__name__}: {radius}. "
                           f"Radius must be greater than 0.")
        
        if not self._is_finite_numeric(elevation):
            raise ValueError(f"SphericalCoord.elevation must be a finite number, "
                           f"got {type(elevation).__name__}: {elevation}. "
                           f"Elevation angle must be finite (not NaN or infinity).")
        
        if not self._is_finite_numeric(azimuth):
            raise ValueError(f"SphericalCoord.azimuth must be a finite number, "
                           f"got {type(azimuth).__name__}: {azimuth}. "
                           f"Azimuth angle must be finite (not NaN or infinity).")
        
        self.radius = float(radius)
        self.elevation = float(elevation)
        self.zenith = 0.5 * math.pi - elevation  # zenith = π/2 - elevation (matches C++)
        self.azimuth = float(azimuth)

    def from_list(self, input_list:List[float]):
        self.radius = input_list[0]
        self.elevation = input_list[1]
        self.zenith = input_list[2]
        self.azimuth = input_list[3]

    def to_list(self) -> List[float]:
        return [self.radius, self.elevation, self.zenith, self.azimuth]
    
    @staticmethod
    def _is_finite_numeric(value) -> bool:
        """Check if value is a finite number (not NaN or inf)."""
        try:
            float_value = float(value)
            return math.isfinite(float_value)
        except (ValueError, TypeError, OverflowError):
            return False
    

# Factory functions to match C++ API
def make_int2(x: int, y: int) -> int2:
    """Make an int2 from two integers"""
    return int2(x, y)

def make_SphericalCoord(elevation_radians: float, azimuth_radians: float) -> SphericalCoord:
    """
    Make a SphericalCoord by specifying elevation and azimuth (C++ API compatibility).
    
    Args:
        elevation_radians: Elevation angle in radians
        azimuth_radians: Azimuthal angle in radians
        
    Returns:
        SphericalCoord with radius=1, and automatically computed zenith
    """
    return SphericalCoord(radius=1, elevation=elevation_radians, azimuth=azimuth_radians)

def make_int3(x: int, y: int, z: int) -> int3:
    """Make an int3 from three integers"""
    return int3(x, y, z)

def make_int4(x: int, y: int, z: int, w: int) -> int4:
    """Make an int4 from four integers"""  
    return int4(x, y, z, w)

def make_vec2(x: float, y: float) -> vec2:
    """Make a vec2 from two floats"""
    return vec2(x, y)

def make_vec3(x: float, y: float, z: float) -> vec3:
    """Make a vec3 from three floats"""
    return vec3(x, y, z)

def make_vec4(x: float, y: float, z: float, w: float) -> vec4:
    """Make a vec4 from four floats"""
    return vec4(x, y, z, w)

def make_RGBcolor(r: float, g: float, b: float) -> RGBcolor:
    """Make an RGBcolor from three floats"""
    return RGBcolor(r, g, b)

def make_RGBAcolor(r: float, g: float, b: float, a: float) -> RGBAcolor:
    """Make an RGBAcolor from four floats"""
    return RGBAcolor(r, g, b, a)


class Time(ctypes.Structure):
    """Helios Time structure for representing time values."""
    _fields_ = [('second', ctypes.c_int32), ('minute', ctypes.c_int32), ('hour', ctypes.c_int32)]

    def __repr__(self) -> str:
        return f'Time({self.hour:02d}:{self.minute:02d}:{self.second:02d})'
    
    def __str__(self) -> str:
        return f'{self.hour:02d}:{self.minute:02d}:{self.second:02d}'
    
    def __init__(self, hour: int = 0, minute: int = 0, second: int = 0):
        """
        Initialize a Time object.
        
        Args:
            hour: Hour (0-23)
            minute: Minute (0-59)
            second: Second (0-59)
        """
        # Validate inputs
        if not isinstance(hour, int):
            raise ValueError(f"Time.hour must be an integer, got {type(hour).__name__}: {hour}")
        if not isinstance(minute, int):
            raise ValueError(f"Time.minute must be an integer, got {type(minute).__name__}: {minute}")
        if not isinstance(second, int):
            raise ValueError(f"Time.second must be an integer, got {type(second).__name__}: {second}")
        
        if hour < 0 or hour > 23:
            raise ValueError(f"Time.hour must be between 0 and 23, got: {hour}")
        if minute < 0 or minute > 59:
            raise ValueError(f"Time.minute must be between 0 and 59, got: {minute}")
        if second < 0 or second > 59:
            raise ValueError(f"Time.second must be between 0 and 59, got: {second}")
        
        self.hour = hour
        self.minute = minute  
        self.second = second

    def from_list(self, input_list: List[int]):
        """Initialize from a list [hour, minute, second]"""
        if len(input_list) < 3:
            raise ValueError("Time.from_list requires a list with at least 3 elements [hour, minute, second]")
        self.hour = input_list[0]
        self.minute = input_list[1]
        self.second = input_list[2]

    def to_list(self) -> List[int]:
        """Convert to list [hour, minute, second]"""
        return [self.hour, self.minute, self.second]

    def __eq__(self, other) -> bool:
        """Check equality with another Time object"""
        if not isinstance(other, Time):
            return False
        return (self.hour == other.hour and 
                self.minute == other.minute and 
                self.second == other.second)

    def __ne__(self, other) -> bool:
        """Check inequality with another Time object"""
        return not self.__eq__(other)


class Date(ctypes.Structure):
    """Helios Date structure for representing date values."""
    _fields_ = [('day', ctypes.c_int32), ('month', ctypes.c_int32), ('year', ctypes.c_int32)]

    def __repr__(self) -> str:
        return f'Date({self.year}-{self.month:02d}-{self.day:02d})'
    
    def __str__(self) -> str:
        return f'{self.year}-{self.month:02d}-{self.day:02d}'
    
    def __init__(self, year: int = 2023, month: int = 1, day: int = 1):
        """
        Initialize a Date object.
        
        Args:
            year: Year (1900-3000)
            month: Month (1-12)
            day: Day (1-31)
        """
        # Validate inputs
        if not isinstance(year, int):
            raise ValueError(f"Date.year must be an integer, got {type(year).__name__}: {year}")
        if not isinstance(month, int):
            raise ValueError(f"Date.month must be an integer, got {type(month).__name__}: {month}")
        if not isinstance(day, int):
            raise ValueError(f"Date.day must be an integer, got {type(day).__name__}: {day}")
        
        if year < 1900 or year > 3000:
            raise ValueError(f"Date.year must be between 1900 and 3000, got: {year}")
        if month < 1 or month > 12:
            raise ValueError(f"Date.month must be between 1 and 12, got: {month}")
        if day < 1 or day > 31:
            raise ValueError(f"Date.day must be between 1 and 31, got: {day}")
        
        self.year = year
        self.month = month
        self.day = day

    def from_list(self, input_list: List[int]):
        """Initialize from a list [year, month, day]"""
        if len(input_list) < 3:
            raise ValueError("Date.from_list requires a list with at least 3 elements [year, month, day]")
        self.year = input_list[0]
        self.month = input_list[1]
        self.day = input_list[2]

    def to_list(self) -> List[int]:
        """Convert to list [year, month, day]"""
        return [self.year, self.month, self.day]

    def __eq__(self, other) -> bool:
        """Check equality with another Date object"""
        if not isinstance(other, Date):
            return False
        return (self.year == other.year and 
                self.month == other.month and 
                self.day == other.day)

    def __ne__(self, other) -> bool:
        """Check inequality with another Date object"""
        return not self.__eq__(other)


def make_Time(hour: int, minute: int, second: int) -> Time:
    """Make a Time from hour, minute, second"""
    return Time(hour, minute, second)

def make_Date(year: int, month: int, day: int) -> Date:
    """Make a Date from year, month, day"""
    return Date(year, month, day)

# Removed duplicate make_SphericalCoord function - keeping only the 2-parameter version above
