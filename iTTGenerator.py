import xml.etree.ElementTree as ET
from xml.dom import minidom

class ITTGenerator:
    def __init__(self, frame_rate=24, frame_rate_multiplier="1000 1001", drop_mode="nonDrop", lang="en"):
        self.frame_rate = frame_rate
        self.frame_rate_multiplier = frame_rate_multiplier
        self.drop_mode = drop_mode
        self.lang = lang
        self.caption_region = "bottom"
        self.caption_style = "normal"
        self.styles = {
            "color": "white",
            "fontFamily": "sansSerif",
            "fontSize": "100%",
            "fontStyle": "normal",
            "fontWeight": "normal"
        }

    def set_frame_rate(self, frame_rate, frame_rate_multiplier="1000 1001"):
        self.frame_rate = frame_rate
        self.frame_rate_multiplier = frame_rate_multiplier

    def set_caption_region(self, region_id, display_align="after", extent="100% 15%", origin="0% 85%", writing_mode="lrtb"):
        self.caption_region = region_id
        self.display_align = display_align
        self.extent = extent
        self.origin = origin
        self.writing_mode = writing_mode

    def set_text_style(self, color=None, fontFamily=None, fontSize=None, fontStyle=None, fontWeight=None):
        if color:
            self.styles["color"] = color
        if fontFamily:
            self.styles["fontFamily"] = fontFamily
        if fontSize:
            self.styles["fontSize"] = fontSize
        if fontStyle:
            self.styles["fontStyle"] = fontStyle
        if fontWeight:
            self.styles["fontWeight"] = fontWeight

    def generate_xml(self):
        # Define namespaces
        ET.register_namespace('', "http://www.w3.org/ns/ttml")
        root = ET.Element("tt", {
            "xmlns": "http://www.w3.org/ns/ttml",
            "xmlns:vt": "http://namespace.itunes.apple.com/itt/ttml-extension#vertical",
            "xmlns:ttp": "http://www.w3.org/ns/ttml#parameter",
            "xmlns:ittp": "http://www.w3.org/ns/ttml/profile/imsc1#parameter",
            "xmlns:tt_feature": "http://www.w3.org/ns/ttml/feature/",
            "xmlns:ebutts": "urn:ebu:tt:style",
            "xmlns:tts": "http://www.w3.org/ns/ttml#styling",
            "xmlns:tt_extension": "http://www.w3.org/ns/ttml/extension/",
            "xmlns:tt_profile": "http://www.w3.org/ns/ttml/profile/",
            "xmlns:ttm": "http://www.w3.org/ns/ttml#metadata",
            "xmlns:ry": "http://namespace.itunes.apple.com/itt/ttml-extension#ruby",
            "xmlns:itts": "http://www.w3.org/ns/ttml/profile/imsc1#styling",
            "xmlns:tt": "http://www.w3.org/ns/ttml",
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "xml:lang": self.lang,
            "ttp:dropMode": self.drop_mode,
            "ttp:frameRate": str(self.frame_rate),
            "ttp:frameRateMultiplier": self.frame_rate_multiplier,
            "ttp:timeBase": "smpte"
        })

        head = ET.SubElement(root, "head")
        styling = ET.SubElement(head, "styling")
        style_attributes = {
            "xml:id": self.caption_style,
            "tts:color": self.styles["color"],
            "tts:fontFamily": self.styles["fontFamily"],
            "tts:fontSize": self.styles["fontSize"],
            "tts:fontStyle": self.styles["fontStyle"],
            "tts:fontWeight": self.styles["fontWeight"]
        }
        ET.SubElement(styling, "style", style_attributes)
        
        layout = ET.SubElement(head, "layout")
        ET.SubElement(layout, "region", {
            "xml:id": self.caption_region,
            "tts:displayAlign": self.display_align,
            "tts:extent": self.extent,
            "tts:origin": self.origin,
            "tts:writingMode": self.writing_mode
        })

        body = ET.SubElement(root, "body", {"region": self.caption_region, "style": self.caption_style})
        div = ET.SubElement(body, "div")

        # Prettify and return the generated XML
        xml_str = ET.tostring(root, 'utf-8')
        reparsed = minidom.parseString(xml_str)
        return reparsed.toprettyxml(indent="  ")
    
    def write_xml(self, file_path):
        with open(file_path, "w") as f:
            f.write(self.generate_xml())

# Example usage:
itt_gen = ITTGenerator()
itt_gen.set_frame_rate(30, "1000 1000")
itt_gen.set_caption_region("bottom", "after", "80% 10%", "10% 90%", "lrtb")
itt_gen.set_text_style(color="white", fontFamily="Arial", fontSize="150%", fontStyle="normal", fontWeight="bold")
xml_content = itt_gen.generate_xml()
itt_gen.write_xml("example.itt")
print(xml_content)
