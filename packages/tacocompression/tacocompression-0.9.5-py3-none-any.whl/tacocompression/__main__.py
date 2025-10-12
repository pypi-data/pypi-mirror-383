import argparse
from compression import compress, decompress
from input_output import load_inputs, save_output


parser = argparse.ArgumentParser()
parser.add_argument("-m", "--mode", type=str, help="c for compress or d for decompress", choices=["c", "d"], default="c")
parser.add_argument("-o", "--output", help="Specify the output directory")
parser.add_argument("-p", "--pairing_function", type=str, default="rosenberg",
                    help="The pairing function to use to combined two values in the time series.",
                    choices=["rosenberg", "szudzik", "cantor"])
parser.add_argument("-d", "--decimals", type=int, default=1,
                    help="Precision of the reconstruction, i.e., number of decimals recoverable during decompression. Only used in compression.")
parser.add_argument("--header", action="store_true",
                    help="Whether the input file(s) contain a header. Only used in compression.")
kw_args, inputs = parser.parse_known_args()
data, file_names = load_inputs(inputs, kw_args.header)
if kw_args.mode == "c":
    representations = compress(data, kw_args.pairing_function, kw_args.decimals)
    file_names = ["compressed_" + fn for fn in file_names]
    save_output(representations, file_names, kw_args.output)
else:
    time_series = decompress(data, kw_args.pairing_function)
    file_names = [fn[11:] if fn.startswith("compressed_") else fn for fn in file_names]
    save_output(time_series, file_names, kw_args.output)
