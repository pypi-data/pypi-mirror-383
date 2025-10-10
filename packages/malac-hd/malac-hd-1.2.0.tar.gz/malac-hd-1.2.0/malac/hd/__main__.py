import argparse
import os
import time
import sys
import shutil
import importlib.util
import json
# dynamic import by init_class()!

if __package__ != "malac.hd":
    current = os.path.dirname(os.path.realpath(__file__))
    parent = os.path.dirname(current)
    sys.path.append(parent)
import malac.hd


description_text = """You are using the MApping LAnguage Compiler for Health Data, short MaLaC-HD.
We differentiate between two modes, CONVERTING and TRANSFORMING.
The CONVERSION is done by compiling a given mapping to python code, that itself can be run with its own argument handling for TRANSFORMING input files.
Additionally, the TRANSFORMATION can also be be done by MaLaC-HD directly after CONVERSION, i.e. for direct testing purposes."""
auto_detect = "the ressource type is detected by its root node inside the xml"


def init_argparse(script) -> argparse.ArgumentParser:
    if script:
        prog = "malac-hd"
    else:
        prog = "python -m malac.hd"
    parser = argparse.ArgumentParser(prog=prog, description=description_text, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        "-m", "--mapping", help='the mapping file path, the conversion/mapping rule language is detected by file ending, right now FML maps (*.map), FHIR R4 (*.4.fhir.xml) StructureMaps and ConceptMaps can be given as mappings', required=True
    )
    parser.add_argument(
        "-co", "--convert_output", help='the conversion python file path, if not given, saved in the working directory with the map-file name', required=False
    )
    
    parser.add_argument(
        "-ti", "--transform_input", help='the transformation input file path, '+auto_detect, required=False
    )
    parser.add_argument(
        "-to", "--transform_output", help='the transformation output file path, '+auto_detect, required=False
    )

    parser.add_argument(
        "-mod", "--models", nargs='+', help='use these model packages', required=False
    )

    # TODO check if we should make the translate params somehow avaiable from the outside
    """parser.add_argument(
        "-tlc", "--translate_code", help='the translate code', required=False
    )
    parser.add_argument(
        "-tlp", "--translate_params", help='the translate params', required=False
    )"""
    
    parser.add_argument(
        "-s", "--silent", action="store_true", help='do not print the converted python mapping to console', required=False
    )

    return parser


def get_standard_by_fileending(filename, list_classes, return_ending_not_class=False):
    for iclass in list_classes:
        if filename.endswith(iclass):
            if return_ending_not_class:
                return iclass
            return list_classes[iclass]
    raise BaseException("The classification could not be detected from the file name. \n %s" % description_text)


def main(script) -> None:
    start = time.time()
    version = malac.hd.version()
    print("____________________ MaLaC-HD "+version+" started ____________________")

    parser = init_argparse(script)
    args = parser.parse_args()

    print("Converting "+args.mapping)

    module_name = get_standard_by_fileending(args.mapping, malac.hd.list_m_modules)
    module_split = ["malac", "hd", "core"] + module_name.split(".")
    m_module = getattr(__import__(".".join(module_split[:-1]), fromlist=[module_split[-1]]), module_split[-1])

    for module_name in args.models or []:
        module_split = module_name.split(".")
        if len(module_split) > 1:
            mod = getattr(__import__(".".join(module_split[:-1]), fromlist=[module_split[-1]]), module_split[-1])
        else:
            mod = __import__(module_name)
        malac.hd.list_i_o_modules.update(mod.list_i_o_modules)

    if args.mapping.endswith(".json"):
        with open(args.mapping, 'r', newline='', encoding='utf-8') as f:
            map = m_module.utils.parse_json(m_module.supermod, json.load(f))
    else:
        map = m_module.parse(args.mapping, silence=True)

    try:
        py_code = map.convert(silent=args.silent, source=getattr(map, "temp_filename", None) or os.path.abspath(args.mapping))

        # as similar as possible to https://www.hl7.org/fhir/resource-operation-convert.html
        if args.convert_output:
            if os.path.isfile(args.convert_output):
                os.remove(args.convert_output)
            with open(args.convert_output, 'w', newline='', encoding='utf-8') as f:
                f.write(py_code)

        # as similar as possible to https://www.hl7.org/fhir/structuremap-operation-transform.html
        # if args.output is full file path, then do the transform itself we just created
        if args.transform_output and args.transform_input:
            print("")
            spec = importlib.util.spec_from_loader("mapping", loader=None)
            module = importlib.util.module_from_spec(spec)
            exec(py_code, module.__dict__)
            module.transform(args.transform_input, args.transform_output)
            print("")

        # TODO Translate params handling
        """if args.translate_code:
            print("")
            spec = importlib.util.spec_from_loader("mapping", loader=None)
            module = importlib.util.module_from_spec(spec)
            exec(py_code, module.__dict__)
            module.translate(code=args.translate_code)
            print("")"""

        print("altogether in "+str(round(time.time()-start,3))+" seconds.")
        print("____________________ MaLaC-HD "+version+" ended ____________________")
    finally:
        if map and getattr(map, "temp_filename", None):
            shutil.rmtree(os.path.dirname(map.temp_filename))


def script_main():
    main(script=True)

if __name__ == '__main__':
    main(script=False)
