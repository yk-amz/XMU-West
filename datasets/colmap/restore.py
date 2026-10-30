"""Verify and restore the downloaded COLMAP ZIP archives using the repository manifest."""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import zipfile


class VolumesReader(io.RawIOBase):
    def __init__(self, paths):
        self.paths = paths
        self.sizes = [p.stat().st_size for p in paths]
        self.length = sum(self.sizes)
        self.pos = 0

    def readable(self):
        return True

    def seekable(self):
        return True

    def tell(self):
        return self.pos

    def seek(self, offset, whence=0):
        pos = offset if whence == 0 else self.pos + offset if whence == 1 else self.length + offset
        if pos < 0:
            raise ValueError('Negative seek')
        self.pos = pos
        return pos

    def read(self, size=-1):
        if size is None or size < 0:
            size = max(0, self.length - self.pos)
        chunks = []
        offset = self.pos
        for path, length in zip(self.paths, self.sizes):
            if offset >= length:
                offset -= length
                continue
            amount = min(size, length - offset)
            if amount <= 0:
                break
            with path.open('rb') as f:
                f.seek(offset)
                block = f.read(amount)
            chunks.append(block)
            self.pos += len(block)
            size -= len(block)
            offset = 0
        return b''.join(chunks)


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        while chunk := f.read(8 * 1024**2):
            h.update(chunk)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archives', type=Path, help='Directory containing all downloaded ZIP files')
    parser.add_argument('destination', type=Path, help='Directory in which to recreate Project')
    parser.add_argument('--metadata', type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    index = json.loads((args.metadata / 'archives.json').read_text(encoding='utf-8'))
    if index['status'] != 'complete':
        raise SystemExit('Backup is still incomplete; do not treat these archives as a complete copy.')
    for entry in index['archives']:
        archive_hash = hashlib.sha256()
        volumes = entry.get('volumes') or [{'name':entry['name'], 'bytes':entry['archive_bytes'], 'sha256':entry['sha256']}]
        for volume in volumes:
            path = args.archives / volume['name']
            if not path.is_file() or path.stat().st_size != volume['bytes']:
                raise SystemExit(f'Missing or wrong-size volume: {path}')
            volume_hash = hashlib.sha256()
            with path.open('rb') as f:
                while chunk := f.read(8 * 1024**2):
                    archive_hash.update(chunk)
                    volume_hash.update(chunk)
            if volume_hash.hexdigest() != volume['sha256']:
                raise SystemExit(f'Volume checksum mismatch: {path}')
        if archive_hash.hexdigest() != entry['sha256']:
            raise SystemExit(f'Archive checksum mismatch: {entry["name"]}')
    args.destination.mkdir(parents=True, exist_ok=True)
    for entry in index['archives']:
        volumes = entry.get('volumes') or [{'name':entry['name']}]
        paths = [args.archives / v['name'] for v in volumes]
        with VolumesReader(paths) as reader, zipfile.ZipFile(reader) as z:
            for info in z.infolist():
                part = PurePosixPath(info.filename)
                if part.is_absolute() or '..' in part.parts or not part.parts or part.parts[0] != 'Project':
                    raise SystemExit(f'Unsafe archive member: {info.filename}')
                target = args.destination.joinpath(*part.parts)
                target.resolve().relative_to(args.destination.resolve())
                if target.exists():
                    raise SystemExit(f'Destination already exists: {target}; choose an empty destination.')
            z.extractall(args.destination)
        print(f'Restored {entry["name"]}', flush=True)
    manifests = sorted((args.metadata / 'manifest').glob('*.csv'))
    if not manifests:
        manifests = [args.metadata / 'manifest.csv']
    rows = []
    for manifest in manifests:
        with manifest.open(encoding='utf-8-sig', newline='') as f:
            rows.extend(csv.DictReader(f))
    for row in rows:
        path = args.destination / 'Project' / row['path']
        if path.stat().st_size != int(row['bytes']) or digest(path) != row['sha256']:
            raise SystemExit(f'Restored file checksum mismatch: {path}')
    print(f'Verified all {len(rows):,} restored files.')


if __name__ == '__main__':
    main()
