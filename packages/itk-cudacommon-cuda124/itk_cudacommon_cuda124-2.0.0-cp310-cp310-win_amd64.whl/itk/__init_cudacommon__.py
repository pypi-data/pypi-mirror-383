"""""" # start delvewheel patch
def _delvewheel_patch_1_10_0():
    import os
    if os.path.isdir(libs_dir := os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'itk_cudacommon_cuda124.libs'))):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_10_0()
del _delvewheel_patch_1_10_0
# end delvewheel patch

import sys
import importlib

itk_module = sys.modules["itk"]
cuda_submodules = ["itk.itkCudaImageFromImage", "itk.itkCudaImageFromCudaArray"]

for mod_name in cuda_submodules:
    mod = importlib.import_module(mod_name)
    for a in dir(mod):
        if a[0] != "_":
            setattr(itk_module, a, getattr(mod, a))
