call "C:\Program Files (x86)\Microsoft Visual Studio 10.0\VC\vcvarsall.bat" x86
cl /Od /MD /Zi %1 /link /pdbaltpath:%%_PDB%%
