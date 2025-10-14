from setuptools import setup, find_packages
from setuptools.dist import Distribution
from distutils.command.build import build as _build

class build(_build):
    def run(self):
        self.run_command("build_ext")
        _build.run(self)

class BinaryDistribution(Distribution):
    def has_ext_modules(self):
        return True

setup(
    name="snAPI",
    version="1.1.0", # also change resource.h !!!
    packages=['snAPI'],
    include_package_data=True,
    zip_safe=False,
    # install_requires=["numpy"],
    # entry_points={
    #     'console_scripts': [
    #         'my_command=snAPI.Main:snAPI',
    #     ],
    # },
    # classifiers=[
    #     "Programming Language :: Python :: 3",
    #     "Programming Language :: Python :: 3.6",
    #     "Programming Language :: Python :: 3.7",
    #     "Programming Language :: Python :: 3.8",
    #     "Programming Language :: Python :: 3.9",
    #     "Programming Language :: Python :: 3.10",
    #     "Programming Language :: Python :: 3.11",
    #     "Programming Language :: Python :: 3.12",
    #     "Programming Language :: Python :: 3.13",
    #     "Programming Language :: Python :: 3"
    #     # Add more classifiers for other compatible Python versions
    # ],
    requires=["setuptools", "wheel"],
    package_data={"snAPI": ["*.dll",
                            "*.so",
                            "*.ini",
                            ]},
    distclass=BinaryDistribution,
    cmdclass={"build": build},
)

# clean delete snAPI.egg-inf, build, dist

# update pyproject.toml (version)
# python -m build --sdist --wheel

# $env:CIBW_ARCHS = "AMD64"
# cibuildwheel --output-dir wheelhouse
# 
# delete old files in wheelhouse
# twine upload --config-file .pypirc --repository snapi --verbose wheelhouse\*.whl  
# pip install --upgrade snapi



# pip install .\dist\snAPI-0.1.0-cp311-cp311-win_amd64.whl --force-reinstall

# git fetch github main:main
# git merge github/main
# git add -A
# git commit
# git tag 'v1.0.11'
# git push github main
# git push github --tags