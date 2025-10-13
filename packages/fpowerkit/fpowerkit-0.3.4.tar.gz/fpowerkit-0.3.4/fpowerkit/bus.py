import math
from typing import Optional
from xml.etree.ElementTree import Element
from feasytools import TimeFunc
from .utils import *


class Bus:
    Pd: TimeFunc  # pu
    Qd: TimeFunc  # pu
    ShadowPrice: FloatVar  # Shadow price of generators on this bus，$/pu power
    Lat: NFloat
    Lon: NFloat

    def __init__(self, id: str, pd_pu: FloatLike, qd_pu: FloatLike, lat: NFloat = None, lon: NFloat = None, 
            v_pu: NFloat = None, min_v_pu: float = 0.0, max_v_pu: float = float('inf'), theta: NFloat = None):
        '''
        Initialize
            id: Bus ID
            pd_pu: Active power demand, pu
            qd_pu: Reactive power demand, pu
            lat: Latitude of the bus
            lon: Longitude of the bus
            v_pu: Voltage, pu. None for unfixed voltage
            min_v_pu: Minimal voltage, pu
            max_v_pu: Maximal voltage, pu
        '''
        self._id = id
        self._v = v_pu
        self._fixed_v = v_pu is not None
        self._minv = min_v_pu
        self._maxv = max_v_pu
        self.Pd = Float2Func(pd_pu)
        self.Qd = Float2Func(qd_pu)
        self.ShadowPrice = None
        self.Lat = lat
        self.Lon = lon
        self._t = theta
        self._fixed_t = self._t is not None

    def V_var(self, bank: VarBank):
        if self.FixedV:
            raise ValueError("Voltage is fixed, cannot create a variable for it.")
        return bank.fvar(f"{self.ID}_V", self, "_v", self.V, nonneg=True, lb=self.MinV, ub=self.MaxV)
    
    def V2_var(self, bank: VarBank):
        if self.FixedV:
            raise ValueError("Voltage is fixed, cannot create a variable for it.")
        v = self.V if self.V is not None else 1.0
        return bank.fvar(f"{self.ID}_V2", self, "_v", v**2, nonneg=True, 
            lb=self.MinV**2, ub=self.MaxV**2, reflect=lambda x: math.sqrt(x))
    
    def theta_var(self, bank: VarBank):
        if self.FixedTheta:
            raise ValueError("Voltage angle is fixed, cannot create a variable for it.")
        return bank.fvar(f"{self.ID}_theta", self, "_theta", self._t)
    
    @property
    def V(self) -> FloatVar:
        '''Voltage, pu'''
        return self._v
    @V.setter
    def V(self, v: float):
        self._v = v

    @property
    def theta(self) -> float:
        '''Voltage angle, rad'''
        return self._t if self._t is not None else 0.0
    @theta.setter
    def theta(self, t: float):
        self._t = t
    
    @property
    def V_cpx(self) -> Optional[complex]:
        if self._v is None or self._t is None: return None
        return self._v * math.cos(self._t) + 1j * self._v * math.sin(self._t)
    
    @property
    def FixedV(self) -> bool:
        '''Whether the voltage is fixed'''
        return self._fixed_v
    
    def fixV(self, v: float):
        '''Fix the voltage'''
        self._v = v
        self._fixed_v = True
    
    def unfixV(self):
        self._v = None
        self._fixed_v = False
    
    @property
    def FixedTheta(self) -> bool:
        '''Whether the voltage angle is fixed'''
        return self._fixed_t

    def fixTheta(self, theta: float):
        '''Fix the voltage angle'''
        self._t = theta
        self._fixed_t = True
    
    def unfixTheta(self):
        '''Unfix the voltage angle'''
        self._t = None
        self._fixed_t = False
    
    @property
    def ID(self) -> str:
        '''Name of the bus'''
        return self._id
    
    @property
    def MinV(self) -> float:
        '''Minimal voltage, pu'''
        return self._minv
    @MinV.setter
    def MinV(self, v: float):
        assert v >= 0 and v <= self._maxv, "MinV should be in [0, MaxV]"
        self._minv = v
    
    @property
    def MaxV(self) -> float:
        '''Maximal voltage, pu'''
        return self._maxv
    @MaxV.setter
    def MaxV(self, v: float):
        assert v >= self._minv, "MaxV should be no less than MinV"
        self._maxv = v
    
    def setVRange(self, min_v: float, max_v: float):
        assert 0 <= min_v <= max_v, "MinV should be in [0, MaxV]"
        self._minv = min_v
        self._maxv = max_v
    
    def __repr__(self):
        return f"Bus(id='{self.ID}', v_pu={self.V}, pd_pu={self.Pd}, qd_pu={self.Qd}, " + \
            f"lat={self.Lat}, lon={self.Lon}, min_v_pu={self.MinV}, max_v_pu={self.MaxV})"

    def __str__(self):
        return repr(self)
    
    def str_t(self, _t: int, /):
        return f"Bus(id='{self.ID}', v_pu={FVstr(self.V)}, pd_pu={self.Pd(_t)}, qd_pu={self.Qd(_t)}, " + \
            f"lat={self.Lat}, lon={self.Lon}, min_v_pu={self.MinV}, max_v_pu={self.MaxV})"

    @property
    def position(self) -> 'tuple[NFloat, NFloat]':
        '''Return the position of the bus, (lat, lon)'''
        return self.Lat, self.Lon
    
    @property
    def LonLat(self) -> 'tuple[NFloat, NFloat]':
        return self.Lon, self.Lat
    
    @staticmethod
    def fromXML(node: 'Element', Sb_MVA: float, Ub_kV: float):
        id = node.attrib["ID"]
        p = ReadFloatLike(node.find("Pd"), Sb_MVA, Ub_kV)
        q = ReadFloatLike(node.find("Qd"), Sb_MVA, Ub_kV)
        lat = node.attrib.get("Lat", None)
        if lat is not None: lat = float(lat)
        lon = node.attrib.get("Lon", None)
        if lon is not None: lon = float(lon)
        if "V" in node.attrib:
            v = ReadConst(node.attrib["V"], Sb_MVA, Ub_kV)
            minv = maxv = v
        else:
            minv = ReadConst(node.attrib.get("MinV",'0.8pu'), Sb_MVA, Ub_kV)
            maxv = ReadConst(node.attrib.get("MaxV",'1.2pu'), Sb_MVA, Ub_kV)
            v = None
        return Bus(id, p, q, lat, lon, v, minv, maxv)
    
    def toXMLNode(self, Ub_kV:Optional[float] = None,
            Sb_MVA:Optional[float] = None, Sb_kVA:Optional[float] = None) -> 'Element':
        e = Element("bus", {"ID": self.ID})
        if self.Lat is not None: e.attrib["Lat"] = f"{self.Lat:.6f}"
        if self.Lon is not None: e.attrib["Lon"] = f"{self.Lon:.6f}"
        if self.V is not None and self.FixedV:
            e.attrib["V"] = str(self.V * Ub_kV)+"kV" if Ub_kV else str(self.V)
        else:
            e.attrib["MinV"] = str(self.MinV * Ub_kV)+"kV" if Ub_kV else str(self.MinV)
            e.attrib["MaxV"] = str(self.MaxV * Ub_kV)+"kV" if Ub_kV else str(self.MaxV)
        if Sb_MVA is not None and Sb_kVA is not None:
            raise ValueError("Provide only ONE of Sb_MVA or Sb_kVA.")
        if Sb_MVA is not None:
            mul = Sb_MVA
            unit = ["MW", "Mvar"]
        elif Sb_kVA is not None:
            mul = Sb_kVA
            unit = ["kW", "kvar"]
        else:
            mul = 1
            unit = ["pu", "pu"]
        e.append(Func2Elem(self.Pd, "Pd", mul, unit[0]))
        e.append(Func2Elem(self.Qd, "Qd", mul, unit[1]))
        return e

__all__ = ["Bus"]