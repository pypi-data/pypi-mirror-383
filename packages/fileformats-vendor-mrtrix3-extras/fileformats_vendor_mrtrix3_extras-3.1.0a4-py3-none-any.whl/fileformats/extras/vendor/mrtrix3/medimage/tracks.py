import time
import struct
import math
from pathlib import Path
import typing as ty
from fileformats.core import FileSet, SampleFileGenerator, extra_implementation
from fileformats.vendor.mrtrix3.medimage import Tracks


@extra_implementation(FileSet.generate_sample_data)
def generate_tracks_sample_data(
    tracks: Tracks,
    generator: SampleFileGenerator,
) -> ty.List[Path]:
    """Generate a tracks file with a single straight track of length 10"""
    fspath = generator.dest_dir / "tracks.tck"
    timestamp = str(time.time() * 1e9 + time.process_time_ns())
    contents = f"""mrtrix tracks
datatype: Float32BE
timestamp: {timestamp}
count: 1
total_count: 1
file: . """
    byte_contents = contents.encode()
    offset = len(byte_contents) + math.ceil(math.log10(len(byte_contents))) + 5
    byte_contents += str(offset).encode() + b"\nEND\n"
    for i in range(10):
        ib = i.to_bytes(32, "big")
        byte_contents += ib + ib + ib
    nan_bytes = struct.pack("!d", float("nan"))
    inf_bytes = struct.pack("!d", float("inf"))
    byte_contents += nan_bytes + nan_bytes + nan_bytes
    byte_contents += inf_bytes + inf_bytes + inf_bytes
    with open(fspath, "wb") as f:
        f.write(byte_contents)
    return [fspath]
