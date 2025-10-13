import configparser
import os

class PSpecError(Exception):
    pass

class PSpec:
    """
    Represents the pspec file structure.
    Supports:
      - [data] for files/folders to package
      - [control] (raw Debian format, supports multi-line continuation)
      - [instructions*] sections (merged for instructions file)
    """

    REQUIRED_CONTROL_KEYS = ["Package", "Version", "Architecture", "Maintainer", "Description"]

    def __init__(self, path):
        self.path = path
        self.parser = configparser.ConfigParser()
        self.parser.optionxform = str  # preserve case sensitivity
        self.parser.read(path)

        # validate required sections
        if "control" not in self.parser:
            raise PSpecError(f"Missing section 'control' in pspec {path}")
        if "data" not in self.parser:
            raise PSpecError(f"Missing section 'data' in pspec {path}")

        # validate control fields
        self.validate_control()

    # --- Data section ---
    @property
    def data(self):
        """
        Returns dict {target_relative_path: source_path}
        Supports files and folders
        """
        return dict(self.parser["data"])

    # --- Control section ---
    @property
    def control_text(self):
        """
        Returns raw lines for control file (Debian format)
        """
        if "control" not in self.parser:
            return []
        lines = []
        for key, value in self.parser.items("control"):
            value_lines = value.splitlines()
            lines.append(f"{key}: {value_lines[0]}")
            for vline in value_lines[1:]:
                lines.append(f" {vline}")  # Debian continuation line
        return lines

    def validate_control(self):
        """
        Check if all required Debian/NIPM fields are present.
        """
        lines = self.control_text
        keys_present = [line.split(":", 1)[0].strip() for line in lines if ":" in line]
        missing = [k for k in self.REQUIRED_CONTROL_KEYS if k not in keys_present]
        if missing:
            raise PSpecError(f"Missing required control fields: {missing}")

    # --- Instructions section ---
    @property
    def instructions(self):
        """
        Returns merged dict of all [instructions*] sections
        """
        instr = {}
        for section in self.parser.sections():
            if section.lower().startswith("instructions"):
                instr.update(dict(self.parser[section]))
        return instr

    # --- Helpers for type ---
    @property
    def is_eula(self):
        """
        Returns True if this pspec is an EULA package (XB-Plugin: eula).
        """
        for line in self.control_text:
            if line.lower().startswith("xb-plugin:") and "eula" in line.lower():
                return True
        return False

    @property
    def package_name(self):
        """
        Extracts the Package: field value
        """
        for line in self.control_text:
            if line.startswith("Package:"):
                return line.split(":", 1)[1].strip()
        return None

    @property
    def version(self):
        """
        Extracts the Version: field value
        """
        for line in self.control_text:
            if line.startswith("Version:"):
                return line.split(":", 1)[1].strip()
        return None
