from dataclasses import dataclass, field
from typing import Dict, Any, Optional

from luxai.magpie.frames import DictFrame

@dataclass
class LedColorFrame(DictFrame):
    """
    RGBA LED color frame.
    """

    value: Dict[str, Any] = field(
        default_factory=lambda: {"r": 0, "g": 0, "b": 0, "a": 1}
    )

    # ----------------------------------------------------------------------
    # Custom initializer supporting LedColorFrame(r=255, g=128, ...)
    # ----------------------------------------------------------------------
    def __init__(
        self,
        *,
        r: Optional[float] = None,
        g: Optional[float] = None,
        b: Optional[float] = None,
        a: Optional[float] = None,
        value: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        """
        If 'value' is given, use it directly.
        Otherwise, construct a dict from r/g/b/a.
        """
        if value is None:
            value = {
                "r": float(r) if r is not None else 0.0,
                "g": float(g) if g is not None else 0.0,
                "b": float(b) if b is not None else 0.0,
                "a": float(a) if a is not None else 1.0,
            }

        # Call DictFrame initializer
        super().__init__(value=value, **kwargs)

    # ----------------------------------------------------------------------
    # Accessors
    # ----------------------------------------------------------------------
    @property
    def r(self) -> float: return float(self.value["r"])

    @r.setter
    def r(self, v: float): self.value["r"] = float(v)

    @property
    def g(self) -> float: return float(self.value["g"])

    @g.setter
    def g(self, v: float): self.value["g"] = float(v)

    @property
    def b(self) -> float: return float(self.value["b"])

    @b.setter
    def b(self, v: float): self.value["b"] = float(v)

    @property
    def a(self) -> float: return float(self.value["a"])

    @a.setter
    def a(self, v: float): self.value["a"] = float(v)

    # ----------------------------------------------------------------------
    def set(self, **kwargs):
        """Update channels selectively (r=..., g=..., etc.)."""
        for k, v in kwargs.items():
            if k in self.value:
                self.value[k] = float(v)

    # ----------------------------------------------------------------------
    def as_tuple(self):
        return (self.r, self.g, self.b, self.a)

    def __str__(self):
        return f"{self.name}#{self.gid}:{self.id}(r={self.r}, g={self.g}, b={self.b}, a={self.a})"
