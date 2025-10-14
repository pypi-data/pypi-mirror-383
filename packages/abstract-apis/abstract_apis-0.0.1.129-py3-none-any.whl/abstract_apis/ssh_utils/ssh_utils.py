from .imports import *
def get_remote_bash(
            cmd: str,
            cwd: str | None = None
        ):
    return f"bash -lc {shlex.quote((f'cd {shlex.quote(cwd)} && {cmd}') if workdir else cmd)}"
def get_remote_ssh(
            user_at_host: str=None,
            remote:str=None
        ):
    return f"ssh {shlex.quote(user_at_host)} {shlex.quote(remote)}"
                   
def get_remote_cmd(
            cmd: str,
            user_at_host: str,
            cwd: str | None = None,
            
        ):
    remote = get_remote_bash(
        cmd=cmd,
        cwd=cwd
        )
    full = get_remote_ssh(
        user_at_host=user_at_host,
        remote=remote
        )
    return full
def execute_cmd(
        *args,
        outfile=None,
        **kwargs
    ) -> str:
    proc = subprocess.run(*args, **kwargs)
    output = (proc.stdout or "") + (proc.stderr or "")
    if outfile:
        try:
            with open(outfile, "w", encoding="utf-8", errors="ignore") as f:
                f.write(output)
        except Exception:
            pass
    return output

def run_local_cmd(
        cmd: str,
        cwd: str | None = None,
        outfile: Optional[str] = None,
        shell=True,
        text=True,
        capture_output=True
    ) -> str:
    return execute_cmd(
            cmd,
            outfile=outfile,
            shell=shell,
            cwd=cwd,
            text=text,
            capture_output=capture_output
        )

def run_ssh_cmd(
        user_at_host: str,
        cmd: str,
        cwd: str | None = None,
        outfile: Optional[str] = None,
        shell=True,
        text=True,
        capture_output=True
    ) -> str:
    """
    Run on remote via SSH; capture stdout+stderr locally; write to local outfile.
    NOTE: we do *not* try to write the file on the remote to avoid later scp.
    """
    # wrap in bash -lc for PATH/profile + allow 'cd && ...'
    cmd = get_remote_cmd(
        cmd=cmd,
        user_at_host=user_at_host,
        cwd=cwd
        )
    return execute_cmd(
            cmd,
            outfile=outfile,
            shell=shell,
            text=text,
            capture_output=capture_output
        )
def run_cmd(
        cmd: str=None,
        cwd: str | None = None,
        outfile: Optional[str] = None,
        shell=True,
        text=True,
        capture_output=True,
        user_at_host: str=None
    ) -> str:
    if user_at_host:
        return run_ssh_cmd(
                user_at_host=user_at_host,
                cmd=cmd,
                cwd=cwd,
                outfile=outfile,
                shell=shell,
                text=text,
                capture_output=capture_output
            )
    return run_local_cmd(
            cmd=cmd,
            cwd=cwd,
            outfile=outfile,
            shell=shell,
            text=text,
            capture_output=capture_output
        )
run_local_cmd = run_local_cmd
local_cmd = run_local_cmd
run_remote_cmd = run_ssh_cmd
remote_cmd = run_ssh_cmd
run_any_cmd = run_cmd
any_cmd = run_cmd
