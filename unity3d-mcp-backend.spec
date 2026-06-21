# -*- mode: python ; coding: utf-8 -*-
a = Analysis(
    ['src/unity3d_mcp/__main__.py'],
    pathex=['src'],
    datas=[('src/unity3d_mcp', 'unity3d_mcp')],
    hiddenimports=[
        'uvicorn.logging','uvicorn.loops','uvicorn.loops.asyncio',
        'uvicorn.protocols','uvicorn.protocols.http',
        'uvicorn.protocols.http.httptools_impl',
        'uvicorn.protocols.http.h11_impl',
        'uvicorn.lifespan','uvicorn.lifespan.on',
        'UnityPy','UnityPy.enums','UnityPy.files',
        'UnityPy.export','UnityPy.assets',
        'structlog','structlog.stdlib','structlog.processors',
        'fastmcp','fastmcp.server','fastmcp.providers',
        'pydantic','pydantic.fields',
    ],
    excludes=['tkinter','setuptools','pip','wheel','test','tests',
              'unittest','_distutils_hack'],
    noarchive=True,
)
for _list in [a.datas, a.binaries, a.zipfiles, a.scripts]:
    _list[:] = [e for e in _list if not (isinstance(e, tuple) and '.dist-info' in str(e[0]))]
SKIP = ['torch','playwright','bitsandbytes','llvmlite','pyarrow',
        'pymupdf','grpc','numba','Cython','google','azure',
        'boto3','botocore','matplotlib','PIL','pandas',
        'scipy','sklearn','onnxruntime']
a.binaries = [b for b in a.binaries if not any(s in b[0].lower() for s in SKIP)]
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, a.binaries, a.zipfiles, a.datas,
          name='unity3d-mcp-backend', debug=False,
          strip=False, upx=False, upx_exclude=[],
          runtime_tmpdir=None, console=False)
