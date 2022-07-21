from dsdl.tools import DetectionParse, Generation
from argparse import ArgumentParser
import os


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("-i", "--dataset_info", type=str, required=True,
                        help="the path of dataset_info.json of tunas 0.3 format dataset.")
    parser.add_argument("-a", "--ann_info", type=str, required=True,
                        help="the path of annotation.json of tunas 0.3 format dataset.")
    parser.add_argument("-w", "--working_dir", type=str, required=True,
                        help="the working dir you want to save the result file.")
    return parser.parse_args()


def main(dataset_info, annotation_info, working_dir):
    conversion = DetectionParse(dataset_info, annotation_info)
    print(conversion.struct_defs)
    print(conversion.class_domain_info)
    print(conversion.meta_info)
    print(conversion.dsdl_version)
    generate_obj = Generation(conversion.dsdl_version, conversion.meta_info, conversion.struct_defs,
                              conversion.class_domain_info, conversion.samples, working_dir)
    class_file = generate_obj.write_class_dom()
    def_file = generate_obj.write_struct_def(file_name="object-detection")
    generate_obj.write_samples(file_name=os.path.basename(annotation_info).replace(".json", ""),
                               import_list=[class_file, def_file])


if __name__ == '__main__':
    args = parse_args()
    main(args.dataset_info, args.ann_info, args.working_dir)
