from commands.cmdbase import CmdBase
from commands.const import DSDL_CLI_DATASET_NAME
from commons.argument_parser import EnvDefaultVar
from commons.exceptions import CLIException, ExistCode
from loguru import logger
from rich import print as rprint
from rich.pretty import pprint
from tabulate import tabulate
from utils import admin


class Ls(CmdBase):
    """Show all the available datasets and its storage path.

    Args:
        CmdBase (_type_): _description_
    """
    def init_parser(self, subparsers):
        """_summary_

        Args:
            subparsers (_type_): _description_
        """
        
        status_parser = subparsers.add_parser('ls', help = 'show local datasets', example = 'ls.example')
        status_parser.add_argument('-s',
                                   '--skip-header', 
                                   help = 'toggle display for headers',
                                   action = 'store_true',
                                   required = False)
        status_parser.add_argument('-v',
                                   '--verbose',
                                   action = 'count',
                                   default = 0,
                                   help = 'display detailed dataset info',
                                   required = False)
        status_parser.add_argument('--dataset-name',
                                    type = str,
                                    required = False,
                                    help = 'dataset name')
        return status_parser
    
    def get_dataset_df(self, dataset_name = ''):
        db_client = admin.DBClient()
        if dataset_name:
            dataset_path = db_client.get_local_dataset_path(dataset_name)
            if not dataset_path:
                raise CLIException(ExistCode.DATASET_NOT_EXIST_LOCAL,
                                "Dataset `{}` does not exist locally".format(dataset_name))
        dataset_list = db_client.get_sqlite_dict_list('select * from dataset')

        if len(dataset_list) == 0:
            raise CLIException(ExistCode.NO_DATASET_LOCAL,
                               "Local storage has no datasets !")
        # datasplit_list = db_client.get_sqlite_dict_list('select * from split')
        datasplit_join_list = db_client.get_sqlite_dict_list("select * from split where dataset_name='%s'" %(dataset_name))

        return dataset_list, datasplit_join_list
    
    def datalist_trim(self, dataset_list, datasplit_join_list):
        dataset_list_trim = []
        dataset_list_out = []
        # datasplit_list_trim = []
        datasplit_join_list_trim = []
        datasplit_join_list_out = []
        dataset_remove_list = ['created_time','updated_time','dataset_path','label_data', 'media_data']
        _verbose_list = ['label_data', 'media_data']
        datasplit_remove_list = ['created_time','updated_time','label_data', 'media_data']
        
        for idx, elem in enumerate(dataset_list):
            dataset_list[idx]['label_data_exists'] = True if dataset_list[idx]['label_data'] else False
            dataset_list[idx]['media_data_exists'] = True if dataset_list[idx]['media_data'] else False
            dataset_list[idx]['dataset_media_file_bytes'] = str(self.human_readable_size(dataset_list[idx]['dataset_media_file_bytes']))
            dataset_list_trim.append({key:dataset_list[idx][key] for key in dataset_list[idx] if key not in dataset_remove_list})
            dataset_list_out.append({key:dataset_list[idx][key] for key in dataset_list[idx] if key not in _verbose_list})
        # for idx, elem in enumerate(datasplit_list):
        #     datasplit_list_trim.append({key:datasplit_list[idx][key] for key in datasplit_list[idx] if key not in datasplit_verbose_list})
        
        for idx, elem in enumerate(datasplit_join_list):
            datasplit_join_list[idx]['label_data_exists'] = True if datasplit_join_list[idx]['label_data'] else False
            datasplit_join_list[idx]['media_data_exists'] = True if datasplit_join_list[idx]['media_data'] else False
            datasplit_join_list[idx]['split_media_file_bytes'] = str(self.human_readable_size(datasplit_join_list[idx]['split_media_file_bytes']))
            datasplit_join_list_trim.append({key:datasplit_join_list[idx][key] for key in datasplit_join_list[idx] if key not in datasplit_remove_list})
            datasplit_join_list_out.append({key:datasplit_join_list[idx][key] for key in datasplit_join_list[idx] if key not in _verbose_list})
        
        # return dataset_list_trim, datasplit_list_trim, datasplit_join_list_trim
        return dataset_list_trim, dataset_list_out, datasplit_join_list_trim, datasplit_join_list_out
    
    def human_readable_size(self, size:int, decimal_places = 2):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
            if size < 1024.0 or unit == 'PB':
                break
            size /= 1024.0
        return f"{size:.{decimal_places}f} {unit}"
    
    
    def cmd_entry(self, cmdargs, config):
        """
        Entry point for the command.

        Args:
            self:
            args:
            config:

        Returns:

        """
        
        __MAPPING = {'dataset_name': 'DatasetName',
                    'task_type': 'TaskType',
                    'storage_name': 'StorageName',
                    'dataset_media_file_num': 'MediaFileNum',
                    'dataset_media_file_bytes': 'MediaFileBytes',
                    'label_data_exists':'LabelDataExists',
                    'media_data_exists':'MediaDataExists',
                    'dataset_path':'DatasetPath',
                    'created_time':'CreatedTime',
                    'updated_time':'UpdatedTime',
                    'split_type':'SplitType',
                    'split_name': 'SplitName',
                    'split_media_file_num':'MediaFileNum',
                    'split_media_file_bytes': 'MediaFileBytes'}

        dataset_name = cmdargs.dataset_name
        dataset_list, datasplit_join_list= self.get_dataset_df(dataset_name)
        dataset_list_trim, dataset_list_out, datasplit_join_list_trim, datasplit_join_list_out = self.datalist_trim(dataset_list, datasplit_join_list)
        
        # no split show dataset table
        if not cmdargs.dataset_name:
        # default display no argument is given
            if not (cmdargs.skip_header or cmdargs.verbose):
                rprint(tabulate(dataset_list_trim, headers=__MAPPING, tablefmt='plain', numalign='left'))
                
            if cmdargs.verbose:
                if cmdargs.verbose >= 1:
                    # verbose and skip head
                    if cmdargs.skip_header:
                        rprint(tabulate(dataset_list_out, tablefmt='plain',numalign='left'))
                    # verbose but not skip head
                    else:
                        rprint(tabulate(dataset_list_out, headers = __MAPPING, tablefmt='plain',numalign='left'))
                        
            if cmdargs.skip_header:
                # not verbose but skip head
                if not cmdargs.verbose:
                    rprint(tabulate(dataset_list_trim, tablefmt='plain', numalign='left'))
        # show split dataset
        else:
            if not (cmdargs.skip_header or cmdargs.verbose):
                rprint(tabulate(datasplit_join_list_trim, headers=__MAPPING, tablefmt='plain',numalign='left'))
                
            if cmdargs.verbose:
                if cmdargs.verbose >= 1:
                    # verbose and skip head
                    if cmdargs.skip_header:
                        rprint(tabulate(datasplit_join_list_out, tablefmt='plain',numalign='left'))
                    # verbose but not skip head
                    else:
                        rprint(tabulate(datasplit_join_list_out, headers = __MAPPING, tablefmt='plain',numalign='left'))
                        
            if cmdargs.skip_header:
                # not verbose but skip head
                if not cmdargs.verbose:
                    rprint(tabulate(datasplit_join_list_trim, tablefmt='plain',numalign='left'))
