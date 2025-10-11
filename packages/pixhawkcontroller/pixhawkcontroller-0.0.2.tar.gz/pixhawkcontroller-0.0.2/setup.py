# SPDX-License-Identifier: MIT
from pathlib import Path
from setuptools import setup, find_packages

HERE = Path(__file__).parent
README_PATH = HERE / "README.md"
long_description = README_PATH.read_text(encoding="utf-8") if README_PATH.exists() else (
    "Lightweight Pixhawk/ArduPilot controller utilities using pymavlink."
)

# Load version without importing the package (works for sdists & linting)
about = {}
version_file = HERE / "pixhawkcontroller" / "__version__.py"
if version_file.exists():
    exec(version_file.read_text(), about)
else:
    about["__version__"] = "0.1.0"  # fallback/dev version
package_version = about["__version__"]

setup(
    name="pixhawkcontroller",
    version=package_version,  # from __version__.py
    description="Lightweight Pixhawk/ArduPilot controller utilities using pymavlink",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Md Shahriar Forhad",
    author_email="shahriar.forhad.eee@gmail.com",
    url="https://github.com/Shahriar88/pixhawkcontroller",
    license="MIT",
    license_files=["LICENSE"],
    packages=find_packages(exclude=("tests", "docs", "examples")),
    include_package_data=True,

    # ✅ Runtime deps only
    install_requires=[
        "pymavlink>=2.4.41",
        "pyserial>=3.5",
    ],

    # 👇 Optional: expose pinned dev/build tools as an extra
    extras_require={
        "dev": [
            "build==1.3.0",
            "setuptools==80.9.0",
            "wheel==0.45.1",
            "twine==6.2.0",
            "packaging==25.0",
        ]
    },

    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
        "Topic :: System :: Hardware",
        "Topic :: Software Development :: Libraries",
    ],
    keywords=["pixhawk", "ardupilot", "mavlink", "pymavlink", "drone", "uav"],
    project_urls={
        "Source": "https://github.com/Shahriar88/pixhawkcontroller",
        "Issues": "https://github.com/Shahriar88/pixhawkcontroller/issues",
    },
)
