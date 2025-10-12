import argparse
from functools import wraps
from . import __author__, __version__


def with_argparse(main_function):
    wraps(main_function)

    def wrapper():
        parser = argparse.ArgumentParser(
          description="Телефонный справочник",
          epilog="консольная версия"
        )

        parser.add_argument(
          '-v',
          '--version',
          'version',
          action='version',
          version=f'%(prog)s {__version__}',
          help='Версия пакета'
        )

        parser.add_argument(
          '--author',
          'author',
          action='store_true',
          help='Автор проекта'
        )
        args = parser.parse_args()

        if args.author:
            print(f'{__author__}')
            return

        if args.version:
            print(f'{__version__}')
            return

        return main_function()
    return wrapper
