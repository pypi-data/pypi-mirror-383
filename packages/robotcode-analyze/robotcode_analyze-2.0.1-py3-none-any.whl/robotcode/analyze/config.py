# ruff: noqa: RUF009
from dataclasses import dataclass
from enum import IntFlag
from typing import Iterable, List, Literal, Optional, Union

from robotcode.robot.config.model import BaseOptions, field
from robotcode.robot.diagnostics.workspace_config import (
    AnalysisDiagnosticModifiersConfig,
    AnalysisRobotConfig,
    WorkspaceAnalysisConfig,
)
from robotcode.robot.diagnostics.workspace_config import CacheConfig as WorkspaceCacheConfig


@dataclass
class ModifiersConfig(BaseOptions):
    """Modifiers configuration."""

    ignore: Optional[List[str]] = field(
        description="""\
            Specifies the diagnostics codes to ignore.

            Examples:

            ```toml
            [tool.robotcode-analyze.modifiers]
            ignore = ["VariableNotFound", "multiple-keywords"]
            ```
        """
    )
    extend_ignore: Optional[List[str]] = field(
        description="""
            Extend the diagnostics codes to ignore.

            Examples:

            ```toml
            [tool.robotcode-analyze.modifiers]
            extend_ignore = ["VariableNotFound", "multiple-keywords"]
            ```
        """
    )
    error: Optional[List[str]] = field(
        description="""
            Specifies the diagnostics codes to treat as errors.

            Examples:

            ```toml
            [tool.robotcode-analyze.modifiers]
            error = ["VariableNotFound", "multiple-keywords"]
            ```
        """
    )
    extend_error: Optional[List[str]] = field(
        description="""
            Extend the diagnostics codes to treat as errors.

            Examples:

            ```toml
            [tool.robotcode-analyze.modifiers]
            extend_error = ["VariableNotFound", "multiple-keywords"]
            ```
        """
    )
    warning: Optional[List[str]] = field(
        description="""
            Specifies the diagnostics codes to treat as warning.

            Examples:

            ```toml
            [tool.robotcode-analyze.modifiers]
            warning = ["VariableNotFound", "multiple-keywords"]
            ```
        """
    )
    extend_warning: Optional[List[str]] = field(
        description="""
            Extend the diagnostics codes to treat as warning.

            Examples:

            ```toml
            [tool.robotcode-analyze.modifiers]
            extend_warning = ["VariableNotFound", "multiple-keywords"]
            ```
        """
    )
    information: Optional[List[str]] = field(
        description="""
            Specifies the diagnostics codes to treat as information.

            Examples:

            ```toml
            [tool.robotcode-analyze.modifiers]
            information = ["VariableNotFound", "multiple-keywords"]
            ```
        """
    )
    extend_information: Optional[List[str]] = field(
        description="""
            Extend the diagnostics codes to treat as information.

            Examples:

            ```toml
            [tool.robotcode-analyze.modifiers]
            extend_information = ["VariableNotFound", "multiple-keywords"]
            ```
        """
    )
    hint: Optional[List[str]] = field(
        description="""
            Specifies the diagnostics codes to treat as hint.

            Examples:

            ```toml
            [tool.robotcode-analyze.modifiers]
            hint = ["VariableNotFound", "multiple-keywords"]
            ```
        """
    )
    extend_hint: Optional[List[str]] = field(
        description="""
            Extend the diagnostics codes to treat as hint.

            Examples:

            ```toml
            [tool.robotcode-analyze.modifiers]
            extend_hint = ["VariableNotFound", "multiple-keywords"]
            ```
        """
    )


@dataclass
class CacheConfig(BaseOptions):
    """Cache configuration."""

    cache_dir: Optional[str] = field(description="Path to the cache directory.")

    ignored_libraries: Optional[List[str]] = field(
        description="""\
            Specifies the library names that should not be cached.
            This is useful if you have a dynamic or hybrid library that has different keywords depending on
            the arguments. You can specify a glob pattern that matches the library name or the source file.

            Examples:
            - `**/mylibfolder/mylib.py`
            - `MyLib`\n- `mylib.subpackage.subpackage`

            For robot framework internal libraries, you have to specify the full module name like
            `robot.libraries.Remote`.
            """,
    )
    extend_ignored_libraries: Optional[List[str]] = field(description="Extend the ignored libraries setting.")

    ignored_variables: Optional[List[str]] = field(
        description="""\
            Specifies the variable files that should not be cached.
            This is useful if you have a dynamic or hybrid variable files that has different variables
            depending on the arguments. You can specify a glob pattern that matches the variable module
            name or the source file.

            Examples:
            - `**/variables/myvars.py`
            - `MyVariables`
            - `myvars.subpackage.subpackage`
            """,
    )
    extend_ignored_variables: Optional[List[str]] = field(description="Extend the ignored variables setting.")

    ignore_arguments_for_library: Optional[List[str]] = field(
        description="""\
            Specifies a list of libraries for which arguments will be ignored during analysis.
            This is usefull if you have library that gets variables from a python file as arguments that contains
            complex data like big dictionaries or complex objects that **RobotCode** can't handle.
            You can specify a glob pattern that matches the library name or the source file.

            Examples:
            - `**/mylibfolder/mylib.py`
            - `MyLib`\n- `mylib.subpackage.subpackage`

            If you change this setting, you may need to run the command
            `RobotCode: Clear Cache and Restart Language Servers`.

            _Ensure your library functions correctly without arguments e.g. by defining default
            values for all arguments._
        """
    )
    extend_ignore_arguments_for_library: Optional[List[str]] = field(
        description="Extend the ignore arguments for library settings."
    )


class ExitCodeMask(IntFlag):
    NONE = 0
    ERROR = 1
    WARN = 2
    WARNING = WARN
    INFO = 4
    INFORMATION = INFO
    HINT = 8
    ALL = ERROR | WARN | INFO | HINT

    @staticmethod
    def parse(value: Union[Iterable[str], str, None]) -> "ExitCodeMask":
        if value is None:
            return ExitCodeMask.NONE

        flags = ExitCodeMask(0)
        for entry in value:
            for part_orig in entry.split(","):
                part = part_orig.strip().upper()
                if part:
                    try:
                        flags |= ExitCodeMask[part]
                    except KeyError as e:
                        raise KeyError(f"Invalid exit code mask value: {part_orig}") from e
        return flags


ExitCodeMaskLiteral = Literal["error", "warn", "warning", "info", "information", "hint", "all"]
ExitCodeMaskList = List[ExitCodeMaskLiteral]


@dataclass
class CodeConfig(BaseOptions):
    """robotcode-analyze code configuration."""

    exit_code_mask: Optional[ExitCodeMaskList] = field(
        description="""\
            Specifies the exit code mask for the code analysis.
            This is useful if you want to ignore certain types of diagnostics in the result code.

            Examples:
            ```toml
            [tool.robotcode-analyze.code]
            exit_code_mask = ["error", "warn"]
            ```
            """,
    )
    extend_exit_code_mask: Optional[ExitCodeMaskList] = field(description="Extend the exit code mask setting.")


@dataclass
class AnalyzeConfig(BaseOptions):
    """robotcode-analyze configuration."""

    code: Optional[CodeConfig] = field(
        description="""\
            Defines the code analysis configuration.

            Examples:

            ```toml
            [tool.robotcode-analyze.code]
            exit_code_mask = "error|warn"
            ```
        """
    )
    extend_code: Optional[CodeConfig] = field(description="Extend the code analysis configuration.")

    modifiers: Optional[ModifiersConfig] = field(
        description="""\
            Defines the modifiers for the analysis.

            Examples:

            ```toml
            [tool.robotcode-analyze.modifiers]
            ignore = ["VariableNotFound"]
            hint = ["KeywordNotFound"]
            information = ["MultipleKeywords"]
            ```
        """
    )
    extend_modifiers: Optional[ModifiersConfig] = field(
        description="""\
            Extends the modifiers for the analysis.

            Examples:

            ```toml
            [tool.robotcode-analyze.extend_modifiers]
            ignore = ["VariableNotFound"]
            extend-hint = ["KeywordNotFound"]
            extend-information = ["MultipleKeywords"]
            ```
        """
    )

    cache: Optional[CacheConfig] = field(description="Defines the cache configuration.")
    extend_cache: Optional[CacheConfig] = field(description="Extend the cache configuration.")

    exclude_patterns: Optional[List[str]] = field(
        description="Specifies glob patterns for excluding files and folders from analysing by the language server.",
    )
    extend_exclude_patterns: Optional[List[str]] = field(description="Extend the exclude patterns.")

    global_library_search_order: Optional[List[str]] = field(
        description="""\
            Specifies a global [search order](https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#specifying-explicit-priority-between-libraries-and-resources)
            for libraries and resources.
            This is usefull when you have libraries containing keywords with the same name. **RobotCode** is unable to
            analyze the library search order in a file specified with
                [`Set Library Search Order`](https://robotframework.org/robotframework/latest/libraries/BuiltIn.html#Set%20Library%20Search%20Order),
            so you can define a global order here. Just make sure to call the `Set Library Search Order`
            keyword somewhere in your robot file or internally in your library.
        """,
    )
    extend_global_library_search_order: Optional[List[str]] = field(
        description="Extend the global library search order setting."
    )

    load_library_timeout: Optional[int] = field(
        description="""\
            Specifies the timeout in seconds for loading (importing) libraries and variable files during
            analysis. Increase this if your libraries perform heavy initialization (network calls, large
            dependency graphs, model loading, etc.).

            Must be > 0 when set. If you omit this key, RobotCode will instead look for the environment
            variable `ROBOTCODE_LOAD_LIBRARY_TIMEOUT`; otherwise it will use the internal default `10`.

            Examples:

            ```toml
            [tool.robotcode-analyze]
            # Fast fail if libraries normally import in < 2s
            load_library_timeout = 5
            ```

            ```toml
            [tool.robotcode-analyze]
            # Allow heavy bootstrap (e.g. Selenium + large resource trees)
            load_library_timeout = 30
            ```

            ```toml
            [tool.robotcode-analyze]
            # Omit to use default
            # load_library_timeout = 15
            ```
        """,
    )

    def to_workspace_analysis_config(self) -> WorkspaceAnalysisConfig:
        return WorkspaceAnalysisConfig(
            exclude_patterns=self.exclude_patterns or [],
            cache=(
                WorkspaceCacheConfig(
                    # TODO savelocation
                    ignored_libraries=self.cache.ignored_libraries or [],
                    ignored_variables=self.cache.ignored_variables or [],
                    ignore_arguments_for_library=self.cache.ignore_arguments_for_library or [],
                )
                if self.cache is not None
                else WorkspaceCacheConfig()
            ),
            robot=AnalysisRobotConfig(
                global_library_search_order=self.global_library_search_order or [],
                load_library_timeout=self.load_library_timeout,
            ),
            modifiers=(
                AnalysisDiagnosticModifiersConfig(
                    ignore=self.modifiers.ignore or [],
                    error=self.modifiers.error or [],
                    warning=self.modifiers.warning or [],
                    information=self.modifiers.information or [],
                    hint=self.modifiers.hint or [],
                )
                if self.modifiers is not None
                else AnalysisDiagnosticModifiersConfig()
            ),
        )
