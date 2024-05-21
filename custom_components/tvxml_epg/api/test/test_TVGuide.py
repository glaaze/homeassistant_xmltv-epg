import pytest
from datetime import datetime
import xml.etree.ElementTree as ET

from ..model import TVChannel, TVProgram, TVGuide


def test_from_xml():
    """Test TVGuide.from_xml method with valid input."""
    xml = ET.fromstring("""
<tv generator-info-name="tvxml_epg" generator-info-url="http://example.com">
  <channel id="CH1">
    <display-name>Channel 1</display-name>
    </channel>
    <programme start="20200101010000 +0000" stop="20200101020000 +0000">
        <title>Program 1</title>
        <desc>Description 1</desc>
    </programme>
</tv>
""")

    guide = TVGuide.from_xml(xml)

    assert guide is not None
    assert guide.generator_name == 'tvxml_epg'
    assert guide.generator_url == 'http://example.com'

    assert len(guide.channels) == 1
    assert len(guide.programs) == 1

    # cross-linked ?
    assert guide.programs[0].channel is not None
    assert guide.programs[0].channel.id == 'CH1'
