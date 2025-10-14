import subprocess

def run_shell(cmd, check=True):
    """run the shell command. If 'check==True' check that returncode is 0"""
    
    print(f'Running in shell: {cmd}')
    p = subprocess.run(cmd.split(), capture_output=True)
    if check:
        try:
            p.check_returncode()
        except subprocess.CalledProcessError:
            print(str(p.stdout, 'utf-8'))
            print(str(p.stderr, 'utf-8'))
            raise
    return p

def run_ntsim(params, output_dir=None, check=True):
    """run the ntsim with given output directory. 
    If 'check'==True, raises CalledProcessError, if the process exited with nonzero status.
    """
    if output_dir:
        params+=" --H5Writer.h5_output_dir "+str(output_dir)
    return run_shell("python3 -m ntsim "+params, check=check)