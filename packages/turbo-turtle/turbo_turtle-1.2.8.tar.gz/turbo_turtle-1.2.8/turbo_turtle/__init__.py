"""Copyright (c) 2023, Triad National Security, LLC. All rights reserved.

This program was produced under U.S. Government contract 89233218CNA000001 for Los Alamos National Laboratory (LANL),
which is operated by Triad National Security, LLC for the U.S.  Department of Energy/National Nuclear Security
Administration. All rights in the program are reserved by Triad National Security, LLC, and the U.S. Department of
Energy/National Nuclear Security Administration. The Government is granted for itself and others acting on its behalf a
nonexclusive, paid-up, irrevocable worldwide license in this material to reproduce, prepare derivative works, distribute
copies to the public, perform publicly and display publicly, and to permit others to do so.

BSD 3-Clause License

Copyright (c) 2023, Triad National Security, LLC. All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following
   disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
   disclaimer in the documentation and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products
   derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

from importlib.metadata import PackageNotFoundError, version

import lazy_loader

submodules = [
    "scons_extensions",
    "geometry_xyplot",
]
__getattr__, __dir__, __all__ = lazy_loader.attach(__name__, submodules=submodules)

try:
    __version__ = version("turbo_turtle")
except PackageNotFoundError:
    try:
        from turbo_turtle import _version

        __version__ = _version.version
    except ImportError:
        # Should only hit this when running as an un-installed package in the local repository
        import pathlib
        import warnings

        warnings.filterwarnings(action="ignore", message="tag", category=UserWarning, module="setuptools_scm")
        import setuptools_scm

        __version__ = setuptools_scm.get_version(root=pathlib.Path(__file__).parent.parent)
