"""24-bit PCM WAV writer with an embedded 'smpl' chunk (root key + loop points).

Kontakt, Creator Tools and most samplers read the smpl chunk, so loops and root
keys travel with the files even if you map them by hand.
"""
import struct

import numpy as np


def _chunk(cid, payload):
    pad = b"\x00" if len(payload) % 2 else b""
    return cid + struct.pack("<I", len(payload)) + payload + pad


def write_wav24(path, audio, sr=44100, root=None, loop=None):
    """Write float audio (-1..1) as 24-bit PCM.

    audio: shape (n,) for mono or (n, 2) for stereo.
    root:  MIDI root key stored in the smpl chunk.
    loop:  (start, end_exclusive) in sample frames, or None.
    """
    a = np.asarray(audio, dtype=np.float64)
    if a.ndim == 1:
        a = a[:, None]
    channels = a.shape[1]
    frames = a.shape[0]

    # TPDF dither at 24-bit level, then quantise
    rng = np.random.default_rng(frames)
    lsb = 1.0 / 8388608.0
    dither = (rng.random(a.shape) - rng.random(a.shape)) * lsb
    q = np.clip(np.round((a + dither) * 8388607.0), -8388608, 8388607).astype(np.int32)
    raw = q.reshape(-1)
    b = np.empty((raw.size, 3), dtype=np.uint8)
    b[:, 0] = raw & 0xFF
    b[:, 1] = (raw >> 8) & 0xFF
    b[:, 2] = (raw >> 16) & 0xFF
    data = b.tobytes()

    block_align = channels * 3
    fmt = struct.pack("<HHIIHH", 1, channels, sr, sr * block_align, block_align, 24)

    chunks = [_chunk(b"fmt ", fmt)]
    if root is not None or loop is not None:
        loops = []
        if loop is not None:
            start, end = int(loop[0]), int(loop[1])
            # smpl loop end is inclusive
            loops.append(struct.pack("<IIIIII", 0, 0, start, end - 1, 0, 0))
        smpl = struct.pack(
            "<IIIIIIIII",
            0, 0,                                   # manufacturer, product
            int(round(1e9 / sr)),                   # sample period (ns)
            int(root if root is not None else 60),  # MIDI unity note
            0, 0, 0,                                # pitch fraction, SMPTE format/offset
            len(loops), 0,                          # loop count, sampler data
        ) + b"".join(loops)
        chunks.append(_chunk(b"smpl", smpl))
    chunks.append(_chunk(b"data", data))

    body = b"WAVE" + b"".join(chunks)
    with open(path, "wb") as f:
        f.write(b"RIFF" + struct.pack("<I", len(body)) + body)


def read_wav24(path):
    """Minimal reader used by the self-tests (24-bit PCM only)."""
    with open(path, "rb") as f:
        d = f.read()
    assert d[:4] == b"RIFF" and d[8:12] == b"WAVE"
    pos = 12
    info = {}
    while pos < len(d):
        cid = d[pos:pos + 4]
        size = struct.unpack("<I", d[pos + 4:pos + 8])[0]
        payload = d[pos + 8:pos + 8 + size]
        if cid == b"fmt ":
            _, ch, sr, _, _, bits = struct.unpack("<HHIIHH", payload[:16])
            info.update(channels=ch, sr=sr, bits=bits)
        elif cid == b"smpl":
            vals = struct.unpack("<IIIIIIIII", payload[:36])
            info["root"] = vals[3]
            if vals[7]:
                _, _, s, e, _, _ = struct.unpack("<IIIIII", payload[36:60])
                info["loop"] = (s, e + 1)
        elif cid == b"data":
            raw = np.frombuffer(payload, dtype=np.uint8).reshape(-1, 3).astype(np.int32)
            v = raw[:, 0] | (raw[:, 1] << 8) | (raw[:, 2] << 16)
            v = np.where(v >= 8388608, v - 16777216, v)
            info["audio"] = (v / 8388608.0).reshape(-1, info["channels"])
        pos += 8 + size + (size % 2)
    return info
