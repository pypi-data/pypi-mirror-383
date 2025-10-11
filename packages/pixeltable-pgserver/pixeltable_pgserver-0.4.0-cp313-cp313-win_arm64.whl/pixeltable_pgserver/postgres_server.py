import atexit
import logging
import os
import platform
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Optional, Union

import psutil

from ._commands import POSTGRES_BIN_PATH, initdb, pg_ctl  # type: ignore[attr-defined]
from .utils import DiskList, PostmasterInfo, find_suitable_port, find_suitable_socket_dir

if platform.system() != 'Windows':
    from .utils import ensure_folder_permissions, ensure_prefix_permissions, ensure_user_exists

_logger = logging.getLogger('pixeltable_pgserver')


class PostgresServer:
    """Provides a common interface for interacting with a server."""

    import fasteners  # type: ignore[import-untyped]
    import platformdirs

    _instances: dict[Path, 'PostgresServer'] = {}

    runtime_path: Path = platformdirs.user_runtime_path('python_PostgresServer')
    if not runtime_path.exists():
        # On some Linux systems, this directory does not necessarily exist, and there is no obvious way to create it
        # at this time. Fall back on the temporary directory.
        runtime_path = Path(tempfile.gettempdir())
    lock_path = runtime_path / '.lockfile'
    _lock = fasteners.InterProcessLock(lock_path)

    def __init__(self, pgdata: Path, *, cleanup_mode: Optional[str] = 'stop'):
        """Initializes the postgresql server instance.
        Constructor is intended to be called directly, use get_server() instead.
        """
        assert cleanup_mode in [None, 'stop', 'delete']

        self.pgdata = pgdata
        self.log = self.pgdata / 'log'

        # postgres user name, NB not the same as system user name
        self.system_user = None

        # note os.geteuid() is not available on windows, so must go after
        if platform.system() != 'Windows' and os.geteuid() == 0:
            # running as root
            # need a different system user to run as
            self.system_user = 'pgserver'
            ensure_user_exists(self.system_user)

        self.postgres_user = 'postgres'
        list_path = self.pgdata / '.handle_pids.json'
        self.global_process_id_list = DiskList(list_path)
        self.cleanup_mode = cleanup_mode
        self._postmaster_info: Optional[PostmasterInfo] = None
        self._count = 0

        atexit.register(self._cleanup)
        with self._lock:
            self._instances[self.pgdata] = self
            self.ensure_pgdata_inited()
            self.ensure_postgres_running()
            self.global_process_id_list.get_and_add(os.getpid())

    def get_postmaster_info(self) -> PostmasterInfo:
        assert self._postmaster_info is not None
        return self._postmaster_info

    def get_pid(self) -> Optional[int]:
        """Returns the pid of the postgresql server process.
        (First line of postmaster.pid file).
        If the server is not running, returns None.
        """
        return self.get_postmaster_info().pid

    def get_uri(self, database: Optional[str] = None, driver: Optional[str] = None) -> str:
        """Returns a connection string for the postgresql server."""
        return self.get_postmaster_info().get_uri(database=database, driver=driver)

    def ensure_pgdata_inited(self) -> None:
        """Initializes the pgdata directory if it is not already initialized."""
        if platform.system() != 'Windows' and os.geteuid() == 0:
            import pwd
            import stat

            assert self.system_user is not None
            ensure_prefix_permissions(self.pgdata)
            ensure_prefix_permissions(POSTGRES_BIN_PATH)

            read_perm = stat.S_IRGRP | stat.S_IROTH
            execute_perm = stat.S_IXGRP | stat.S_IXOTH
            # for envs like cibuildwheel docker, where the user is has no permission otherwise
            ensure_folder_permissions(POSTGRES_BIN_PATH, execute_perm | read_perm)
            ensure_folder_permissions(POSTGRES_BIN_PATH.parent / 'lib', read_perm)

            os.chown(self.pgdata, pwd.getpwnam(self.system_user).pw_uid, pwd.getpwnam(self.system_user).pw_gid)

        if not (self.pgdata / 'PG_VERSION').exists():  # making a new PGDATA
            # First ensure there are no left-over servers on a previous version of the same pgdata path,
            # which does happen on Mac/Linux if the previous pgdata was deleted without stopping the server process
            # (the old server continues running for some time, sometimes indefinitely)
            #
            # It is likely the old server could also corrupt the data beyond the socket file, so it is best to kill it.
            # This must be done before initdb to ensure no race conditions with the old server.
            #
            # Since we do not know PID information of the old server, we stop all servers with the same pgdata path.
            # way to test this: python -c 'import pixeltable as pxt; pxt.Client()'; rm -rf ~/.pixeltable/; python -c 'import pixeltable as pxt; pxt.Client()'
            _logger.info(f'no PG_VERSION file found within {self.pgdata}. Initializing pgdata')
            for proc in psutil.process_iter(attrs=['name', 'cmdline']):
                if proc.info['name'] == 'postgres':
                    if proc.info['cmdline'] is not None and str(self.pgdata) in proc.info['cmdline']:
                        _logger.info(f"Found a running postgres server with same pgdata: {proc.as_dict(attrs=['name', 'pid', 'cmdline'])=}.\
                                            Assuming it is a leftover from a previous run on a different version of the same pgdata path, killing it.")
                        proc.terminate()
                        try:
                            proc.wait(2)  # wait at most a second
                        except psutil.TimeoutExpired:
                            pass
                        if proc.is_running():
                            proc.kill()
                        assert not proc.is_running()

            initdb(
                ['--auth=trust', '--auth-local=trust', '--encoding=utf8', '-U', self.postgres_user],
                pgdata=self.pgdata,
                user=self.system_user,
            )
        else:
            _logger.info('PG_VERSION file found, skipping initdb')

    def ensure_postgres_running(self) -> None:
        """pre condition: pgdata is initialized, being run with lock.
        post condition: self._postmaster_info is set.
        """

        postmaster_info = PostmasterInfo.read_from_pgdata(self.pgdata)
        if postmaster_info is not None and postmaster_info.is_running():
            _logger.info(f'a postgres server is already running: {postmaster_info=} {postmaster_info.process=}')
            self._postmaster_info = postmaster_info
        else:
            if postmaster_info is not None and not postmaster_info.is_running():
                _logger.info(f'found a postmaster.pid file, but the server is not running: {postmaster_info=}')
            if postmaster_info is None:
                _logger.info(f'no postmaster.pid file found in {self.pgdata}')

            if platform.system() != 'Windows':
                # use sockets to avoid any future conflict with port numbers
                socket_dir = find_suitable_socket_dir(self.pgdata, self.runtime_path)

                if self.system_user is not None and socket_dir != self.pgdata:
                    ensure_prefix_permissions(socket_dir)
                    socket_dir.chmod(0o777)

                pg_ctl_args = [
                    '-w',  # wait for server to start
                    '-o',
                    '-h ""',  # no listening on any IP addresses (forwarded to postgres exec) see man postgres for -hj
                    '-o',
                    f'-k {socket_dir}',  # socket option (forwarded to postgres exec) see man postgres for -k
                    '-l',
                    str(self.log),  # log location: set to pgdata dir also
                    'start',  # action
                ]
            else:  # Windows,
                socket_dir = None
                # socket.AF_UNIX is undefined when running on Windows, so default to a port
                host = '127.0.0.1'
                port = find_suitable_port(host)
                pg_ctl_args = [
                    '-w',  # wait for server to start
                    '-o',
                    f'-h "{host}"',
                    '-o',
                    f'-p {port}',
                    '-l',
                    str(self.log),  # log location: set to pgdata dir also
                    'start',  # action
                ]

            try:
                _logger.info(f'running pg_ctl... {pg_ctl_args=}')
                pg_ctl(pg_ctl_args, pgdata=self.pgdata, user=self.system_user, timeout=10)
            except subprocess.CalledProcessError as err:
                _logger.error(
                    f'Failed to start server.\nShowing contents of postgres server log ({self.log.absolute()}) below:\n{self.log.read_text()}'
                )
                raise err
            except subprocess.TimeoutExpired as err:
                _logger.error(
                    f'Timeout starting server.\nShowing contents of postgres server log ({self.log.absolute()}) below:\n{self.log.read_text()}'
                )
                raise err

            while True:
                # in Windows, when there is a postmaster.pid,  init_ctl seems to return
                # but the file is not immediately updated, here we wait until the file shows
                # a new running server. see test_stale_postmaster
                _logger.info(f'waiting for postmaster info to show a running process')
                pinfo = PostmasterInfo.read_from_pgdata(self.pgdata)
                _logger.info(f'running... checking if ready {pinfo=}')
                if pinfo is not None and pinfo.is_running() and pinfo.status == 'ready':
                    self._postmaster_info = pinfo
                    break

                _logger.info(f'not ready yet... waiting a bit more...')
                time.sleep(1.0)

        _logger.info(f'Now asserting server is running {self._postmaster_info=}')
        assert self._postmaster_info is not None
        assert self._postmaster_info.is_running()
        assert self._postmaster_info.status == 'ready'

    def _cleanup(self) -> None:
        with self._lock:
            pids = self.global_process_id_list.get_and_remove(os.getpid())
            _logger.info(f'exiting {os.getpid()} remaining {pids=}')
            if pids != [os.getpid()]:  # includes case where already cleaned up
                return

            _logger.info(f'cleaning last handle for server: {self.pgdata}')
            # last handle is being removed
            del self._instances[self.pgdata]
            if self.cleanup_mode is None:  # done
                return

            assert self.cleanup_mode in ['stop', 'delete']
            if self._postmaster_info is not None:
                assert self._postmaster_info.process is not None
                if self._postmaster_info.process.is_running():
                    try:
                        pg_ctl(['-w', 'stop'], pgdata=self.pgdata, user=self.system_user)
                        stopped = True
                    except subprocess.CalledProcessError:
                        stopped = False
                        pass  # somehow the server is already stopped.

                    if not stopped:
                        _logger.warning(f'Failed to stop server, killing it instead.')
                        self._postmaster_info.process.terminate()
                        try:
                            self._postmaster_info.process.wait(2)
                        except psutil.TimeoutExpired:
                            pass
                        if self._postmaster_info.process.is_running():
                            self._postmaster_info.process.kill()

            if self.cleanup_mode == 'stop':
                return

            assert self.cleanup_mode == 'delete'
            shutil.rmtree(str(self.pgdata))
            atexit.unregister(self._cleanup)

    def psql(self, command: str) -> str:
        """Runs a psql command on this server. The command is passed to psql via stdin."""
        executable = POSTGRES_BIN_PATH / 'psql'
        stdout = subprocess.check_output(f'{executable} {self.get_uri()}', input=command.encode(), shell=True)
        return stdout.decode('utf-8')

    def __enter__(self):
        self._count += 1
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._count -= 1
        if self._count <= 0:
            self._cleanup()

    def cleanup(self) -> None:
        """Stops the postgresql server and removes the pgdata directory."""
        self._cleanup()


def get_server(pgdata: Union[Path, str], cleanup_mode: Optional[str] = 'stop') -> PostgresServer:
    """Returns handle to postgresql server instance for the given pgdata directory.
    Args:
        pgdata: pddata directory. If the pgdata directory does not exist, it will be created, but its
        parent must exists and be a valid directory.
        cleanup_mode: If 'stop', the server will be stopped when the last handle is closed (default)
                        If 'delete', the server will be stopped and the pgdata directory will be deleted.
                        If None, the server will not be stopped or deleted.

        To create a temporary server, use mkdtemp() to create a temporary directory and pass it as pg_data,
        and set cleanup_mode to 'delete'.
    """
    if isinstance(pgdata, str):
        pgdata = Path(pgdata)
    pgdata = pgdata.expanduser().resolve()

    if not pgdata.parent.exists():
        raise FileNotFoundError(f'Parent directory of pgdata does not exist: {pgdata.parent}')

    if not pgdata.exists():
        pgdata.mkdir(parents=False, exist_ok=False)

    if pgdata in PostgresServer._instances:
        return PostgresServer._instances[pgdata]

    return PostgresServer(pgdata, cleanup_mode=cleanup_mode)
