import paramiko , traceback
from easy_utils_dev.debugger import DEBUGGER
from easy_utils_dev import utils

class CREATESSH :
    def __init__(self, loggerName=None , logger_homepath=None ,  **kwargs) -> None:
        '''
        @Parameters:
        address: address plain string
        user wsnoc user plain string
        password: password plain string
        options: 
        sshPort: ssh 22
        '''
        self.address = kwargs.get('address')
        self.user = kwargs.get('user' , 'root')
        if loggerName is None :
            loggerName = f"ssh-{self.address}"
        self.password = kwargs.get('password')
        self.port = kwargs.get('sshPort' , 22 )
        self.logger = DEBUGGER(loggerName ,homePath=logger_homepath)
        self.ssh = None
        self.ssh_sessions = []


    def init_sftp(self) -> paramiko.SFTPClient :
        return self.ssh.open_sftp()
    
    
    def init_shell(self) -> paramiko.SSHClient :
        ssh = paramiko.SSHClient()
        try :
            ssh.load_system_host_keys()
        except Exception as error:
            self.logger.warning(f"Faield to load system host keys: {error}. [This error is not critical but better to report it]")
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self.address,self.port,self.user, self.password )
        transport = ssh.get_transport()
        transport.set_keepalive(60)
        def init_ch() :
            return self.init_ch(ssh)
        ssh.init_ch = init_ch
        ssh.connectionId = utils.getRandomKey(5)
        self.ssh_sessions.append(ssh)
        self.ssh = ssh
        ssh.core = self
        return ssh
    
    def isSessionActive(session) -> bool:
        return session.active
    
    def isSshActive(self) -> bool :
        if self.ssh.get_transport() is not None:
            return self.ssh.get_transport().is_active()
        else :
            return False

    def init_ch(self) -> paramiko.Channel:
        # to get new invoked shells for multi executions
        ch = self.ssh.invoke_shell()
        ch.exit_level = 0
        ch.parent_ssh = self.ssh
        def disconnect(ch=ch) :
            try :
                ch.sendall('exit\n')
                ch.close()
            except :
                pass
        ch.disconnect = disconnect
        return ch

    def ssh_execute(self ,command ,  merge_output=False , hide_output=True) :
        self.logger.info(f"executing {command}")
        try :
            stdin_ , stdout_ , stderr_ = self.ssh.exec_command(command)
            r = stdout_.read().decode()
            e = stderr_.read().decode()
            if r.endswith('\n') :
                r = r[ : -1]
            if hide_output : 
                self.logger.debug(f""" 
                =========================
                +command = '{command}'
                -stdout = {r}
                -stderr = {e}
                =========================
                """)
            else :
                self.logger.info(f""" 
                =========================
                +command = '{command}'
                -stdout = {r}
                -stderr = {e}
                =========================
                """)
            if merge_output :
                return str(r) + str(e)
            return r 
        except Exception as error :
            self.logger.info(traceback.format_exc())
            return str(error)
        
        
if __name__ == "__main__" :
    pass
