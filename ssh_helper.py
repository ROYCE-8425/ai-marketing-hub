"""SSH helper — connect to VPS and run commands via paramiko."""
import paramiko, sys, os, time

HOST = "160.191.237.64"
USER = "root"
PASS = "yjuqEJnpTBs0oUaE"

def ssh_run(cmd, timeout=120):
    """Run a single command on VPS, return stdout."""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username=USER, password=PASS, timeout=10)
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode("utf-8", errors="replace")
    err = stderr.read().decode("utf-8", errors="replace")
    code = stdout.channel.recv_exit_status()
    client.close()
    return out, err, code

if __name__ == "__main__":
    cmd = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "echo OK && hostname && uname -a && free -h && df -h /"
    out, err, code = ssh_run(cmd)
    if out:
        print(out.encode("ascii", errors="replace").decode("ascii"))
    if err:
        print(err, file=sys.stderr)
    sys.exit(code)
