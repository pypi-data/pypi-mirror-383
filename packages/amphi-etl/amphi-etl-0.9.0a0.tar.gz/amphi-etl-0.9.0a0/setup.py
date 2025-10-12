# setup.py — make amphi-etl install the pipeline-scheduler JLab extension by default

from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.develop import develop
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.resolve()

def collect_files(src_dir, dest_dir):
    files = []
    for root, dirs, filenames in os.walk(src_dir):
        for dirname in dirs:
            dirpath = os.path.join(root, dirname)
            files.append((os.path.join(dest_dir, os.path.relpath(dirpath, src_dir)), []))
        for filename in filenames:
            src_file = os.path.join(root, filename)
            dest_file = os.path.relpath(src_file, src_dir)
            files.append((os.path.join(dest_dir, os.path.dirname(dest_file)), [src_file]))
    return files

# Paths
LABEXT_BASE = 'share/jupyter/labextensions/@amphi'
PIPELINE_SCHEDULER_SRC = ROOT / 'amphi' / 'pipeline-scheduler'  # Changed: built labextension location
PIPELINE_SCHEDULER_WHEEL = ROOT / 'packages' / 'pipeline-scheduler' / 'dist' / 'pipeline_scheduler-0.9.0a0-py3-none-any.whl'

# Base data files
data_files = (
    collect_files('config/labconfig', 'etc/jupyter/labconfig') +
    collect_files('config/settings', 'share/jupyter/lab/settings')
)

# Include pipeline-scheduler (built) labextension inside this wheel
# The labextension is built to amphi/pipeline-scheduler by the jupyterlab builder
if PIPELINE_SCHEDULER_SRC.exists():
    data_files += collect_files(
        str(PIPELINE_SCHEDULER_SRC),
        f'{LABEXT_BASE}/pipeline-scheduler'
    )
    # Ensure package.json is present for JupyterLab discovery
    pkg_json = PIPELINE_SCHEDULER_SRC / 'package.json'
    if pkg_json.exists():
        data_files += [(
            f'{LABEXT_BASE}/pipeline-scheduler',
            [str(pkg_json)]
        )]
else:
    # Optional: fail early to avoid publishing a wheel without the JS assets
    raise FileNotFoundError(
        f"Missing built JupyterLab extension for pipeline-scheduler at {PIPELINE_SCHEDULER_SRC}. "
        "Run `cd packages/pipeline-scheduler && jlpm install && jlpm run build:prod` before building the wheel."
    )

# Custom install commands to automatically install the bundled wheel
class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        install.run(self)
        self._install_pipeline_scheduler()
    
    def _install_pipeline_scheduler(self):
        wheel_path = PIPELINE_SCHEDULER_WHEEL
        if wheel_path.exists():
            print(f"Installing bundled pipeline-scheduler from {wheel_path}")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', str(wheel_path)])
        else:
            print(f"Warning: pipeline-scheduler wheel not found at {wheel_path}")

class PostDevelopCommand(develop):
    """Post-installation for development mode."""
    def run(self):
        develop.run(self)
        self._install_pipeline_scheduler()
    
    def _install_pipeline_scheduler(self):
        wheel_path = PIPELINE_SCHEDULER_WHEEL
        if wheel_path.exists():
            print(f"Installing bundled pipeline-scheduler from {wheel_path}")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', str(wheel_path)])
        else:
            print(f"Warning: pipeline-scheduler wheel not found at {wheel_path}")

setup(
    name='amphi-etl',
    version='0.9.0-alpha0',
    description='Open-source and Python-based ETL',
    author='Thibaut Gourdel',
    author_email='tgourdel@amphi.ai',
    license='ELv2',
    install_requires=[
        'jupyterlab==4.4.7',
        'jupyterlab-amphi==0.9.0-alpha0',
        'pandas>=2.0'
    ],
    packages=find_packages(include=['amphi', 'config']),  # Removed 'packages' - don't want to include source
    include_package_data=True,
    package_data={
        'amphi': [
            'theme-light/*', 
            'ui-component/*',
            'pipeline-scheduler/**/*',  # Include the built labextension
        ]
    },
    data_files=data_files,
    cmdclass={
        'install': PostInstallCommand,
        'develop': PostDevelopCommand,
    },
    entry_points={
        'console_scripts': [
            'amphi=amphi.main:main',
        ],
    },
)