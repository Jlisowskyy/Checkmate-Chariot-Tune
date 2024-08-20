class CliTranslator:
    _args: list[str]

    def __init__(self):
        pass

    def parse_args(self, args: list[str]) -> None:
        try:
            self._parse_args_internal(args)
        except Exception as e:
            print(f"[ ERROR ] During argument parsing error occurred: {e}")


    def parse_stdin(self) -> None:
        pass


    def _parse_args_internal(self, args: list[str]) -> None:
        index = 0
        self._args = args

        while index < len(args):
            index = self._execute_command(index)

    def _execute_command(self, index: int) -> int:
        return index