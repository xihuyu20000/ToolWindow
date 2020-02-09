from cx_Freeze import setup, Executable
import sys

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="爬虫工具",
    version="1.0",
    description="交流QQ群 692711347",
    author="吴超",
    executables=[Executable("ToolWindow_main.py", base=base, targetName="SpiderTool20200210.exe")])