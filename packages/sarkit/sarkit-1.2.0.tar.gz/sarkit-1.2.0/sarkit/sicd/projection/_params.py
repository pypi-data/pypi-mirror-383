"""Classes that encapsulate collections of parameters to support SICD projections."""

import dataclasses
import functools
from typing import Optional, Self, TypeAlias

import lxml.etree
import numpy as np
import numpy.polynomial.polynomial as npp

import sarkit.sicd._xml as ss_xml

# TODO: encouraged to migrate to type statements instead of TypeAlias in python 3.12
CoaPosVelsLike: TypeAlias = "CoaPosVelsMono | CoaPosVelsBi"
ProjectionSetsLike: TypeAlias = "ProjectionSetsMono | ProjectionSetsBi"


def _get_rcv_poly(xmlhelp):
    """Per Metadata Parameter List: If multiple receive APCs are used, compute the centroid."""
    chan_indices = [
        xmlhelp.load_elem(el)
        for el in xmlhelp.element_tree.findall(
            "{*}ImageFormation/{*}RcvChanProc/{*}ChanIndex"
        )
    ]
    rcv_apc_indices = [
        xmlhelp.load(
            f"{{*}}RadarCollection/{{*}}RcvChannels/{{*}}ChanParameters[@index='{c}']/{{*}}RcvAPCIndex"
        )
        for c in chan_indices
    ]
    rcv_apc_polys = [
        xmlhelp.load(f"{{*}}Position/{{*}}RcvAPC/{{*}}RcvAPCPoly[@index='{c}']")
        for c in rcv_apc_indices
        if c is not None
    ]
    if rcv_apc_polys:
        return functools.reduce(npp.polyadd, rcv_apc_polys) / len(rcv_apc_polys)
    return None


@dataclasses.dataclass(kw_only=True)
class MetadataParams:
    """Parameters from IPDD Metadata Parameter List."""

    # To help link the code to the SICD Image Projections Description Document, the variable names
    # used here are intended to closely match the names used in the document.  As a result they
    # may not adhere to the PEP8 convention used elsewhere in the code.

    Collect_Type: str
    # Scene Center Point Parameters
    SCP: np.ndarray
    SCP_Lat: float
    SCP_Lon: float
    SCP_HAE: float
    SCP_Row: float
    SCP_Col: float
    # SCP COA Parameters
    t_SCP_COA: float  # noqa N815
    ARP_SCP_COA: np.ndarray
    VARP_SCP_COA: np.ndarray
    SideOfTrack: str
    GRAZ_SCP_COA: float
    # SCP COA Parameters - Only provided for Collect_Type = BISTATIC
    tx_SCP_COA: Optional[float] = None  # noqa N815
    Xmt_SCP_COA: Optional[np.ndarray] = None
    VXmt_SCP_COA: Optional[np.ndarray] = None
    tr_SCP_COA: Optional[float] = None  # noqa N815
    Rcv_SCP_COA: Optional[np.ndarray] = None
    VRcv_SCP_COA: Optional[np.ndarray] = None
    # Image Data Parameters
    NumRows: int
    NumCols: int
    FirstRow: int
    FirstCol: int
    # Image Grid Parameters
    Grid_Type: str
    uRow: np.ndarray  # noqa N815
    uCol: np.ndarray  # noqa N815
    Row_SS: float
    Col_SS: float
    cT_COA: np.ndarray  # noqa N815
    # ARP Position Parameters
    ARP_Poly: np.ndarray
    Xmt_Poly: Optional[np.ndarray] = None
    Rcv_Poly: Optional[np.ndarray] = None
    GRP_Poly: Optional[np.ndarray] = None
    # Image Formation Parameters
    IFA: str
    # Range & Azimuth Compression Parameters
    AzSF: Optional[float] = None
    # Polar Format Algorithm Parameters
    cPA: Optional[np.ndarray] = None  # noqa N815
    cKSF: Optional[np.ndarray] = None  # noqa N815
    # Range Migration Algorithm INCA Parameters
    cT_CA: Optional[np.ndarray] = None  # noqa N815
    R_CA_SCP: Optional[float] = None
    cDRSF: Optional[np.ndarray] = None  # noqa N815

    @property
    def LOOK(self):  # noqa N802
        """+1 if SideOfTrack = L, -1 if SideOfTrack = R"""
        if self.SideOfTrack == "L":
            return +1
        if self.SideOfTrack == "R":
            return -1
        raise ValueError(
            f"Unrecognized SideOfTrack: {self.SideOfTrack}; must be L or R"
        )

    def is_monostatic(self) -> bool:
        """Returns True if MONOSTATIC, False if BISTATIC. Otherwise raises exception."""
        Collect_Type = self.Collect_Type  # noqa N802
        if Collect_Type == "MONOSTATIC":
            return True
        if Collect_Type == "BISTATIC":
            return False
        raise ValueError(f"{Collect_Type=} must be MONOSTATIC or BISTATIC")

    def is_bistatic(self) -> bool:
        """Returns True if BISTATIC, False if MONOSTATIC. Otherwise raises exception."""
        return not self.is_monostatic()

    @classmethod
    def from_xml(cls, sicd_xmltree: lxml.etree.ElementTree) -> Self:
        """Extract relevant metadata parameters from SICD XML as described in SICD IPDD.

        Parameters
        ----------
        sicd_xmltree : lxml.etree.ElementTree
            SICD XML metadata.

        Returns
        -------
        MetadataParams
            The metadata parameter list object initialized with values from the XML.

        """
        xmlhelp = ss_xml.XmlHelper(sicd_xmltree)
        return cls(
            **{
                "Collect_Type": xmlhelp.load("{*}CollectionInfo/{*}CollectType")
                or "MONOSTATIC",
                # Scene Center Point Parameters
                "SCP": xmlhelp.load("{*}GeoData/{*}SCP/{*}ECF"),
                "SCP_Lat": xmlhelp.load("{*}GeoData/{*}SCP/{*}LLH/{*}Lat"),
                "SCP_Lon": xmlhelp.load("{*}GeoData/{*}SCP/{*}LLH/{*}Lon"),
                "SCP_HAE": xmlhelp.load("{*}GeoData/{*}SCP/{*}LLH/{*}HAE"),
                "SCP_Row": xmlhelp.load("{*}ImageData/{*}SCPPixel/{*}Row"),
                "SCP_Col": xmlhelp.load("{*}ImageData/{*}SCPPixel/{*}Col"),
                # SCP COA Parameters
                "t_SCP_COA": xmlhelp.load("{*}SCPCOA/{*}SCPTime"),
                "ARP_SCP_COA": xmlhelp.load("{*}SCPCOA/{*}ARPPos"),
                "VARP_SCP_COA": xmlhelp.load("{*}SCPCOA/{*}ARPVel"),
                "SideOfTrack": xmlhelp.load("{*}SCPCOA/{*}SideOfTrack"),
                "GRAZ_SCP_COA": xmlhelp.load("{*}SCPCOA/{*}GrazeAng"),
                # SCP COA Parameters - Only provided for Collect_Type = BISTATIC
                "tx_SCP_COA": xmlhelp.load(
                    "{*}SCPCOA/{*}Bistatic/{*}TxPlatform/{*}Time"
                ),
                "Xmt_SCP_COA": xmlhelp.load(
                    "{*}SCPCOA/{*}Bistatic/{*}TxPlatform/{*}Pos"
                ),
                "VXmt_SCP_COA": xmlhelp.load(
                    "{*}SCPCOA/{*}Bistatic/{*}TxPlatform/{*}Vel"
                ),
                "tr_SCP_COA": xmlhelp.load(
                    "{*}SCPCOA/{*}Bistatic/{*}RcvPlatform/{*}Time"
                ),
                "Rcv_SCP_COA": xmlhelp.load(
                    "{*}SCPCOA/{*}Bistatic/{*}RcvPlatform/{*}Pos"
                ),
                "VRcv_SCP_COA": xmlhelp.load(
                    "{*}SCPCOA/{*}Bistatic/{*}RcvPlatform/{*}Vel"
                ),
                # Image Data Parameters
                "NumRows": xmlhelp.load("{*}ImageData/{*}NumRows"),
                "NumCols": xmlhelp.load("{*}ImageData/{*}NumCols"),
                "FirstRow": xmlhelp.load("{*}ImageData/{*}FirstRow"),
                "FirstCol": xmlhelp.load("{*}ImageData/{*}FirstCol"),
                # Image Grid Parameters
                "Grid_Type": xmlhelp.load("{*}Grid/{*}Type"),
                "uRow": xmlhelp.load("{*}Grid/{*}Row/{*}UVectECF"),
                "uCol": xmlhelp.load("{*}Grid/{*}Col/{*}UVectECF"),
                "Row_SS": xmlhelp.load("{*}Grid/{*}Row/{*}SS"),
                "Col_SS": xmlhelp.load("{*}Grid/{*}Col/{*}SS"),
                "cT_COA": xmlhelp.load("{*}Grid/{*}TimeCOAPoly"),
                # ARP Position Parameters
                "ARP_Poly": xmlhelp.load("{*}Position/{*}ARPPoly"),
                "Xmt_Poly": xmlhelp.load("{*}Position/{*}TxAPCPoly"),
                "Rcv_Poly": _get_rcv_poly(xmlhelp),
                "GRP_Poly": xmlhelp.load("{*}Position/{*}GRPPoly"),
                # Image Formation Parameters
                "IFA": xmlhelp.load("{*}ImageFormation/{*}ImageFormAlgo"),
                # Range & Azimuth Compression Parameters
                "AzSF": xmlhelp.load("{*}RgAzComp/{*}AzSF"),
                # Polar Format Algorithm Parameters
                "cPA": xmlhelp.load("{*}PFA/{*}PolarAngPoly"),
                "cKSF": xmlhelp.load("{*}PFA/{*}SpatialFreqSFPoly"),
                # Range Migration Algorithm INCA Parameters
                "cT_CA": xmlhelp.load("{*}RMA/{*}INCA/{*}TimeCAPoly"),
                "R_CA_SCP": xmlhelp.load("{*}RMA/{*}INCA/{*}R_CA_SCP"),
                "cDRSF": xmlhelp.load("{*}RMA/{*}INCA/{*}DRateSFPoly"),
            }
        )


@dataclasses.dataclass(kw_only=True)
class CoaPosVelsMono:
    """Ensemble of monostatic Center Of Aperture sensor positions and velocities.

    Constructor arguments are array_like and broadcast into the attributes.

    Attributes
    ----------
    ARP_COA, VARP_COA : (..., 3) ndarray
        Aperture reference point positions and velocities with ECEF X, Y, Z components (m) in last dimension
    """

    # To help link the code to the SICD Image Projections Description Document, the variable names
    # used here are intended to closely match the names used in the document.  As a result they
    # may not adhere to the PEP8 convention used elsewhere in the code.

    ARP_COA: np.ndarray
    VARP_COA: np.ndarray

    def __post_init__(self):
        self.ARP_COA, self.VARP_COA = np.broadcast_arrays(
            np.asarray(self.ARP_COA), np.asarray(self.VARP_COA)
        )


@dataclasses.dataclass(kw_only=True)
class CoaPosVelsBi:
    """Ensemble of bistatic Center Of Aperture sensor positions and velocities.

    Constructor arguments are array_like and broadcast into the attributes after an implicit, right-most dimension is
    added to `tx_COA` and `tr_COA`.
    The implicit dimension is subsequently removed.

    Attributes
    ----------
    GRP_COA : (..., 3) ndarray
        Ground reference points with ECEF X, Y, Z components (m) in last dimension
    tx_COA, tr_COA : (...) ndarray
        Transmit and receive times in seconds relative to collect start for computing bistatic geometry
    Xmt_COA, Rcv_COA : (..., 3) ndarray
        Transmit and receive APC positions with ECEF X, Y, Z components (m) in last dimension
    VXmt_COA, VRcv_COA : (..., 3) ndarray
        Transmit and receive APC velocities with ECEF X, Y, Z components (m/s) in last dimension
    """

    # To help link the code to the SICD Image Projections Description Document, the variable names
    # used here are intended to closely match the names used in the document.  As a result they
    # may not adhere to the PEP8 convention used elsewhere in the code.

    GRP_COA: np.ndarray
    tx_COA: np.ndarray  # noqa N802
    tr_COA: np.ndarray  # noqa N802
    Xmt_COA: np.ndarray
    VXmt_COA: np.ndarray
    Rcv_COA: np.ndarray
    VRcv_COA: np.ndarray

    def __post_init__(self):
        (
            self.GRP_COA,
            self.tx_COA,
            self.tr_COA,
            self.Xmt_COA,
            self.VXmt_COA,
            self.Rcv_COA,
            self.VRcv_COA,
        ) = np.broadcast_arrays(
            np.asarray(self.GRP_COA),
            np.asarray(self.tx_COA)[..., np.newaxis],
            np.asarray(self.tr_COA)[..., np.newaxis],
            np.asarray(self.Xmt_COA),
            np.asarray(self.VXmt_COA),
            np.asarray(self.Rcv_COA),
            np.asarray(self.VRcv_COA),
        )
        self.tx_COA = self.tx_COA[..., 0]
        self.tr_COA = self.tr_COA[..., 0]


@dataclasses.dataclass(kw_only=True)
class ProjectionSetsMono:
    """Ensemble of monostatic Center of Aperture projection sets.

    For a selected image grid location, the COA projection set contains the parameters
    needed for computing precise image-to-scene projection.

    Constructor arguments are array_like and broadcast into the attributes after an implicit, right-most dimension is
    added to `t_COA`, `R_COA` and `Rdot_COA`.
    The implicit dimension is subsequently removed

    Attributes
    ----------
    t_COA : (...) ndarray
        Center of aperture times in seconds relative to collect start
    ARP_COA : (..., 3) ndarray
        Aperture reference point positions with ECEF X, Y, Z components (m) in last dimension
    VARP_COA : (..., 3) ndarray
        Aperture reference point velocities with ECEF X, Y, Z components (m/s) in last dimension
    R_COA, Rdot_COA : (...) ndarray
        Ranges (m) and range rates (m/s) relative to the ARP COA positions and velocities
    """

    # To help link the code to the SICD Image Projections Description Document, the variable names
    # used here are intended to closely match the names used in the document.  As a result they
    # may not adhere to the PEP8 convention used elsewhere in the code.

    t_COA: np.ndarray  # noqa N802
    ARP_COA: np.ndarray
    VARP_COA: np.ndarray
    R_COA: np.ndarray
    Rdot_COA: np.ndarray

    def __post_init__(self):
        (
            self.t_COA,
            self.ARP_COA,
            self.VARP_COA,
            self.R_COA,
            self.Rdot_COA,
        ) = np.broadcast_arrays(
            np.asarray(self.t_COA)[..., np.newaxis],
            np.asarray(self.ARP_COA),
            np.asarray(self.VARP_COA),
            np.asarray(self.R_COA)[..., np.newaxis],
            np.asarray(self.Rdot_COA)[..., np.newaxis],
        )
        self.t_COA = self.t_COA[..., 0]
        self.R_COA = self.R_COA[..., 0]
        self.Rdot_COA = self.Rdot_COA[..., 0]


@dataclasses.dataclass(kw_only=True)
class ProjectionSetsBi:
    """Ensemble of bistatic Center of Aperture projection sets.

    For a selected image grid location, the COA projection set contains the parameters
    needed for computing precise image-to-scene projection.

    Constructor arguments are array_like and broadcast into the attributes after an implicit, right-most dimension is
    added to `t_COA`, `tx_COA`, `tr_COA`, `R_Avg_COA` and `Rdot_Avg_COA`.
    The implicit dimension is subsequently removed

    Attributes
    ----------
    t_COA : (...) ndarray
        Center of aperture times in seconds relative to collect start
    tx_COA, tr_COA : (...) ndarray
        Transmit and receive times in seconds relative to collect start for computing bistatic geometry
    Xmt_COA, Rcv_COA : (..., 3) ndarray
        Transmit and receive APC positions with ECEF X, Y, Z components (m) in last dimension
    VXmt_COA, VRcv_COA : (..., 3) ndarray
        Transmit and receive APC velocities with ECEF X, Y, Z components (m/s) in last dimension
    R_Avg_COA, Rdot_Avg_COA : (...) ndarray
        Range (m) and range rate (m/s) averages relative to the APC COA positions and velocities
    """

    # To help link the code to the SICD Image Projections Description Document, the variable names
    # used here are intended to closely match the names used in the document.  As a result they
    # may not adhere to the PEP8 convention used elsewhere in the code.

    t_COA: np.ndarray  # noqa N802
    tx_COA: np.ndarray  # noqa N802
    tr_COA: np.ndarray  # noqa N802
    Xmt_COA: np.ndarray
    VXmt_COA: np.ndarray
    Rcv_COA: np.ndarray
    VRcv_COA: np.ndarray
    R_Avg_COA: np.ndarray
    Rdot_Avg_COA: np.ndarray

    def __post_init__(self):
        (
            self.t_COA,
            self.tx_COA,
            self.tr_COA,
            self.Xmt_COA,
            self.VXmt_COA,
            self.Rcv_COA,
            self.VRcv_COA,
            self.R_Avg_COA,
            self.Rdot_Avg_COA,
        ) = np.broadcast_arrays(
            np.asarray(self.t_COA)[..., np.newaxis],
            np.asarray(self.tx_COA)[..., np.newaxis],
            np.asarray(self.tr_COA)[..., np.newaxis],
            np.asarray(self.Xmt_COA),
            np.asarray(self.VXmt_COA),
            np.asarray(self.Rcv_COA),
            np.asarray(self.VRcv_COA),
            np.asarray(self.R_Avg_COA)[..., np.newaxis],
            np.asarray(self.Rdot_Avg_COA)[..., np.newaxis],
        )
        self.t_COA = self.t_COA[..., 0]
        self.tx_COA = self.tx_COA[..., 0]
        self.tr_COA = self.tr_COA[..., 0]
        self.R_Avg_COA = self.R_Avg_COA[..., 0]
        self.Rdot_Avg_COA = self.Rdot_Avg_COA[..., 0]


@dataclasses.dataclass(kw_only=True)
class ScenePointRRdotParams:
    """
    Ensemble of range and range rate parameters for a collection of scene points (PT).

    Constructor arguments are array_like and broadcast into the attributes after an implicit, right-most dimension is
    added to `R_Avg_PT` and `Rdot_Avg_PT`.
    The implicit dimension is subsequently removed

    Attributes
    ----------
    R_Avg_PT : (...) ndarray
        Average range (m)
    Rdot_Avg_PT : (...) ndarray
        Average range rate (m/s)
    bP_PT : (..., 3) ndarray
        Bistatic pointing vector with ECEF X, Y, Z components (m) in last dimension
    bPDot_PT : (..., 3) ndarray
        Derivative w.r.t. time of bistatic pointing vector
    uSPN_PT: (..., 3) ndarray
        Bistatic slant plant unit normal with ECEF X, Y, Z components (m) in last dimension
    """

    # To help link the code to the SICD Image Projections Description Document, the variable names
    # used here are intended to closely match the names used in the document.  As a result they
    # may not adhere to the PEP8 convention used elsewhere in the code.

    R_Avg_PT: np.ndarray
    Rdot_Avg_PT: np.ndarray
    bP_PT: np.ndarray  # noqa N802
    bPDot_PT: np.ndarray  # noqa N802
    uSPN_PT: np.ndarray  # noqa N802

    def __post_init__(self):
        (
            self.R_Avg_PT,
            self.Rdot_Avg_PT,
            self.bP_PT,
            self.bPDot_PT,
            self.uSPN_PT,
        ) = np.broadcast_arrays(
            np.asarray(self.R_Avg_PT)[..., np.newaxis],
            np.asarray(self.Rdot_Avg_PT)[..., np.newaxis],
            np.asarray(self.bP_PT),
            np.asarray(self.bPDot_PT),
            np.asarray(self.uSPN_PT),
        )
        self.R_Avg_PT = self.R_Avg_PT[..., 0]
        self.Rdot_Avg_PT = self.Rdot_Avg_PT[..., 0]


@dataclasses.dataclass(kw_only=True)
class ScenePointGpXyParams:
    """
    Ensemble of scene point ground plane XY parameters for a collection of scene points (PT).

    Attributes
    ----------
    uGX, uGY : (..., 3) ndarray
        Unit vectors that lie in the ground plane with ECEF (WGS 84 cartesian) X, Y, Z
        components in meters in the last dimension.
    M_RRdot_GPXY : (..., 2, 2) ndarray
        Sensitivity matrix to compute changes in average R/Rdot due to changes in GX and GY.
    M_GPXY_RRdot : (..., 2, 2) ndarray
        Sensitivity matrix to compute changes in GX and GY from change in average R/Rdot.
    """

    # To help link the code to the SICD Image Projections Description Document, the variable names
    # used here are intended to closely match the names used in the document.  As a result they
    # may not adhere to the PEP8 convention used elsewhere in the code.

    uGX: np.ndarray  # noqa N802
    uGY: np.ndarray  # noqa N802
    M_RRdot_GPXY: np.ndarray
    M_GPXY_RRdot: np.ndarray


@dataclasses.dataclass(kw_only=True)
class AdjustableParameterOffsets:
    """Parameters from IPDD Adjustable Parameter Offsets List."""

    # To help link the code to the SICD Image Projections Description Document, the variable names
    # used here are intended to closely match the names used in the document.  As a result they
    # may not adhere to the PEP8 convention used elsewhere in the code.

    delta_tx_SCP_COA: float  # noqa N815
    delta_tr_SCP_COA: float  # noqa N815
    # Monostatic Adjustable Offsets
    delta_ARP_SCP_COA: Optional[np.ndarray] = None  # noqa N815
    delta_VARP: Optional[np.ndarray] = None  # noqa N815
    # Bistatic Adjustable Offsets
    delta_Xmt_SCP_COA: Optional[np.ndarray] = None  # noqa N815
    delta_VXmt: Optional[np.ndarray] = None  # noqa N815
    f_Clk_X_SF: Optional[float] = None  # noqa N815
    delta_Rcv_SCP_COA: Optional[np.ndarray] = None  # noqa N815
    delta_VRcv: Optional[np.ndarray] = None  # noqa N815
    f_Clk_R_SF: Optional[float] = None  # noqa N815

    @classmethod
    def exists(cls, sicd_xmltree: lxml.etree.ElementTree) -> bool:
        """Determine if the APO nodes exist in the SICD XML.

        Parameters
        ----------
        sicd_xmltree : lxml.etree.ElementTree
            SICD XML metadata.

        Returns
        -------
        bool

        """
        if (
            sicd_xmltree.find("{*}ErrorStatistics/{*}AdjustableParameterOffsets")
            is not None
        ):
            return True
        if (
            sicd_xmltree.find(
                "{*}ErrorStatistics/{*}BistaticAdjustableParameterOffsets"
            )
            is not None
        ):
            return True
        return False

    @classmethod
    def from_xml(cls, sicd_xmltree: lxml.etree.ElementTree) -> Self:
        """Extract relevant adjustable parameter offsets from SICD XML as described in SICD IPDD.

        Parameters
        ----------
        sicd_xmltree : lxml.etree.ElementTree
            SICD XML metadata.

        Returns
        -------
        AdjustableParameterOffsets
            The adjustable parameter offsets list object initialized with values from the XML.

        """
        xmlhelp = ss_xml.XmlHelper(sicd_xmltree)
        return cls(
            **{
                "delta_tx_SCP_COA": xmlhelp.load(
                    "{*}ErrorStatistics/{*}AdjustableParameterOffsets/{*}TxTimeSCPCOA"
                )
                or xmlhelp.load(
                    "{*}ErrorStatistics/{*}BistaticAdjustableParameterOffsets/{*}TxPlatform/{*}TimeSCPCOA"
                ),
                "delta_tr_SCP_COA": xmlhelp.load(
                    "{*}ErrorStatistics/{*}AdjustableParameterOffsets/{*}RcvTimeSCPCOA"
                )
                or xmlhelp.load(
                    "{*}ErrorStatistics/{*}BistaticAdjustableParameterOffsets/{*}RcvPlatform/{*}TimeSCPCOA"
                ),
                # Optional Monostatic Adjustable Offsets
                "delta_ARP_SCP_COA": xmlhelp.load(
                    "{*}ErrorStatistics/{*}AdjustableParameterOffsets/{*}ARPPosSCPCOA"
                ),
                "delta_VARP": xmlhelp.load(
                    "{*}ErrorStatistics/{*}AdjustableParameterOffsets/{*}ARPVel"
                ),
                # Optional Bistatic Adjustable Offsets
                "delta_Xmt_SCP_COA": xmlhelp.load(
                    "{*}ErrorStatistics/{*}BistaticAdjustableParameterOffsets/{*}TxPlatform/{*}APCPosSCPCOA"
                ),
                "delta_VXmt": xmlhelp.load(
                    "{*}ErrorStatistics/{*}BistaticAdjustableParameterOffsets/{*}TxPlatform/{*}APCVel"
                ),
                "f_Clk_X_SF": xmlhelp.load(
                    "{*}ErrorStatistics/{*}BistaticAdjustableParameterOffsets/{*}TxPlatform/{*}ClockFreqSF"
                ),
                "delta_Rcv_SCP_COA": xmlhelp.load(
                    "{*}ErrorStatistics/{*}BistaticAdjustableParameterOffsets/{*}RcvPlatform/{*}APCPosSCPCOA"
                ),
                "delta_VRcv": xmlhelp.load(
                    "{*}ErrorStatistics/{*}BistaticAdjustableParameterOffsets/{*}RcvPlatform/{*}APCVel"
                ),
                "f_Clk_R_SF": xmlhelp.load(
                    "{*}ErrorStatistics/{*}BistaticAdjustableParameterOffsets/{*}RcvPlatform/{*}ClockFreqSF"
                ),
            }
        )
