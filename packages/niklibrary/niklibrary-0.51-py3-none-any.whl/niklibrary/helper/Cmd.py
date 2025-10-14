import os
import sys
from pathlib import Path

from nikassets.helper.Assets import Assets

from .F import F
import subprocess


class Cmd:
    commands_list = []
    adb_path = ['adb']
    apktool_version = "2.11.1"
    apktool_path = Assets.get(f"apktool_{apktool_version}.jar")
    if sys.platform.startswith('win32'):
        commands_list = ['cmd', '/c']
        adb_path = [Assets.adb_path]
    aapt_path = [Assets.aapt_path]
    if str(Assets.system_name).__eq__("Linux"):
        aapt_path = [Assets.aapt_path]
    elif str(Assets.system_name).__eq__("Darwin"):
        aapt_path = [Assets.aapt_path]
    sign_jar_path = Assets.get("NikGappsZipSigner.jar")
    COMMAND_ADB_DEVICES = adb_path + ["devices"]
    COMMAND_ADB_KILL_SERVER = adb_path + ["kill-server"]
    COMMAND_ADB_ROOT = adb_path + ["root"]
    COMMAND_ADB_REMOUNT = adb_path + ["remount"]
    COMMAND_ADB_PRODUCT_MODEL = adb_path + ["shell", "getprop", "ro.product.model"]
    COMMAND_ADB_PRODUCT_NAME = adb_path + ["shell", "getprop", "ro.product.name"]
    COMMAND_ADB_PRODUCT_DEVICE = adb_path + ["shell", "getprop", "ro.product.device"]
    COMMAND_ADB_PULL = adb_path + ["pull", "source", "destination"]
    COMMAND_ADB_PUSH = adb_path + ["push", "source", "destination"]
    COMMAND_LIST_PACKAGES = adb_path + ["shell", "pm", "list", "packages"]
    COMMAND_LIST_FILES = adb_path + ["shell", "ls", "-p", ""]
    COMMAND_LIST_FILES_RECURSIVELY = adb_path + ["shell", "ls", "-R", ""]
    COMMAND_LIST_PACKAGES_EXTENDED = adb_path + ["shell", "pm", "list", "packages", "-f"]
    COMMAND_LIST_PACKAGES_SYSTEM = adb_path + ["shell", "pm", "list", "packages", "-s"]
    COMMAND_PATH_PACKAGES = adb_path + ["shell", "pm", "path", "package"]
    COMMAND_AAPT_DUMP_BADGING = aapt_path + ["dump", "badging", "apkFilePath"]
    COMMAND_AAPT_DUMP_PACKAGENAME = aapt_path + ["dump", "packagename", "apkFilePath"]
    COMMAND_AAPT_DUMP_PERMISSIONS = aapt_path + ["dump", "permissions", "apkFilePath"]
    COMMAND_LIST_FILES_SU = adb_path + ["ls", "/data/app"]
    COMMAND_ADB_SHELL_SU = adb_path + ["shell", "su"]
    COMMAND_ANDROID_VERSION = adb_path + ["shell", "getprop", "ro.build.version.release"]
    COMMAND_DEVICE_ARCHITECTURE = adb_path + ["shell", "getprop", "ro.product.cpu.abi"]
    COMMAND_ADB_CONNECT_DEVICES = adb_path + ["connect", "IP"]
    COMMAND_SIGN_ZIP = ["java", "-jar", sign_jar_path, "file_path", sign_jar_path, "false"]
    COMMAND_BUILD_APK = ["java", "-jar", apktool_path, "b", "folder_name"]
    COMMAND_DECOMPILE_APK = ["java", "-jar", apktool_path, "d", "apk_path", "-o", "folder_name"]
    COMMAND_SIGN_APK = ["java", "-jar", Assets.get("apksigner.jar"), "sign", "--key", Assets.get("cert.pk8"), "--cert",
                        Assets.get("cert.x509.pem"), "-v", "outfile.apk"]
    COMMAND_ZIPALIGN_APK = ["zipalign", "-p", "-f", "-v", "4", "infile.apk", "outfile.apk"]
    COMMAND_ZIPALIGN_VERIFY = ["zipalign", "-c", "-v", "4", "outfile.apk"]

    def execute_adb_command(self, params):
        return self.execute_cmd(self.adb_path + params)

    def execute(self, command, capture_output=True, shell=False):
        try:
            command_to_execute = self.commands_list + command
            result = subprocess.run(command_to_execute, encoding="utf-8", capture_output=capture_output, text=True,
                                    shell=shell,
                                    check=True)
            return ['', result.stdout.split('\n'), True, result.returncode]
        except subprocess.CalledProcessError as e:
            return [e.stderr, e.stdout, False, e.returncode]
        except Exception as e:
            return [str(e), '', False, -1]

    def execute_cmd(self, command):
        command_to_execute = self.commands_list + command
        p = subprocess.run(command_to_execute, encoding="utf-8", universal_newlines=True, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
        if p.returncode == 0:
            return p.stdout.split('\n')
        else:
            exception_msg = "Exception occurred while executing " + str(command_to_execute) + " " + \
                            p.stderr.split("\n")[0]
            return [exception_msg, p.stdout]

    def adb_has_root_permissions(self):
        print("Checking for root permissions")
        output_line = self.execute_cmd(self.COMMAND_ADB_REMOUNT)
        if len(output_line) > 0:
            for line in output_line:
                if line.__contains__("Using a specified mount point") or line.__contains__("remount succeeded"):
                    return True
        return False

    def build_overlay(self, folder_name):
        print(f"Building {Path(folder_name).name} overlay")
        self.COMMAND_BUILD_APK[4] = folder_name
        built_apk = False
        output_line = self.execute_cmd(self.COMMAND_BUILD_APK)
        if len(output_line) > 0:
            for line in output_line:
                print(line)
                if line.__contains__("Built apk"):
                    built_apk = True
                    break
        apk_path = os.path.join(folder_name, "dist", f"{Path(folder_name).name}.apk")
        if built_apk and F.file_exists(apk_path):
            if self.sign_apk(apk_path):
                return self.zipalign_apk(apk_path)
        return ""

    def zipalign_apk(self, apk_path, sign_apk=True):
        print(f"Zipaligning {apk_path}")
        self.COMMAND_ZIPALIGN_APK[5] = apk_path
        aligned_apk_path = apk_path.replace(".apk", "-aligned.apk")
        self.COMMAND_ZIPALIGN_APK[6] = aligned_apk_path
        output_line = self.execute_cmd(self.COMMAND_ZIPALIGN_APK)
        if len(output_line) > 0:
            for line in output_line:
                print(line)
                if line.__contains__("Verification successful") or line.__contains__("Verification successful"):
                    if sign_apk and self.sign_apk(aligned_apk_path):
                        return aligned_apk_path
                    else:
                        return aligned_apk_path
        return ""

    def sign_apk(self, apk_path):
        print(f"Signing {Path(apk_path).name}")
        self.COMMAND_SIGN_APK[9] = apk_path
        output_line = self.execute_cmd(self.COMMAND_SIGN_APK)
        if len(output_line) > 0:
            for line in output_line:
                print(line)
                if line.__contains__("Signed"):
                    print(f"APK {apk_path} signed successfully!")
                    return True
        return False

    def decompile_apk(self, apk_path, output_folder):
        self.COMMAND_DECOMPILE_APK[4] = apk_path
        self.COMMAND_DECOMPILE_APK[6] = output_folder
        print(f"Decompiling {Path(apk_path).name} with command {self.COMMAND_DECOMPILE_APK}")
        output_line = self.execute_cmd(self.COMMAND_DECOMPILE_APK)
        if len(output_line) > 0:
            for line in output_line:
                print(line)
                if line.__contains__("Copying original files..."):
                    return True
        return False

    def established_device_connection_as_root(self):
        if self.adb_has_root_permissions():
            return True
        else:
            print("Killing Adb Server")
            self.execute_cmd(self.COMMAND_ADB_KILL_SERVER)
            self.execute_cmd(self.COMMAND_ADB_DEVICES)
            self.execute_cmd(self.COMMAND_ADB_ROOT)
            print("Checking for root permissions again")
            if self.adb_has_root_permissions():
                print("Acquiring root permissions")
                return True
        return False

    def get_package_path(self, package_name):
        self.COMMAND_PATH_PACKAGES[4] = package_name
        output_list = self.execute_cmd(self.COMMAND_PATH_PACKAGES)
        if output_list.__len__() == 1 and output_list[0].startswith("Exception occurred"):
            return ["Exception occurred"]
        return_list = []
        if output_list is not None:
            for path in output_list:
                if path.__contains__(":"):
                    return_list.append(path.split(':')[1])
        return return_list

    def get_package_files(self, package_folder):
        self.COMMAND_LIST_FILES_RECURSIVELY[4] = package_folder
        output_list = self.execute_cmd(self.COMMAND_LIST_FILES_RECURSIVELY)
        return_list = []
        if output_list is not None:
            for path in output_list:
                return_list.append(path)
        return return_list

    def get_package_files_recursively(self, package_folder, return_list):
        package_folder = str(package_folder).replace("\\", "/")
        if package_folder.endswith("/"):
            package_folder = package_folder[0:-1]
        self.COMMAND_LIST_FILES[4] = package_folder
        output_list = self.execute_cmd(self.COMMAND_LIST_FILES)
        if output_list is not None:
            for path in output_list:
                if path.__contains__(".") and not path.__contains__("base.dm"):
                    return_list.append(package_folder + '/' + path)
                elif path.endswith("/") and path != "oat/":
                    return_list = self.get_package_files_recursively(package_folder + '/' + path, return_list)
        return return_list

    def pull_package(self, source, destination):
        self.COMMAND_ADB_PULL[2] = source
        self.COMMAND_ADB_PULL[3] = destination
        output_list = self.execute_cmd(self.COMMAND_ADB_PULL)
        return_list = []
        if output_list is not None:
            for path in output_list:
                # Output needs to contain "1 file pulled" in it for successful execution
                return_list.append(path)
        return return_list

    def push_package(self, source, destination):
        self.COMMAND_ADB_PUSH[2] = source
        self.COMMAND_ADB_PUSH[3] = destination
        output_list = self.execute_cmd(self.COMMAND_ADB_PUSH)
        return_list = []
        if output_list is not None:
            for path in output_list:
                return_list.append(path)
        return return_list

    def file_exists(self, file_path):
        exists = False
        self.COMMAND_LIST_FILES[4] = file_path
        output_list = self.execute_cmd(self.COMMAND_LIST_FILES)
        if output_list is not None:
            for path in output_list:
                if path == file_path:
                    exists = True
                    break
        return exists

    def get_white_list_permissions(self, apk_path):
        self.COMMAND_AAPT_DUMP_PERMISSIONS[3] = apk_path
        result = self.execute(self.COMMAND_AAPT_DUMP_PERMISSIONS)
        return_list = set()
        if result[2]:
            keys = ["uses-permission", "permission"]
            for line in result[1]:
                if line.startswith(keys[0]):
                    return_list.add(line.split('\'')[1])
                elif line.startswith(keys[1]):
                    return_list.add(line.split(' ')[1])
        else:
            return_list.add("Exception: " + str(result[0]))
        return list(return_list)

    def get_package_name(self, apk_path):
        self.COMMAND_AAPT_DUMP_PERMISSIONS[3] = apk_path
        result = self.execute(self.COMMAND_AAPT_DUMP_PERMISSIONS)
        if result[2]:
            key = "package:"
            key_line = next((line for line in result[1] if line.startswith(key)), None)
            if key_line:
                value = key_line.split(" ")[1]
                return value
        else:
            return "Exception: Package Name Not Found"

    def get_package_version(self, apk_path):
        self.COMMAND_AAPT_DUMP_BADGING[3] = apk_path
        result = self.execute(self.COMMAND_AAPT_DUMP_BADGING)
        if result[2]:
            key = "versionName"
            key_line = next((line for line in result[1] if line.__contains__(key)), None)
            if key_line:
                parts = key_line.split()
                value = next((part.split('=')[1].strip("'") for part in parts if key in part), '')
                return value
        else:
            return "Exception: Package Name Not Found"

    def get_package_details(self, apk_path, key):
        self.COMMAND_AAPT_DUMP_BADGING[3] = apk_path
        result = self.execute(self.COMMAND_AAPT_DUMP_BADGING)
        if result[2]:
            key_line = next((line for line in result[1] if line.__contains__(key)), None)
            if key_line:
                parts = key_line.split()
                value = next((part for part in parts if key in part), '')
                return value.split('=')[1].strip("'")
        else:
            return f"Exception: {key} Not Found"

    def get_package_version_code(self, apk_path):
        self.COMMAND_AAPT_DUMP_BADGING[3] = apk_path
        result = self.execute(self.COMMAND_AAPT_DUMP_BADGING)
        if result[2]:
            key = "versionCode="
            key_line = next((line for line in result[1] if line.__contains__(key)), None)
            if key_line:
                parts = key_line.split()
                value = next((part.split('=')[1].strip("'") for part in parts if key in part), '')
                return value
        else:
            return "Exception: Package Version Code Not Found"

    def sign_zip_file(self, zip_path):
        zip_path = os.path.abspath(zip_path)
        self.COMMAND_SIGN_ZIP[3] = zip_path
        output_list = self.execute_cmd(self.COMMAND_SIGN_ZIP)
        return_list = []
        if output_list is not None:
            for path in output_list:
                return_list.append(path)
        return return_list
