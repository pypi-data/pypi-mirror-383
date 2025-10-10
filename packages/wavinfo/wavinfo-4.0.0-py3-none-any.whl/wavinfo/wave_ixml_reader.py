from lxml import etree as ET
import io
# from collections import namedtuple
from typing import Optional
from enum import IntEnum
from typing import NamedTuple


class IXMLTrack(NamedTuple):
    channel_index: int
    interleave_index: int
    name: str
    function: str


class SteinbergMetadata:
    """
    Vendor-specific Steinberg metadata.
    """

    class AudioSpeakerArrangement(IntEnum):
        """
        Steinberg speaker format enumeration.
        """
        MONO = 0
        STEREO = 1
        LRC = 10
        LRCS = 14
        QUAD = 15
        CINE_50 = 18
        CINE_51 = 19
        CINE_60 = 20
        CINE_61 = 22
        CINE_70 = 25
        CINE_71 = 27
        SDDS_70 = 24
        SDDS_71 = 26
        MUSIC_60 = 21  # ??
        MUSIC_61 = 23
        ATMOS_712 = 33
        ATMOS_504 = 35
        ATMOS_514 = 36
        ATMOS_714 = 44
        ATMOS_702 = 48
        ATMOS_716 = 51
        ATMOS_914 = 53
        ATMOS_916 = 55
        AMB_1ORDER = 45
        AMB_2ORDER = 46
        AMB_3ORDER = 47
        AURO_10_0 = 37
        AURO_10_1 = 38
        AURO_11_0 = 39
        AURO_11_1 = 40
        AURO_13_0 = 41
        AURO_13_1 = 42

    Steinberg_xpath = "./STEINBERG"

    @classmethod
    def present(cls, xml: ET.ElementTree) -> bool:
        """
        Test if `xml` has Steinberg metadata.
        :param xml: an iXML ElementTree
        """
        x = xml.find(cls.Steinberg_xpath)
        return x is not None

    def __init__(self, xml: ET.ElementTree) -> None:
        """
        Parse Steinberg iXML data.
        :param xml: The entire iXML Tree
        """
        self.parsed = xml.find(self.Steinberg_xpath)

    @property
    def audio_speaker_arrangement(self) -> Optional[AudioSpeakerArrangement]:
        """
        `AudioSpeakerArrangement` property
        """
        val = self.parsed.find(
            "./ATTR_LIST/ATTR[NAME = 'AudioSpeakerArrangement']/VALUE")
        if val is not None:
            return type(self).AudioSpeakerArrangement(int(val.text))

    @property
    def sample_format_size(self) -> Optional[int]:
        """
        AudioSampleFormatSize
        """
        val = self.parsed.find(
            "./ATTR_LIST/ATTR[NAME = 'AudioSampleFormatSize']/VALUE")
        if val is not None:
            return int(val.text)

    @property
    def media_company(self) -> Optional[str]:
        """
        MediaCompany
        """
        val = self.parsed.find(
            "./ATTR_LIST/ATTR[NAME = 'MediaCompany']/VALUE")
        if val is not None:
            return val.text

    @property
    def media_drop_frames(self) -> Optional[bool]:
        """
        MediaDropFrames
        """
        val = self.parsed.find(
            "./ATTR_LIST/ATTR[NAME = 'MediaDropFrames']/VALUE")
        if val is not None:
            return val.text == "1"

    @property
    def media_duration(self) -> Optional[float]:
        """
        MediaDuration
        """
        val = self.parsed.find(
            "./ATTR_LIST/ATTR[NAME = 'MediaDuration']/VALUE")
        if val is not None:
            return float(val.text)

    @property
    def media_start_time(self) -> Optional[float]:
        """
        MediaStartTime
        """
        pass

    @property
    def media_track_title(self) -> Optional[str]:
        """
        MediaTrackTitle
        """
        pass

    @property
    def program_name(self) -> Optional[str]:
        """
        ProgramName
        """
        pass

    @property
    def program_version(self) -> Optional[str]:
        """
        ProgramVersion
        """
        pass


class WavIXMLFormat:
    """
    iXML recorder metadata.
    """

    def __init__(self, xml):
        """
        Parse iXML.
        :param xml: A bytes-like object containing the iXML payload.
        """
        self.source = xml
        xml_bytes = io.BytesIO(xml)
        parser = ET.XMLParser(recover=True)
        self.parsed: ET.ElementTree = ET.parse(xml_bytes, parser=parser)

    def _get_text_value(self, xpath) -> Optional[str]:
        e = self.parsed.find("./" + xpath)
        if e is not None:
            return e.text
        else:
            return None

    def xml_str(self) -> str:
        return ET.tostring(self.parsed).decode("utf-8")

    @property
    def raw_xml(self) -> ET.ElementTree:
        """
        The root entity of the iXML document.
        """
        return self.parsed

    @property
    def track_list(self):
        """
        A description of each track.

        :yields: `IXMLTrack` for each track.
        """
        for track in self.parsed.find("./TRACK_LIST").iter():
            if track.tag == 'TRACK':
                yield IXMLTrack(
                    channel_index=track.xpath('string(CHANNEL_INDEX/text())'),
                    interleave_index=track.xpath(
                        'string(INTERLEAVE_INDEX/text())'),
                    name=track.xpath('string(NAME/text())'),
                    function=track.xpath('string(FUNCTION/text())')
                )

    @property
    def project(self) -> Optional[str]:
        """
        The project/film name entered for the recording.
        """
        return self._get_text_value("PROJECT")

    @property
    def scene(self) -> Optional[str]:
        """
        Scene/slate.
        """
        return self._get_text_value("SCENE")

    @property
    def take(self) -> Optional[str]:
        """
        Take number.
        """
        return self._get_text_value("TAKE")

    @property
    def tape(self) -> Optional[str]:
        """
        Tape name.
        """
        return self._get_text_value("TAPE")

    @property
    def family_uid(self) -> Optional[str]:
        """
        The globally-unique ID for this file family. This may be in the format
        of a GUID, or an EBU Rec 9 source identifier, or some other dumb
        number.
        """
        return self._get_text_value("FILE_SET/FAMILY_UID")

    @property
    def family_name(self) -> Optional[str]:
        """
        The name of this file's file family.
        """
        return self._get_text_value("FILE_SET/FAMILY_NAME")

    @property
    def steinberg(self) -> Optional[SteinbergMetadata]:
        """
        Steinberg vendor iXML metadata if present.
        """
        if SteinbergMetadata.present(self.raw_xml):
            return SteinbergMetadata(self.raw_xml)
        else:
            return None

    def to_dict(self):
        return dict(
            track_list=list(map(lambda x: x._asdict(), self.track_list)),
            project=self.project, scene=self.scene, take=self.take,
            tape=self.tape, family_uid=self.family_uid,
            family_name=self.family_name)
