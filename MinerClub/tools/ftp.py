from pathlib import Path


def write_file(host, filename, text):
    with host.open(filename, 'w') as f:
        f.write(text)


def read_file(host, filename):
    with host.open(filename) as f:
        return f.read()


def copy_dir(host, from_, to):
    from_ = Path(from_)
    to = Path(to)
    for root, dirs, files in host.walk(from_.as_posix()):
        root = Path(root)
        dest_dir = to / root.relative_to(from_.parent) # if from_ is a subdirectory, no point having full path there

        if not dest_dir.exists():
            dest_dir.mkdir()

        for file in files:
            source = root / file
            destination = dest_dir / file
            host.download(source.as_posix(), destination.as_posix())


