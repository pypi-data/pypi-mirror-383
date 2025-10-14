# Copyright (c) 2022, TU Wien
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

import io
import logging
import os
from subprocess import CalledProcessError

from traitlets import Unicode

from grader_service.autograding.local_grader import LocalAutogradeExecutor
from grader_service.autograding.utils import rmtree
from grader_service.convert.converters.generate_feedback import GenerateFeedback
from grader_service.handlers.handler_utils import GitRepoType
from grader_service.orm.assignment import Assignment
from grader_service.orm.lecture import Lecture
from grader_service.orm.submission import FeedbackStatus, Submission


class GenerateFeedbackExecutor(LocalAutogradeExecutor):
    def __init__(self, grader_service_dir: str, submission: Submission, **kwargs):
        super().__init__(grader_service_dir, submission, **kwargs)

    @property
    def input_path(self):
        return os.path.join(
            self.grader_service_dir, self.relative_input_path, f"feedback_{self.submission.id}"
        )

    @property
    def output_path(self):
        return os.path.join(
            self.grader_service_dir, self.relative_output_path, f"feedback_{self.submission.id}"
        )

    def _get_git_repo_path(self, repo_type: GitRepoType) -> str:
        assignment: Assignment = self.submission.assignment
        lecture: Lecture = assignment.lecture
        repo_name = self.submission.user.name

        return os.path.join(
            self.grader_service_dir,
            "git",
            lecture.code,
            str(assignment.id),
            repo_type,
            "user",
            repo_name,
        )

    def _pull_submission(self):
        if not os.path.exists(self.input_path):
            os.mkdir(self.input_path)

        git_repo_path = self._get_git_repo_path(repo_type=GitRepoType.AUTOGRADE)

        if os.path.exists(self.input_path):
            rmtree(self.input_path)
        os.mkdir(self.input_path)

        self.log.info(f"Pulling repo {git_repo_path} into input directory")

        command = f"{self.git_executable} init"
        self.log.info(f"Running {command}")
        try:
            self._run_subprocess(command, self.input_path)
        except CalledProcessError:
            pass

        command = (
            f'{self.git_executable} pull "{git_repo_path}" submission_{self.submission.commit_hash}'
        )
        self.log.info(f"Running {command}")
        try:
            self._run_subprocess(command, self.input_path)
        except CalledProcessError:
            pass
        self.log.info("Successfully cloned repo")

    def _run(self):
        if os.path.exists(self.output_path):
            rmtree(self.output_path)

        os.makedirs(self.output_path)
        self._write_gradebook(self.submission.properties.properties)

        feedback_generator = GenerateFeedback(
            self.input_path,
            self.output_path,
            "*.ipynb",
            assignment_settings=self.assignment.settings,
        )
        feedback_generator.force = True

        log_stream = io.StringIO()
        log_handler = logging.StreamHandler(log_stream)
        feedback_generator.log.addHandler(log_handler)

        feedback_generator.start()

        self.grading_logs = log_stream.getvalue()
        feedback_generator.log.removeHandler(log_handler)

    def _push_results(self):
        os.unlink(os.path.join(self.output_path, "gradebook.json"))

        git_repo_path = self._get_git_repo_path(repo_type=GitRepoType.FEEDBACK)

        if not os.path.exists(git_repo_path):
            os.makedirs(git_repo_path, exist_ok=True)
            try:
                self._run_subprocess(f'git init --bare "{git_repo_path}"', self.output_path)
            except CalledProcessError:
                raise

        command = f"{self.git_executable} init"
        self.log.info(f"Running {command} at {self.output_path}")
        try:
            self._run_subprocess(command, self.output_path)
        except CalledProcessError:
            pass

        self.log.info(f"Creating new branch feedback_{self.submission.commit_hash}")
        command = f"{self.git_executable} switch -c feedback_{self.submission.commit_hash}"
        try:
            self._run_subprocess(command, self.output_path)
        except CalledProcessError:
            pass
        self.log.info(f"Now at branch feedback_{self.submission.commit_hash}")

        self.log.info(f"Commiting all files in {self.output_path}")
        self._run_subprocess(f"{self.git_executable} add -A", self.output_path)
        self._run_subprocess(
            f'{self.git_executable} commit -m "{self.submission.commit_hash}"', self.output_path
        )
        self.log.info(
            f"Pushing to {git_repo_path} at branch feedback_{self.submission.commit_hash}"
        )
        command = (
            f'{self.git_executable} push -uf "{git_repo_path}" '
            f"feedback_{self.submission.commit_hash}"
        )
        self._run_subprocess(command, self.output_path)
        self.log.info("Pushing complete")

    def _set_properties(self):
        # No need to set properties
        pass

    def _set_db_state(self, success=True):
        """
        Sets the submission feedback status based on the success of the generation.
        :param success: Whether feedback generation was succesfull or not.
        :return: None
        """
        if success:
            self.submission.feedback_status = FeedbackStatus.GENERATED
        else:
            self.submission.feedback_status = FeedbackStatus.GENERATION_FAILED
        self.session.commit()


class GenerateFeedbackProcessExecutor(GenerateFeedbackExecutor):
    convert_executable = Unicode("grader-convert", allow_none=False).tag(config=True)

    def _run(self):
        if os.path.exists(self.output_path):
            rmtree(self.output_path)

        os.mkdir(self.output_path)
        self._write_gradebook(self.submission.properties)

        command = (
            f"{self.convert_executable} generate_feedback -i "
            f'"{self.input_path}" -o "{self.output_path}" -p "*.ipynb"'
        )
        self.log.info(f"Running {command}")
        process = self._run_subprocess(command, None)
        self.grading_logs = process.stderr.read().decode("utf-8")
        self.log.info(self.grading_logs)
        if process.returncode == 0:
            self.log.info("Process has successfully completed execution!")
        else:
            raise RuntimeError("Process has failed execution!")
