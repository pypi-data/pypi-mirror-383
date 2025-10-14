"""
Convert fdb data with metadata from disk into a qube as fast as possible

Example running this in parallel ls test_scripts/data/*.zst | xargs -n 1 -P 10 python test_scripts/fdb_dump_parser.py
"""

import subprocess
import sys
from pathlib import Path
import time

from qubed import Qube

if len(sys.argv) != 2:
    print("Usage: python fdb_deblaster.py INPUT_PATH")
    sys.exit()

assert sys.argv[1].endswith(".zst")

p = Path(sys.argv[1])  # Compressed file
decompressed = p.parent / f"{p.stem}"  # decompressed file
output = p.parent / Path(f"monthly/{p.stem[:-5]}.json")

if output.exists():
    sys.exit()

if not decompressed.exists():
    result = subprocess.run(["zstd", "--decompress", p], stdout=subprocess.PIPE)

print(f"{output} does not exist")
print(decompressed)

qube = Qube.empty()

one_count = 0
two_count = 0

level_one = {}
level_two = {}
path_meta = {}

level_one_qube = Qube.empty()
level_two_qube = Qube.empty()
level_three_qube = Qube.empty()

t0 = time.time()
with decompressed.open() as f:
    for i, line in enumerate(f.readlines()):
        level, key, *metadata = line.strip().split(" ")

        if level == "0":
            level_one_qube |= level_two_qube
            level_two_qube = Qube.empty()

            level_one = dict(item.split("=", 1) for item in key.split(","))
            one_count += 1
            print(f"{one_count}th level one key, {i / (time.time() - t0):.0f} leaves/s")

        elif level == "1":
            level_two_qube |= level_three_qube.add_metadata(path_meta)
            level_three_qube = Qube.empty()

            level_two = dict(item.split("=", 1) for item in key.split(","))
            path_meta = dict(item.split("=", 1) for item in metadata[0].split(","))
            two_count += 1
            print(f"{two_count}th level two key, {i / (time.time() - t0):.0f} leaves/s")

        elif level == "2":
            level_three = dict(item.split("=", 1) for item in key.split(","))
            offset_length_meta = dict(
                item.split("=", 1) for item in metadata[0].split(",")
            )

            keys = level_one | level_two | level_three

            keys.pop("year", None)
            keys.pop("month", None)

            key_order = key_order = [
                "class",
                "dataset",
                "stream",
                "activity",
                "resolution",
                "expver",
                "experiment",
                "generation",
                "model",
                "realization",
                "type",
                "date",
                "time",
                "number",
                "datetime",
                "levtype",
                "levelist",
                "step",
                "param",
            ]
            keys = {k: keys[k] for k in key_order if k in keys}

            offset_length_meta["length"] = int(offset_length_meta["length"])
            offset_length_meta["offset"] = int(offset_length_meta["offset"])

            level_three_qube |= Qube.from_datacube(keys).add_metadata(
                offset_length_meta
            )

    level_two_qube |= level_three_qube.add_metadata(path_meta)
    level_one_qube |= level_two_qube

print(level_one_qube)
level_one_qube.save(str(output))

if decompressed.exists():
    print(f"Removing {decompressed}")
    decompressed.unlink()

print("ENDED SCRIPT")
