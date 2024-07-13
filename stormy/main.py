#!/usr/bin/env python

"""
A simple and user-friendly CLI to interact with your Lego Mindstorms NXT 2.0 Brick
"""

import typer
from rich import pretty, box
from rich.console import Console
from rich.table import Table
import pathlib
import os

import nxt.locator
import nxt.motor
import nxt.error
import nxt.brick

pretty.install()
console = Console()
app = typer.Typer(name="stormy", short_help="A simple and user-friendly CLI to interact with your Lego Mindstorms NXT "
                                            "2.0 Brick", invoke_without_command=False)


def print_warning(message: str):
    """
    Print a formatted warning message.

    Args:
       message (str): The message to be printed.

    Returns:
       None
    """
    console.print(f"⚠ {message}", style="bold yellow")


def print_error(message: str):
    """
    Print a formatted error message.

    Args:
       message (str): The message to be printed.

    Returns:
       None
    """
    console.print(f"👿 {message}", style="bold red")


def is_file_exist(brick: nxt.brick.Brick, file_name: str):
    """
    Check if a file exists in the NXT brick.

    Args:
       brick (nxt.brick.Brick): The NXT brick object.
       file_name (str): The file name to be checked.

    Returns:
       True: if the file exists.
       False: if the file does not exist.
    """
    try:
        brick.file_find_first(file_name)
        return True
    except nxt.error.FileNotFoundError:
        return False


def get_file_info(brick: nxt.brick.Brick, file_name: str):
    """
    get file information from the NXT brick.

    Args:
       brick (nxt.brick.Brick): The NXT brick object.
       file_name (str): The file name.

    Returns:
       tuple[int, str, int]: if success - [handle, file_name, size]
       raises: nxt.error.FileNotFoundError when file is not found.
    """
    try:
        file = brick.file_find_first(file_name)
        return file
    except nxt.error.FileNotFoundError as e:
        raise nxt.error.FileNotFoundError


def can_proceed():
    answer = ""
    attempts = 3
    cpt = 1
    while answer not in ["y", "n"] and cpt <= attempts:
        answer = input(f"🚦 [{cpt}/{attempts}] - Do you want to proceed [Y/N]? ").lower()
        cpt = cpt + 1

    if answer == "y":
        return True
    else:
        return False


def get_file_type(file_name: str):
    """
    get file type details based on the extension.

    Args:
       file_name (str): The file name.

    Returns:
       str: file type description
    """
    ext = pathlib.Path(file_name).suffix.lower().replace('.', '')
    if ext == 'rxe':
        return "Executable program"
    elif ext == 'rtm':
        return "Built-in try me program"
    elif ext == 'rso':
        return "Sound file"
    elif ext == 'sys':
        return "Internal firmware file"
    elif ext == 'rpg':
        return "5-step programs created using the 'NXT Program' UI on the NXT brick"
    elif ext == 'ric':
        return "Image files used with the NXTDrawPicture syscall method in .RXE programs"
    elif ext == 'cal':
        return "Sensor calibration file"
    elif ext == 'txt':
        return "ASCII text file using carriage return/line feed (CR/LF, Windows) end-of-line convention"
    elif ext == 'log':
        return "ASCII text file, created by the NXT data logging functionality"
    else:
        return "Unknown file type"


@app.command(help="Get the lego Mindstorms NXT 2.0 brick's details")
def get_brick_info():
    """
    get information about the NXT brick.

    Args:
       None

    Returns:
       None
       raises: nxt.locator.BrickNotFoundError if no NXT Brick was detected.
    """
    console.print("🔎 Looking for the NXT brick")
    try:
        with nxt.locator.find() as brick:
            table = Table(show_header=True, title=console.print("🤖 Brick Information", style="cyan bold"),
                          box=box.ROUNDED,
                          show_lines=False, style="blue")
            table.add_column("Property", no_wrap=True)
            table.add_column("value", no_wrap=True)
            table.add_row("Brick name", brick.get_device_info()[0])
            table.add_row("Brick mac addr", brick.get_device_info()[1])
            table.add_row("Bluetooth signal strength", str(brick.get_device_info()[2]))
            table.add_row("Free memory", str(brick.get_device_info()[3]))

            table.add_row("Protocol version",
                          (str(brick.get_firmware_version()[0][0]) + "." + str(brick.get_firmware_version()[0][1])))
            table.add_row("Firmware version",
                          (str(brick.get_firmware_version()[1][0]) + "." + str(brick.get_firmware_version()[1][1])))
            table.add_row("Battery charge level ", (str(brick.get_battery_level()) + " mv"))
            console.print(table)
    except Exception as e:
        print_error(f"{e}")


@app.command(help="List all available files in the lego Mindstorms NXT 2.0 brick")
def list_brick_files():
    """
    list all files in the NXT brick.

    Args:
       None

    Returns:
       None
       raises: nxt.locator.BrickNotFoundError if no NXT Brick was detected.
    """
    console.print("🔎 Looking for the NXT brick")
    try:
        with nxt.locator.find() as brick:
            files = brick.find_files("*.*")
            files = sorted(files, key=lambda x: x[0])
            table = Table(show_header=True, title=console.print("📑 Files Information", style="cyan bold"),
                          box=box.ROUNDED,
                          show_lines=False, style="blue")
            table.add_column("Name", no_wrap=True)
            table.add_column("Type", no_wrap=True)
            table.add_column("Size", no_wrap=True)
            for (name, size) in files:
                table.add_row(str(name), get_file_type(name), str(size))
            console.print(table)
    except Exception as e:
        print_error(f"{e}")


@app.command(help="Delete a file form the lego Mindstorms NXT 2.0 brick")
def delete_file(file: str):
    """
    get information about the NXT brick.

    Args:
       file(str): The name of the file to delete

    Returns:
       None
       raises: Exception if any error during the process.
    """
    console.print("🔎 Looking for the NXT brick")
    try:
        with nxt.locator.find() as brick:
            if not is_file_exist(brick, file):
                raise nxt.error.FileNotFoundError(f"the file <{file}> does not exist")

            file_data = get_file_info(brick, file)
            console.print(f"✔ Founded file <{file_data[1]}> with size <{file_data[2]}>")
            if can_proceed():
                brick.file_delete(file)
                console.print(f"🧽 the file <{file}> was deleted successfully")
            else:
                console.print("👾 Aborted")
    except Exception as e:
        print_error(f"{e}")


@app.command(help="Upload a file from your local computer into the lego Mindstorms NXT 2.0 brick")
def upload_file(file: str):
    """
    upload a file to the NXT brick.

    Args:
       file(str): The name of the file to upload

    Returns:
       None
       raises: Exception if any error during the process.
    """
    console.print("🔎 Looking for the NXT brick")
    try:
        with nxt.locator.find() as brick:
            if not os.path.isfile(file):
                print_error(f"the file <{file}> does not exist on your local computer")
                return

            if is_file_exist(brick, file):
                print_warning(f"the file <{file}> already exist in the NXT Brick. if you choose to continue, the file "
                              f"in the NXT Brick will be [red]deleted[/red]")
                if not can_proceed():
                    console.print("👾 Aborted")
                    return

                brick.file_delete(file)
                console.print(f"🧽 the file <{file}> was deleted successfully from your NXT Brick")

            console.print(f"📖 Opening <{file}> on your local computer for read")
            src_file = open(file, 'rb')

            src_file_stats = os.stat(file)

            console.print(f"📝 Opening <{file}> on your NXT Brick for write")
            dst_file = brick.open_file(name=file, mode='wb', size=src_file_stats.st_size)

            dst_file.write(src_file.read())

            console.print(f"🚪 Closing the NXT Brick file")
            dst_file.close()
            console.print(f"🚪 Closing the local file")
            src_file.close()

            console.print(f"📑 The File <{file}> was successfully copied into the NXT Brick")

    except Exception as e:
        print_error(f"{e}")


@app.command(help="Download a file from the lego Mindstorms NXT 2.0 brick to your local computer")
def download_file(file: str):
    """
    download a file from the NXT brick.

    Args:
       file(str): The name of the file to download

    Returns:
       None
       raises: Exception if any error during the process.
    """
    console.print("🔎 Looking for the NXT brick")
    try:
        with nxt.locator.find() as brick:
            if not is_file_exist(brick, file):
                print_error(f"the file <{file}> does not exist in the NXT Brick.")
                return

            if os.path.isfile(file):
                print_warning(f"the file <{file}> already exist in your local computer. if you choose to continue, "
                              f"the file in your local computer will be [red]deleted[/red]")
                if not can_proceed():
                    console.print("👾 Aborted")
                    return

                os.remove(file)
                console.print(f"🧽 the file <{file}> was successfully deleted from your local computer")

            console.print(f"📖 Opening <{file}> on your NXT Brick for read")
            src_file = brick.open_file(name=file, mode='rb')

            console.print(f"📝 Opening <{file}> on your local computer for write")
            dst_file = open(file, 'wb')

            dst_file.write(src_file.read())

            console.print(f"🚪 Closing the NXT Brick file")
            src_file.close()
            console.print(f"🚪 Closing the local file")
            dst_file.close()

            console.print(f"📑 The File <{file}> was successfully copied to your local computer")

    except Exception as e:
        print_error(f"{e}")


@app.command(help="Change the lego Mindstorms NXT 2.0 brick's name to a new one")
def set_brick_name(name: str):
    """
    set or update the NXT brick's name.

    Args:
       name(str): the name of the brick.

    Returns:
       None
       raises: Exception if any error during the process.
    """
    console.print("🔎 Looking for the NXT brick")
    try:
        with nxt.locator.find() as brick:
            brick.set_brick_name(name)
            console.print(f"🤖 Updated the NXT Brick name to <{name}>", style="bold green")
    except Exception as e:
        print_error(f"{e}")


if __name__ == "__main__":
    app()
