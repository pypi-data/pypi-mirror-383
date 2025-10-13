import os
import shutil
import subprocess
import xml.etree.ElementTree as ET

from pynipkg.pspec import PSpec
from pynipkg.run_commands_utility import run_command_live

class NipkgBuilderError(Exception):
    pass

class NipkgBuilder:
    def __init__(self, pspec: PSpec, workspace_dir: str):
        self.pspec = pspec
        self.workspace = workspace_dir
        self.pkgroot = os.path.join(workspace_dir, "pkgroot")
        self.ctrl_dir = os.path.join(self.pkgroot, "control")
        self.ctrl_path = os.path.join(self.ctrl_dir, "control") 
        self.data_dir = os.path.join(self.pkgroot, "data")
        self.inst_path = os.path.join(self.pkgroot, "instructions")
        self.debfile = os.path.join(self.pkgroot, "debian-binary")

    def set_working_dir(self):
        os.chdir(self.workspace)

    # --- Workspace management ---
    def clean_workspace(self):
        if os.path.isdir(self.pkgroot):
            shutil.rmtree(self.pkgroot)
        os.makedirs(self.pkgroot)

    # --- Control file ---
    def make_control(self):
        lines = self.pspec.control_text
        if not lines:
            raise NipkgBuilderError("Control section in pspec is empty")
        os.makedirs(self.ctrl_dir, exist_ok=True)
        with open(self.ctrl_path, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(lines))

    # --- Debian-binary file ---
    def make_debian_binary(self):
        with open(self.debfile, "w", encoding="utf-8", newline="\n") as f:
            f.write("2.0\n")

    # --- Data folder ---
    def make_data(self):
        os.makedirs(self.data_dir, exist_ok=True)
        for target, src in self.pspec.data.items():
            src = os.path.abspath(src)
            dest = os.path.join(self.data_dir, target)
            if not os.path.exists(src):
                raise NipkgBuilderError(f"Source path does not exist: {src}")
            if os.path.isfile(src):
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                shutil.copy2(src, dest)
            elif os.path.isdir(src):
                os.makedirs(dest, exist_ok=True)
                for root, _, files in os.walk(src):
                    rel_root = os.path.relpath(root, src)
                    dest_root = os.path.join(dest, rel_root) if rel_root != "." else dest
                    os.makedirs(dest_root, exist_ok=True)
                    for file in files:
                        shutil.copy2(os.path.join(root, file), os.path.join(dest_root, file))
            else:
                raise NipkgBuilderError(f"Source path is not file or folder: {src}")

    # --- Instructions XML ---
    def make_instructions(self):
        # Skip instructions entirely for EULA-only packages
        if self.pspec.is_eula:
            return

        instr_dict = self.pspec.instructions
        if not instr_dict:
            return

        root = ET.Element("instructions")

        # Custom Executes
        custom_exes_el = ET.SubElement(root, "customExecutes")
        for key, val in instr_dict.items():
            if key.lower() in ["postinstall", "preinstall", "postuninstall", "preuninstall", "postallinstall", "postalluninstall"]:
                step = "uninstall" if "uninstall" in key.lower() else "install"
                schedule = ""
                if key.lower().startswith("pre"):
                    schedule = "pre"
                elif key.lower().startswith("postall"):
                    schedule = "postall"
                elif key.lower().startswith("post"):
                    schedule = "post"
                parts = [p.strip() for p in val.split(",")]
                exe_name = parts[0]
                args = []
                extra_attrs = {}
                for p in parts[1:]:
                    if "=" in p:
                        k, v = p.split("=", 1)
                        extra_attrs[k.strip()] = v.strip()
                    else:
                        args.append(p)
                attribs = {"step": step, "schedule": schedule, "exeName": exe_name}
                if args:
                    attribs["args"] = " ".join(args)
                attribs.update(extra_attrs)
                ET.SubElement(custom_exes_el, "customExecute", attrib=attribs)

        # Shortcuts
        shortcut_keys = [k for k in instr_dict.keys() if k.lower().startswith("shortcut")]
        shortcut_ids = set(k.split("_")[0] for k in shortcut_keys)
        for sid in shortcut_ids:
            target_key = f"{sid}_target"
            path_key = f"{sid}_path"
            if target_key in instr_dict and path_key in instr_dict:
                shortcut_el = ET.SubElement(root, "shortcut")
                ET.SubElement(shortcut_el, "destination", root="ProgramMenu", path=instr_dict[path_key])
                ET.SubElement(shortcut_el, "target", exeName=instr_dict[target_key])

        # Return codes
        for key, val in instr_dict.items():
            if key.lower().startswith("returncode"):
                code = key.split("_")[1]
                ET.SubElement(root, "returnCode", code=code, behavior=val)

        # Inline EULA reference (only if specified in pspec instructions)
        # if "eula" in instr_dict:
        #     ET.SubElement(root, "eula", file=instr_dict["eula"])

        import xml.dom.minidom as minidom

        # Convert the ElementTree root to a pretty-printed XML string
        xml_str = ET.tostring(root, encoding="utf-8")
        pretty_xml = minidom.parseString(xml_str).toprettyxml(indent="  ")

        # Remove the XML declaration (first line)
        pretty_lines = pretty_xml.splitlines()
        pretty_xml_no_decl = "\n".join(pretty_lines[1:])  # skip first line

        # Write to file without XML declaration
        with open(self.inst_path, "w", encoding="utf-8") as f:
            f.write(pretty_xml_no_decl)



    # --- Build package ---
    def build_package(self, output_nipkg_dir: str, nipkg_executable: str = "nipkg"):
        os.makedirs(output_nipkg_dir, exist_ok=True)
        cmd = [nipkg_executable, "pack", self.pkgroot, output_nipkg_dir]
        try:
            run_command_live(cmd)
        except subprocess.CalledProcessError as e:
            raise NipkgBuilderError(
                f"nipkg pack failed (exit {e.returncode}):\nstdout: {e.stdout}\nstderr: {e.stderr}"
            )
        return True

    def build_nsis_package(self):
        # nsis_command_dir = os.path.join(self.data_dir,"BootVolume", "lv-bots")
        # shutil.copy2("installer.nsi", os.path.join(nsis_command_dir, "installer.nsi"))
        cmd = ["makensis", "installer.nsi"]
        try:
            run_command_live(cmd)
        except subprocess.CalledProcessError as e:
            raise NipkgBuilderError(
                f"nipkg pack failed (exit {e.returncode}):\nstdout: {e.stdout}\nstderr: {e.stderr}"
            )
        return True

    # --- Full build ---
    def full_build(self, output_nipkg_dir: str, nipkg_executable: str = "nipkg"):
        self.set_working_dir()
        self.clean_workspace()
        self.make_control()
        self.make_debian_binary()
        self.make_instructions()
        self.make_data()
        return self.build_package(output_nipkg_dir, nipkg_executable)

    def full_nsis_build(self):
        self.set_working_dir()
        self.clean_workspace()
        self.make_control()
        self.make_debian_binary()
        self.make_instructions()
        self.make_data()
        return self.build_nsis_package()
