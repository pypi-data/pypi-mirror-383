import fnmatch
import glob
import importlib
import os
import re
import shutil
import traceback
import typing
from textwrap import dedent

from nbconvert.exporters import Exporter, NotebookExporter
from nbconvert.exporters.exporter import ResourcesDict
from nbconvert.writers import FilesWriter
from traitlets import Any, Bool, Instance, Integer, List, TraitError, Type, default, validate
from traitlets.config import LoggingConfigurable

from grader_service.api.models.assignment_settings import AssignmentSettings
from grader_service.convert.gradebook.gradebook import Gradebook
from grader_service.convert.nbgraderformat import SchemaTooNewError, SchemaTooOldError
from grader_service.convert.nbgraderformat.common import ValidationError
from grader_service.convert.preprocessors.execute import UnresponsiveKernelError


class GraderConvertException(Exception):
    pass


class BaseConverter(LoggingConfigurable):
    notebooks = List([])
    writer = Instance(FilesWriter)
    exporter = Instance(Exporter)
    exporter_class = Type(NotebookExporter, klass=Exporter).tag(config=True)
    preprocessors = List([])

    force = Bool(False, help="Whether to overwrite existing files").tag(config=True)

    ignore = List(
        [".ipynb_checkpoints", "*.pyc", "__pycache__", ".git", "grader_config.py"],
        help=dedent(
            """
            List of file names or file globs.
            Upon copying directories recursively, matching files and
            directories will be ignored.
            """
        ),
    ).tag(config=True)

    pre_convert_hook = Any(
        None,
        config=True,
        allow_none=True,
        help=dedent(
            """
        An optional hook function that you can implement to do some
        bootstrapping work before converting. 
        This function is called before the notebooks are converted
        and should be used for specific converters such as Autograde,
        GenerateAssignment or GenerateFeedback.

        It will be called as (all arguments are passed as keywords)::

            hook(notebooks=notebooks, input_dir=input_dir, output_dir=output_dir)
        """
        ),
    )

    post_convert_hook = Any(
        None,
        config=True,
        allow_none=True,
        help=dedent(
            """
        An optional hook function that you can implement to do some
        work after converting. 
        This function is called after the notebooks are converted
        and should be used for specific converters such as Autograde,
        GenerateAssignment or GenerateFeedback.

        It will be called as (all arguments are passed as keywords)::

            hook(notebooks=notebooks, input_dir=input_dir, output_dir=output_dir)
        """
        ),
    )

    permissions = Integer(
        help=dedent(
            """
            Permissions to set on files output by nbgrader. The default is
            generally read-only (444), with the exception of nbgrader
            generate_assignment and nbgrader generate_feedback, in which case
            the user also has write permission.
            """
        )
    ).tag(config=True)

    @default("permissions")
    def _permissions_default(self) -> int:
        return 664

    @validate("pre_convert_hook")
    def _validate_pre_convert_hook(self, proposal):
        value = proposal["value"]
        if isinstance(value, str):
            module, function = value.rsplit(".", 1)
            value = getattr(importlib.import_module(module), function)
        if not callable(value):
            raise TraitError("pre_convert_hook must be callable")
        return value

    @validate("post_convert_hook")
    def _validate_post_convert_hook(self, proposal):
        value = proposal["value"]
        if isinstance(value, str):
            module, function = value.rsplit(".", 1)
            value = getattr(importlib.import_module(module), function)
        if not callable(value):
            raise TraitError("post_convert_hook must be callable")
        return value

    # Override this method to allow certain traitlets to be overridden
    # def _allowed_override_keys(self):
    #     return {
    #         'ClearSolutions': ['code_stub'],
    #         'ClearHiddenTests': ['begin_test_delimeter', 'end_test_delimeter'],
    #     }

    # Sanitize config to only allow certain keys to be overridden
    # def _sanitize_config(self, raw_config, allowed_keys):
    #     sanitized_config = Config()
    #     for key, value in raw_config.items():
    #         if key in allowed_keys:
    #             if isinstance(value, Config):
    #                 sanitized_config[key] = self._sanitize_config(value, allowed_keys[key])
    #             else:
    #                 sanitized_config[key] = value
    #     return sanitized_config

    def __init__(
        self,
        input_dir: str,
        output_dir: str,
        file_pattern: str,
        assignment_settings: AssignmentSettings,
        **kwargs: typing.Any,
    ) -> None:
        super(BaseConverter, self).__init__(**kwargs)
        self._input_directory = os.path.abspath(os.path.expanduser(input_dir))
        self._output_directory = os.path.abspath(os.path.expanduser(output_dir))
        self._file_pattern = file_pattern
        self._assignment_settings = assignment_settings
        if self.parent and hasattr(self.parent, "logfile"):
            self.logfile = self.parent.logfile
        else:
            self.logfile = None

    # register pre-processors to self.exporter
    # self.convert_notebooks() converts all notebooks in the CourseDir
    # notebooks are set in init_notebooks()
    def start(self) -> None:
        self.init_notebooks()
        self.writer = FilesWriter(parent=self, config=self.config)
        self.exporter: Exporter = self.exporter_class(parent=self, config=self.config)
        for pp in self.preprocessors:
            self.exporter.register_preprocessor(pp)
        currdir = os.getcwd()
        os.chdir(self._output_directory)
        try:
            self.convert_notebooks()
        finally:
            os.chdir(currdir)

    @default("classes")
    def _classes_default(self):
        classes = super(BaseConverter, self)._classes_default()
        classes.append(FilesWriter)
        classes.append(Exporter)
        for pp in self.preprocessors:
            if len(pp.class_traits(config=True)) > 0:
                classes.append(pp)
        return classes

    # returns string that can be used for globs
    def _format_source(self, escape: bool = False) -> str:
        source = os.path.join(self._input_directory, self._file_pattern)
        if escape:
            return re.escape(source)
        else:
            return source

    def init_notebooks(self) -> None:
        self.notebooks = []
        notebook_glob = self._format_source()
        self.notebooks = glob.glob(notebook_glob)
        if len(self.notebooks) == 0:
            self.log.warning("No notebooks were matched by '%s'", notebook_glob)

    def init_single_notebook_resources(
        self, notebook_filename: str
    ) -> typing.Dict[str, typing.Any]:
        resources = {}
        resources["unique_key"] = os.path.splitext(os.path.basename(notebook_filename))[0]
        resources["output_files_dir"] = "%s_files" % os.path.basename(notebook_filename)
        resources["output_json_file"] = "gradebook.json"
        resources["output_json_path"] = os.path.join(
            self._output_directory, resources["output_json_file"]
        )
        resources["nbgrader"] = dict()  # support nbgrader pre-processors
        return resources

    def write_single_notebook(self, output: str, resources: ResourcesDict) -> None:
        # configure the writer build directory
        self.writer.build_directory = self._output_directory

        # write out the results
        self.writer.write(output, resources, notebook_name=resources["unique_key"])

    def init_destination(self) -> bool:
        """Initialize the destination for an assignment. Returns whether the
        assignment should actually be processed or not (i.e. whether the
        initialization was successful).

        """
        dest = self._output_directory
        source = self._input_directory

        # if we have specified --force, then always remove existing stuff
        if self.force:
            return True

        # if files exist in the destination and force is not specified return false
        src_files = glob.glob(self._format_source())
        for src in src_files:
            file_name = os.path.join(dest, os.path.relpath(src, source))
            if os.path.exists(os.path.join(dest, file_name)):
                return False
        return True

    def copy_unmatched_files(self, gb: Gradebook):
        """
        Copy the files from source to the output directory that match the allowed file patterns,
        excluding files and directories that match any of the ignore patterns.
        :return: None
        """
        dst = self._output_directory
        src = self._input_directory

        allowed_files = self._assignment_settings.allowed_files
        ignore_patterns = self.ignore  # List of patterns to ignore

        if allowed_files is None:
            self.log.info(
                "No additional file patterns specified; only copying files included "
                "in release version"
            )
            files_patterns = gb.get_extra_files()
        else:
            self.log.info(f"Found additional file patterns: {allowed_files}")
            files_patterns = allowed_files + gb.get_extra_files()

        copied_files = []

        def matches_allowed_patterns(file_path):
            """
            Check if a file matches any of the allowed glob patterns.
            """
            return any(fnmatch.fnmatch(file_path, pattern) for pattern in files_patterns)

        def is_ignored(file_path):
            """
            Check if a file or directory matches any of the ignore glob patterns.
            """
            # Ensure to check both files and directories
            return any(fnmatch.fnmatch(file_path, pattern) for pattern in ignore_patterns)

        self.log.info(
            f"Copying files from {src} to {dst} that match allowed patterns "
            f"and don't match ignored patterns."
        )

        for root, dirs, files in os.walk(src, topdown=True):
            # Exclude directories that match ignore patterns
            dirs[:] = [
                d for d in dirs if not is_ignored(d)
            ]  # Modify dirs in-place to ignore unwanted dirs

            for file in files:
                abs_file_path = os.path.join(root, file)
                rel_file_path = os.path.relpath(abs_file_path, src)

                if matches_allowed_patterns(rel_file_path) and not is_ignored(rel_file_path):
                    dst_file_path = os.path.join(dst, rel_file_path)

                    # Ensure the destination directory exists
                    os.makedirs(os.path.dirname(dst_file_path), exist_ok=True)

                    # Copy the file
                    shutil.copy2(abs_file_path, dst_file_path)
                    copied_files.append(rel_file_path)

        # Update the Gradebook with the copied files
        gb.set_extra_files(copied_files)
        self.log.info(f"Copied the following files: {copied_files}")

    def set_permissions(self) -> None:
        self.log.info("Setting destination file permissions to %s", self.permissions)
        dest = os.path.normpath(self._output_directory)
        permissions = int(str(self.permissions), 8)
        for dirname, _, filenames in os.walk(dest):
            for filename in filenames:
                os.chmod(os.path.join(dirname, filename), permissions)

    def convert_single_notebook(self, notebook_filename: str) -> None:
        """
        Convert a single notebook.

        Performs the following steps:
            1. Initialize notebook resources
            2. Export the notebook to a particular format
            3. Write the exported notebook to file
        """
        self.log.info("Converting notebook %s", notebook_filename)
        resources = self.init_single_notebook_resources(notebook_filename)
        output, resources = self.exporter.from_filename(notebook_filename, resources=resources)
        self.write_single_notebook(output, resources)

    def convert_notebooks(self) -> None:
        errors = []

        def _handle_failure(exception) -> None:
            # dest = os.path.normpath(self._output_directory)
            # rmtree(dest)
            pass

        # initialize the list of notebooks and the exporter
        self.notebooks = sorted(self.notebooks)

        try:
            # determine whether we actually even want to process the notebooks
            should_process = self.init_destination()
            if not should_process:
                return

            self.run_pre_convert_hook()

            # convert all the notebooks
            for notebook_filename in self.notebooks:
                self.convert_single_notebook(notebook_filename)

            # set assignment permissions
            self.set_permissions()
            self.run_post_convert_hook()

            json_path = os.path.join(self._output_directory, "gradebook.json")
            with Gradebook(json_path) as gb:
                self.copy_unmatched_files(gb)

        except UnresponsiveKernelError as e:
            self.log.error(
                "While processing files %s, the kernel became "
                "unresponsive and we could not interrupt it. This probably "
                "means that the students' code has an infinite loop that "
                "consumes a lot of memory or something similar. nbgrader "
                "doesn't know how to deal with this problem, so you will "
                "have to manually edit the students' code (for example, to "
                "just throw an error rather than enter an infinite loop). ",
                self._format_source(),
            )
            errors.append(e)
            _handle_failure(e)

        except SchemaTooOldError as e:
            _handle_failure(e)
            msg = (
                "One or more notebooks in the assignment use an old version \n"
                "of the nbgrader metadata format. Please **back up your class files \n"
                "directory** and then update the metadata using:\n\nnbgrader update .\n"
            )
            self.log.error(msg)
            raise GraderConvertException(msg)

        except SchemaTooNewError as e:
            _handle_failure(e)
            msg = (
                "One or more notebooks in the assignment use an newer version \n"
                "of the nbgrader metadata format. Please update your version of \n"
                "nbgrader to the latest version to be able to use this notebook.\n"
            )
            self.log.error(msg)
            raise GraderConvertException(msg)

        except KeyboardInterrupt as e:
            _handle_failure(e)
            self.log.error("Canceled")
            raise

        except ValidationError as e:
            _handle_failure(e)
            self.log.error(e.message)
            raise GraderConvertException(e.message)

        except Exception as e:
            self.log.error("There was an error processing files: %s", self._format_source())
            self.log.error(traceback.format_exc())
            errors.append(e)
            _handle_failure(e)

        if errors:
            if self.logfile:
                msg = (
                    f"Please see the error log ({self.logfile}) for details on the specific "
                    "errors on the above failures."
                )
            else:
                msg = errors[0]

            self.log.error(msg)
            raise GraderConvertException(msg)

    def run_pre_convert_hook(self):
        if self.pre_convert_hook:
            self.log.info("Running pre-convert hook")
            try:
                self.pre_convert_hook(
                    notebooks=self.notebooks,
                    input_dir=self._input_directory,
                    output_dir=self._output_directory,
                )
            except Exception:
                self.log.error("Pre-convert hook failed", exc_info=True)

    def run_post_convert_hook(self):
        if self.post_convert_hook:
            self.log.info("Running post-convert hook")
            try:
                self.post_convert_hook(
                    notebooks=self.notebooks,
                    input_dir=self._input_directory,
                    output_dir=self._output_directory,
                )
            except Exception:
                self.log.error("Post-convert hook failed", exc_info=True)
