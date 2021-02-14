from distutils.core import setup

# Autogenerates pyproject.toml and the git-ignored *.egg-info folder

VERSION = ".".join(map(str, (0, 0, 1)))

setup(
    name="GolangCodeGenerator",
    version=VERSION,
    author="Snapper Vibes",
    author_email="ruffoloCAPITALSAREOBFUSACATIONTO🛑BOTSdrew@gmail.com",
    url="https://www.github.com/snappervibes/golang_code_generator",
    packages=["golang_code_gen"],
)
