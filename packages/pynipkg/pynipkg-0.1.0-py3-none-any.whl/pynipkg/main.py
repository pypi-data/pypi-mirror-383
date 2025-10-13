import os
from pynipkg.pspec import PSpec
from pynipkg.builder import NipkgBuilder
import argparse

def build_from_pspec(pspec_path, 
                    workspace,
                    output_nipkg_dir=os.path.join(os.getcwd(), "packages"),
                    nipkg_exe="nipkg"
                    ):
    ps = PSpec(pspec_path)
    nb = NipkgBuilder(ps, workspace)
    nb.full_build(output_nipkg_dir, nipkg_exe)
    print(f"✅ Package Build Successful for {os.path.basename(pspec_path)} \n Output Directory: {output_nipkg_dir}\n")

# def build_nsis_from_pspec(pspec_path, 
#                     workspace,
#                     output_nipkg_dir=os.path.join(os.getcwd(), "packages"),
#                     nipkg_exe="nipkg"
#                     ):
#     ps = PSpec(pspec_path)
#     nb = NipkgBuilder(ps, workspace)
#     nb.full_nsis_build()
#     print(f"✅ Package Build Successful for {os.path.basename(pspec_path)} \n Output Directory: {output_nipkg_dir}\n")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("pspec", help="Path to pspec file")
    parser.add_argument("workspace",
                        help="Set working directory to build the package, temporary folder pkgroot will also be created in working directory for build purposes")
    parser.add_argument("--outnipkgdir",
                        default= str(os.path.join(os.getcwd(), "packages")),
                        help="Output .nipkg file path")
    parser.add_argument("--nipkgexe", 
                        default=r"C:\Program Files\National Instruments\NI Package Manager\nipkg.exe",
                        help="Path to nipkg executable")
    args = parser.parse_args()
    build_from_pspec(args.pspec, args.workspace, args.outnipkgdir, args.nipkgexe)

if __name__ == "__main__":
    main()
