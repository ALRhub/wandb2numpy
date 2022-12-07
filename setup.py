from setuptools import setup

setup(
    name='wandb2numpy',
    version='0.1',
    packages=['wandb2numpy'],
    url='',
    license='',
    author='Kolja Bauer',
    author_email='kolja.bauer@gmail.com',
    description='Library to export data from WandB to numpy arrays or csv files.',
    install_requires=['argparse', 'pandas', 'pyyaml', 'numpy', 'requests', 'tqdm', 'wandb'],
    entry_points = {'console_scripts': ['wandb2numpy=wandb2numpy.command_line:main'],}
)


