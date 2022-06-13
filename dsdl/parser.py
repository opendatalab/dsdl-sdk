import click
import yaml


def label_field_generator(raw):
    if not raw.startswith("Label"):
        return ""
    raw = raw.replace("Label[", "").replace("]", "")
    param_list = raw.split(",")
    valid_param_list = []
    for param in param_list:
        parts = param.split("=")
        if len(parts) != 2:
            continue
        if parts[0] == "dom" and parts[1].isidentifier():
            valid_param_list.append(f"{parts[0]}={parts[1]}")
    return "LabelField(" + ",".join(valid_param_list) + ")"


def field_generator(raw_field_type: str) -> str:
    if raw_field_type in ["Image", "Bool", "Num", "Int", "Str", "Coord"]:
        return raw_field_type + "Field()"
    if raw_field_type.startswith("Label"):
        return label_field_generator(raw_field_type)
    raise "Unknown field"


@click.command()
@click.option(
    "-y",
    "--yaml",
    "dsdl_yaml",
    type=str,
    required=True,
)
def parse(dsdl_yaml):
    with open(dsdl_yaml, "r") as f:
        desc = yaml.load(f, Loader=yaml.SafeLoader)

    output_file = dsdl_yaml.replace(".yaml", ".py")
    with open(output_file, "w") as of:
        print("from dsdl.types import *\nfrom enum import Enum\n\n", file=of)
        for define in desc["defs"].items():
            define_name = define[0]
            define_type = define[1]["$def"]
            if not define_name.isidentifier():
                continue

            if define_type == "struct":
                print(f"class {define_name}(Struct):", file=of)
                for raw_field in define[1]["$fields"].items():
                    if not raw_field[0].isidentifier():
                        continue
                    print(
                        f"""    {raw_field[0]} = {field_generator(raw_field[1])}""",
                        file=of,
                    )
                print("\n", file=of)

            if define_type == "class_domain":
                print(f"class {define_name}(Enum):", file=of)
                for class_name in define[1]["classes"]:
                    if not class_name.isidentifier():
                        continue
                    print(f'''    {class_name.upper()} = "{class_name}"''', file=of)
                print("\n", file=of)
