from pathlib import Path


def load_inputs(locations: list[str], header: bool) -> tuple[list[list[float]], list[str]]:
    """
    Retrieves the input to process. During compression, the input time series. During decompression, the compressed
    representations.

    :param locations: An absolute or relative path (measured from the current working directory) to the input files.
    :param header: Whether the files to load include headers.
    :return: A pair with the list of time series at first position and a list of file names at second.
    """
    time_series = []
    file_names = []
    for location in locations:
        path = Path(location)
        if not path.is_absolute():
            path = Path.cwd() / location
            assert path.exists()
        if path.is_file():
            file_names.append(path.name)
            time_series.append(load_file(path, header))
        elif path.is_dir():
            for entry in path.iterdir():
                if entry.is_file() and entry.name.endswith(".csv"):
                    file_names.append(entry.name)
                    time_series.append(load_file(entry, header))
    return time_series, file_names


def load_file(path: Path, header: bool) -> list[float|int]:
    """
    Loads an individual file containing a sequence of numbers (integers or floats), one number per line.

    :param path: Absolute path of the file to load.
    :param header: Whether the file to load includes a header.
    :return: The sequence of numbers.
    """
    with open(path, "r") as f:
        if header:
            f.readline()
        data_str = f.readlines()
    data_str = [s.strip('\n').strip() for s in data_str]
    data = [float(s) if '.' in s else int(s) for s in data_str]
    return data


def save_output(data: list[list[float|int]], filenames: list[str], output_location: str):
    """
    Writes the processed sequences to files, one sequence per file. These sequences are either representations
    (compression) or time series (decompression).

    :param data: The sequences to save.
    :param filenames: Names of the output files to save.
    :param output_location: Target directory.
    """
    output_dir = prepare_path(output_location)
    for t, fn in zip(data, filenames):
        with open(output_dir / fn, 'w') as f:
            for value in t:
                if isinstance(value, list):
                    f.write(str(value)[1:-1].replace(' ', '') + "\n")
                else:
                    f.write(f"{value}\n")


def prepare_path(location: str) -> Path:
    directory = Path(location)
    if not (directory.is_absolute()):
        directory = Path.cwd() / directory
    assert directory.exists()
    return directory
