from commands.cmdbase import CmdBase


class Config(CmdBase):
    """Set dsdl configuration {file path, user login info}.

    Args:
        CmdBase (_type_): _description_
    """
    def init_parser(self, subparsers):
        """_summary_

        _extended_summary_

        Args:
            subparsers (_type_): _description_
        """
        
        available_keys ='''
        The available keys are:       
        
            auth.username             # central repo username  
            auth.password             # central repo password
            storage.name              # storage name
            storage.loc               # storage path
            '''
        config_parser = subparsers.add_parser('config', help = 'set dsdl configuration.')
        config_parser.add_argument('-k',
                                   '--keys',
                                   action = 'store_const',
                                   const = available_keys,
                                   help = 'show all the available keys',
                                   required = False)
        config_parser.add_argument('-s',
                                   '--setvalue',
                                   type = str,
                                   nargs = 2,
                                   action = 'append',
                                   help = 'Set key-value for a specific configuration.')
        config_parser.add_argument('-l',
                                   '--list',
                                   help = 'show all key value pairs')
        
        return config_parser
    
    def cmd_entry(self, cmdargs, config):
        """
        Entry point for the command.

        Args:
            self:
            args:
            config:

        Returns:

        """
        print(cmdargs)
        print(f"{cmdargs.setvalue}")
