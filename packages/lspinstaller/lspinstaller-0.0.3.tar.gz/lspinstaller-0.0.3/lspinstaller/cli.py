import argparse
from dataclasses import dataclass
import os
import shutil
import time

from lspinstaller.config import load_config
from lspinstaller.constants import LSP_HOME
from lspinstaller.resolver.resolver import resolve
from .data import sources

class Arguments(argparse.Namespace):
    packages: list[str] | None


def run_list(_args):
    print(f"There are {len(sources)} available servers.")
    print()
    print('   {0:<30} How installed'.format("Name in lspinstaller"))
    for (name, data) in sources.items():
        builder = f" * {name:<30} "
        if ("github" in data):
            builder += f"via GitHub: {data['github']['fragment']}"
        elif ("npm" in data):
            builder += f"via npm: {data['npm']['package']}"
        else:
            builder += "Unknown source. Someone added a type without updating list"
        print(builder)

def run_install(args):
    assert args.packages is not None
    print(f"Installing: {', '.join(args.packages)}")

    config = load_config()

    for package in args.packages:
        if not package in sources:
            print(
                f"{package} is not a known lsp. See lspinstaller list for the available LSPs"
            )
            exit(-1)
        elif package in config.packages:
            print(
                f"{package} has already been installed. Use update instead"
            )
            exit(-1)

    # This is not inlined into the previous for loop intentionally. 
    # The previous loop is just validation, and gives much more rapid feedback
    # than a unified loop would be able to do.
    for package in args.packages:
        spec = sources[package]

        if "binary" in spec:
            output_path = os.path.join(
                LSP_HOME,
                package
            )
            if os.path.exists(
                output_path
            ):
                print(f"WARNING: {output_path} already exists.")
                print("This is likely a weird state artefact. The folder will now be removed before the install is attempted")
                print("If this is a mistake, press CTRL-C to abort NOW!")

                time.sleep(10)

                shutil.rmtree(
                    output_path
                )

        resolve(package, spec, config)
    config.commit()


def run_update(_args):
    pass

def start_cli():
    parser = argparse.ArgumentParser(
        prog="lspinstaller",
        description="Installs (some) LSP servers",
        epilog="lspinstaller is licensed under the MIT license: https://codeberg.org/LunarWatcher/lspinstaller/src/branch/master/LICENSE",
    )

    subs = parser.add_subparsers(required=True)
    cmd_list = subs.add_parser(
        "list",
        help="List the available LSP servers"
    )
    cmd_list.set_defaults(func=run_list)

    cmd_install = subs.add_parser(
        "install",
        help="Install an LSP server"
    )
    cmd_install.add_argument(
        "packages",
        nargs="+",
        help="The packages to install",
    )
    cmd_install.set_defaults(func=run_install)

    cmd_update = subs.add_parser(
        "update",
        help="Updates all LSP servers"
    )
    cmd_update.set_defaults(func=run_update)

    args: Arguments = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    start_cli()
