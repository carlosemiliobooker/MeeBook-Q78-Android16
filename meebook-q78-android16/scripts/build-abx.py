#!/usr/bin/env python3
"""Generate the Q78 calibration file in Android Binary XML v0 (ABX).

Protocol derived from AOSP BinaryXmlSerializer and FastDataOutput:
https://android.googlesource.com/platform/frameworks/base/+/b6ad99651e5f/core/java/com/android/internal/util/BinaryXmlSerializer.java
https://android.googlesource.com/platform/prebuilts/fullsdk/sources/+/refs/heads/androidx-constraintlayout-release/android-35/com/android/modules/utils/FastDataOutput.java

The input file is limited to simple XML: names, string attributes, and text.
"""
import argparse
import pathlib
import struct
import xml.etree.ElementTree as ET


def encode_xml(root: ET.Element) -> bytes:
    output = bytearray(b"ABX\x00\x10")  # ABX v0, START_DOCUMENT | TYPE_NULL
    interned = {}

    def utf(value: str) -> bytes:
        # For this file, all strings are ASCII; AOSP's modified-UTF8 matches UTF8.
        if not value.isascii():
            raise ValueError("This generator intentionally supports ASCII only")
        raw = value.encode("ascii")
        if len(raw) > 65535:
            raise ValueError("ABX string too long")
        return struct.pack(">H", len(raw)) + raw

    def intern(value: str) -> bytes:
        if value in interned:
            return struct.pack(">H", interned[value])
        index = len(interned)
        if index >= 65535:
            raise ValueError("Too many interned names")
        interned[value] = index
        return b"\xff\xff" + utf(value)

    def element(node: ET.Element) -> None:
        output.append(0x32)  # START_TAG | TYPE_STRING_INTERNED
        output.extend(intern(node.tag))
        for name, value in node.attrib.items():
            output.append(0x2F)  # ATTRIBUTE | TYPE_STRING
            output.extend(intern(name))
            output.extend(utf(value))
        if node.text and node.text.strip():
            output.append(0x24)  # TEXT | TYPE_STRING
            output.extend(utf(node.text.strip()))
        for child in node:
            element(child)
        output.append(0x33)  # END_TAG | TYPE_STRING_INTERNED
        output.extend(intern(node.tag))

    element(root)
    output.append(0x11)  # END_DOCUMENT | TYPE_NULL
    return bytes(output)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("xml", type=pathlib.Path)
    parser.add_argument("output", type=pathlib.Path)
    args = parser.parse_args()
    document = ET.parse(args.xml).getroot()
    assert document.tag == "input-manager-state", "Unexpected root tag"
    result = encode_xml(document)
    if len(result) != 322:
        raise RuntimeError(f"Expected Q78 calibration ABX length 322; got {len(result)}")
    args.output.write_bytes(result)
    print(f"Wrote {len(result)}-byte ABX: {args.output}")


if __name__ == "__main__":
    main()
