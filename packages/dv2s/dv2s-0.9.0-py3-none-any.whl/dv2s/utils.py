#!/usr/bin/python3
import platform
import subprocess
from pathlib import Path
from os import chdir
from queue import Queue
from shutil import unpack_archive
from urllib.parse import quote

import requests

from dv2s.global_vars import R2_URL, TEST_URL, log, NAME


def open_url(url: str, timeout: int):
    headers = {'User-Agent': f'python-urllib/3.13 {NAME}'}
    log.info(f'Connecting to {url}')
    resp = requests.get(url, headers=headers, timeout=timeout)
    if not resp.ok:
        log.error(f'Cannot open {url}')
        raise SystemExit(resp.status_code)
    return resp


def test_file(filename: str|Path):
    filename = Path(filename).resolve()
    if not filename.exists():
        log.error(f'{filename} does not exist')
        raise SystemExit(-1)
    elif filename.stat().st_size == 0:
        log.error(f'{filename} is empty')
        raise SystemExit(-1)
    else:
        return filename


def test_cmd(program: Path|str, option='-version', change_dir=False) -> bool:
    """
    Test given program and option is ok to run or not.
    Args:
        program(Path or str): program path, could be relative path if it can
        be found in $PATH or %PATH%
        option(str): option for program, usually use "-v" to show version to
        test the program
    Return:
        success(bool): success or not
    """
    program = Path(program)
    if program.exists():
        program.chmod(0o755)
    cmd = f'{program} {option}'
    if not change_dir:
        test = subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL)
        success = (not bool(test.returncode))
    else:
        cwd = Path.cwd()
        chdir(program.parent)
        test = subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL)
        success = (not bool(test.returncode))
        chdir(cwd)
    return success


def run_cmd(cmd: str, tmp_file: Path, name: str) -> bool:
    log.debug(f'{cmd}')
    with open(tmp_file, 'w') as f:
        r = subprocess.run(cmd, shell=True, stdout=f, stderr=f)
    if r.returncode != 0:
        log.error(f'Failed to run {name}. See logs for more details')
        log_text = tmp_file.read_text()
        log.error(log_text)
        log.error(f'Command: {cmd}')
        return False
    return True


def get_third_party_path() -> Path:
    """
    Return:
        success(bool): ok or not
        third_party(Path): absolute path of third_party folder
    """
    third_party = Path().home().absolute() / f'.{NAME}'
    if not third_party.exists():
        log.debug(f'Create folder {third_party}')
        try:
            third_party.mkdir()
        except Exception:
            log.error(f'Failed to create {third_party}.' 
                      'Please contact the administrator.')
            raise SystemExit(-1)
    return third_party


def get_software(software: str, url: str, filename: Path,
                 third_party: Path, home_bin: Path, test_option='-version'):
    log.warning(f'Cannot find {software}. Try to install. May cost minutes')
    try:
        _ = open_url(TEST_URL, timeout=10)
        log.info('Internet connection is ok')
    except Exception:
        log.critical('Cannot connect to Server.'
                     'Please check your Internet connection.')
        raise SystemExit(-1)
    try:
        # file is 10mb or larger
        log.info(f'Downloading {filename.name} from {url}')
        down = open_url(f'{url}', timeout=100)
    except Exception as e:
        raise e
        log.critical(f'Cannot download {software}. '
                     f'Please manually download it from {url}')
        raise SystemExit(-1)
    down_file = filename
    with open(down_file, 'wb') as out:
        try:
            _ = down.content
        except TimeoutError:
            log.critical(f'Download {software} timeout.'
                         f'Please manually download it from {url}')
            raise SystemExit(-1)
        out.write(_)
    log.info(f'{filename.name} got. Installing...')
    try:
        # unpack_archive(down_file, third_party/fileinfo[system][1])
        unpack_archive(down_file, third_party)
    except Exception:
        log.critical(f'The {software} file is damaged. '
                     f'Please recheck your connection.')
        raise SystemExit(-1)
    if software == 'mafft.bat':
        for i in ('bin', 'libexec'):
            subfolder = home_bin.parent / 'mafftdir' / i
            # windows use the different path
            if subfolder.exists():
                for file in subfolder.iterdir():
                    file.chmod(0o755)
    if software == 'mkdssp.exe':
        assert test_cmd(home_bin, test_option, change_dir=True)
    else:
        assert test_cmd(home_bin, test_option)
    log.info(f'{software} installed successfully.')
    return True


def get_mafft(third_party=None, result=None) -> str:
    """
    Get mafft location.
    If not found, download it.
    Args:
        third_party(Path or None): path for install
        result(Queue): return values
    Return:
        mafft(str): mafft path
    """
    if third_party is None:
        third_party = get_third_party_path()
    system = platform.system()
    mafft = 'mafft.bat'
    # in Windows, ".exe" can be omitted
    # win_home_blast = home_blast.with_name('blastn.exe')
    ok = False
    # original_url = 'https://mafft.cbrc.jp/alignment/software/'
    # system: {filename, folder}
    fileinfo = {'Linux': ('mafft-7.511-linux.tgz', 'mafft-linux64'),
                'Darwin': ('mafft-7.511-mac.zip', 'mafft-mac'),
                'Windows': ('mafft-7.511-win64-signed.zip', 'mafft-win')}
    home_mafft = third_party / fileinfo[system][1] / mafft
    system = platform.system()
    filename = fileinfo[system][0]
    down_url = f'{R2_URL}{quote(filename)}'
    down_file = third_party / fileinfo[system][0]
    # mafft use '--version' to test
    test_option = '--version'
    if test_cmd(mafft, test_option):
        ok = True
        home_mafft = str(mafft)
    elif test_cmd(home_mafft, test_option):
        ok = True
    else:
        ok = get_software(mafft, down_url, down_file, third_party, home_mafft,
                          test_option=test_option)
    if not ok:
        log.error('Failed to locate and install MAFFT.')
        raise SystemExit(-2)
    if result is not None and ok:
        result.put(('MAFFT', ok))
    return str(home_mafft)


def get_dssp(third_party=None, result=None) -> str:
    """
    Get dssp location.
    If not found, download it.
    Build from https://github.com/PDB-REDO/dssp
    Args:
        third_party(Path or None): path for install
        result(Queue): return values
    Return:
        dssp(str): dssp path
    """
    if third_party is None:
        third_party = get_third_party_path()
    dssp = 'mkdssp.exe'
    # system: {filename, folder}
    fileinfo = {'Linux': 'linux-mkdssp.zip', 'Darwin': 'macos-mkdssp.zip',
                'Windows': 'win-mkdssp.zip'}
    system = platform.system()
    filename = fileinfo[system]
    home_dssp = third_party / dssp
    down_url = f'{R2_URL}{quote(filename)}'
    down_file = third_party / fileinfo[system]
    # dssp use '--version' to test
    test_option = '--version'
    if test_cmd(dssp, test_option):
        return dssp
    elif test_cmd(home_dssp, test_option):
        return str(home_dssp)
    else:
        ok = get_software(dssp, down_url, down_file, third_party, home_dssp,
                          test_option=test_option)
        if ok:
            if result is not None:
                result.put(('DSSP', ok))
            return str(home_dssp)
    log.error('Failed to locate and install DSSP')
    if system == 'Linux':
        log.error('Please try to install via "sudo apt install dssp"')
    elif system == 'Darwin':
        log.error('Please try to install via "brew install brewsci/bio/dssp"')
    else:
        log.error('Please try to install DSSP via conda')
    raise SystemExit(500)
