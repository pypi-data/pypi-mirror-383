# Copyright (c) 2022, TU Wien
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
import os
import shlex
import subprocess
from pathlib import Path
from string import Template
from typing import List, Optional

from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from tornado.ioloop import IOLoop
from tornado.iostream import StreamClosedError
from tornado.process import Subprocess
from tornado.web import HTTPError, stream_request_body

from grader_service.handlers.base_handler import GraderBaseHandler, RequestHandlerConfig
from grader_service.handlers.handler_utils import GitRepoType
from grader_service.orm.lecture import Lecture
from grader_service.orm.submission import Submission
from grader_service.orm.takepart import Role, Scope
from grader_service.registry import VersionSpecifier, register_handler


class GitBaseHandler(GraderBaseHandler):
    async def data_received(self, chunk: bytes):
        return self.process.stdin.write(chunk)

    def write_error(self, status_code: int, **kwargs) -> None:
        self.clear()
        if status_code == 401:
            self.set_header("WWW-Authenticate", 'Basic realm="User Visible Realm"')
        self.set_status(status_code)

    def on_finish(self):
        if hasattr(
            self, "process"
        ):  # if we exit super prepare (authentication) process is not created
            if self.process.stdin is not None:
                self.process.stdin.close()
            if self.process.stdout is not None:
                self.process.stdout.close()
            if self.process.stderr is not None:
                self.process.stderr.close()
            IOLoop.current().spawn_callback(self.process.wait_for_exit)

    async def git_response(self):
        try:
            while data := await self.process.stdout.read_bytes(8192, partial=True):
                self.write(data)
                await self.flush()
        except StreamClosedError:
            pass
        except Exception as e:
            self.log.error(f"Error from git response {e}")
            raise HTTPError(500, str(e))

    def _check_git_repo_permissions(self, rpc: str, role: Role, pathlets: List[str]):
        repo_type: str = pathlets[2]

        if role.role == Scope.student:
            # 1. no source or release interaction with source repo for students
            # 2. no pull allowed for autograde for students
            if (repo_type in {GitRepoType.SOURCE, GitRepoType.RELEASE, GitRepoType.EDIT}) or (
                repo_type == GitRepoType.AUTOGRADE and rpc == "upload-pack"
            ):
                raise HTTPError(403)

            # 3. students should not be able to pull other submissions
            #    -> add query param for sub_id
            if (repo_type == GitRepoType.FEEDBACK) and (rpc == "upload-pack"):
                try:
                    sub_id = int(pathlets[3])
                except (ValueError, IndexError):
                    raise HTTPError(403)
                submission = self.session.query(Submission).get(sub_id)
                if submission is None or submission.user_id != self.user.id:
                    raise HTTPError(403)

        # 4. no push allowed for autograde and feedback
        #    -> the autograder executor can push locally (will bypass this)
        if (repo_type in {GitRepoType.AUTOGRADE, GitRepoType.FEEDBACK}) and (
            rpc in ["send-pack", "receive-pack"]
        ):
            raise HTTPError(403)

    def gitlookup(self, rpc: str) -> Optional[str]:
        pathlets = self.request.path.strip("/").split("/")
        # check if request is sent using jupyterhub as a proxy
        # if yes, remove services/grader path prefix
        assert len(pathlets) > 0
        if pathlets[0] == "services":
            pathlets = pathlets[2:]

        # pathlets should look like this
        # pathlets = ['git',
        #             'lecture_code', 'assignment_id', 'repo_type', ...]
        if len(pathlets) < 4:
            return None

        # cut git prefix
        pathlets = pathlets[1:]
        lect_code, assign_id, repo_type, *pathlets_tail = pathlets

        # Repo type "assignment" has been replaced by "user", so this should not happen,
        # but we are leaving this check for the time being, just to be on the safe side:
        if repo_type == "assignment":
            self.log.warning("Deprecated repo_type: 'assignment'! Setting it to 'user'")
            repo_type = GitRepoType.USER

        try:
            repo_type = GitRepoType(repo_type)
        except ValueError:
            return None

        # get lecture and assignment if they exist
        try:
            lecture = self.session.query(Lecture).filter(Lecture.code == lect_code).one()
        except NoResultFound:
            raise HTTPError(404, reason="Lecture was not found")
        except MultipleResultsFound:
            raise HTTPError(500, reason="Found more than one lecture")

        role = self.session.get(Role, (self.user.id, lecture.id))
        self._check_git_repo_permissions(rpc, role, pathlets)

        try:
            assignment = self.get_assignment(lecture.id, int(assign_id))
        except ValueError:
            raise HTTPError(404, reason="Assignment not found")

        # create directories once we know they exist in the database
        lecture_path = os.path.abspath(os.path.join(self.gitbase, lect_code))
        assignment_path = os.path.abspath(os.path.join(lecture_path, assign_id))
        if not os.path.exists(lecture_path):
            os.mkdir(lecture_path)
        if not os.path.exists(assignment_path):
            os.mkdir(assignment_path)

        submission = None
        if repo_type in {GitRepoType.AUTOGRADE, GitRepoType.FEEDBACK, GitRepoType.EDIT}:
            try:
                sub_id = int(pathlets_tail[0])
            except (ValueError, IndexError):
                raise HTTPError(403, "Invalid or missing submission id")
            submission = self.get_submission(lecture.id, assignment.id, sub_id)

        path = self.construct_git_dir(repo_type, lecture, assignment, submission=submission)
        if path is None:
            return None

        os.makedirs(os.path.dirname(path), exist_ok=True)
        is_git = self.is_base_git_dir(path)
        # return git repo
        if os.path.exists(path) and is_git:
            self.write_pre_receive_hook(path)
            return path
        else:
            os.mkdir(path)
            # this path has to be a git dir -> call git init
            try:
                self.log.info("Running: git init --bare")
                subprocess.run(["git", "init", "--bare", path], check=True)
            except subprocess.CalledProcessError:
                return None

            if repo_type == GitRepoType.USER:
                repo_path_release = self.construct_git_dir(
                    GitRepoType.RELEASE, assignment.lecture, assignment
                )
                if not os.path.exists(repo_path_release):
                    return None
                self.duplicate_release_repo(
                    repo_path_release=repo_path_release,
                    repo_path_user=path,
                    assignment=assignment,
                    message="Initialize with Release",
                    checkout_main=True,
                )

            self.write_pre_receive_hook(path)
            return path

    def write_pre_receive_hook(self, path: str):
        hook_dir = os.path.join(path, "hooks")
        if not os.path.exists(hook_dir):
            os.mkdir(hook_dir)

        hook_file = os.path.join(hook_dir, "pre-receive")
        if not os.path.exists(hook_file):
            tpl = Template(self._read_hook_template())
            hook = tpl.safe_substitute(
                {
                    "tpl_max_file_size": self._get_hook_max_file_size(),
                    "tpl_file_extensions": self._get_hook_file_allow_pattern(),
                    "tpl_max_file_count": self._get_hook_max_file_count(),
                }
            )
            with open(hook_file, "wt") as f:
                os.chmod(hook_file, 0o755)
                f.write(hook)

    @staticmethod
    def _get_hook_file_allow_pattern(extensions: Optional[List[str]] = None) -> str:
        pattern = ""
        if extensions is None:
            req_handler_conf = RequestHandlerConfig.instance()
            extensions = req_handler_conf.git_allowed_file_extensions
        if len(extensions) > 0:
            allow_patterns = ["\\." + s.strip(".").replace(".", "\\.") for s in extensions]
            pattern = "|".join(allow_patterns)
        return pattern

    @staticmethod
    def _get_hook_max_file_size():
        return RequestHandlerConfig.instance().git_max_file_size_mb

    @staticmethod
    def _get_hook_max_file_count():
        return RequestHandlerConfig.instance().git_max_file_count

    @staticmethod
    def _read_hook_template() -> str:
        file_path = Path(__file__).parent / "hook_templates" / "pre-receive"
        with open(file_path, mode="rt") as f:
            return f.read()

    @staticmethod
    def _create_path(path):
        if not os.path.exists(path):
            os.mkdir(path)

    def get_gitdir(self, rpc: str):
        """Determine the git repository for this request"""
        gitdir = self.gitlookup(rpc)
        if gitdir is None:
            raise HTTPError(404, reason="unable to find repository")
        self.log.info("Accessing git at: %s", gitdir)

        return gitdir


@register_handler(path="/.*/git-(.*)", version_specifier=VersionSpecifier.NONE)
@stream_request_body
class RPCHandler(GitBaseHandler):
    """Request handler for RPC calls

    Use this handler to handle example.git/git-upload-pack
    and example.git/git-receive-pack URLs"""

    async def prepare(self):
        await super().prepare()
        self.rpc = self.path_args[0]
        self.gitdir = self.get_gitdir(rpc=self.rpc)
        self.cmd = f'git {self.rpc} --stateless-rpc "{self.gitdir}"'
        self.log.info(f"Running command: {self.cmd}")
        self.process = Subprocess(
            shlex.split(self.cmd),
            stdin=Subprocess.STREAM,
            stderr=Subprocess.STREAM,
            stdout=Subprocess.STREAM,
        )

    async def post(self, rpc):
        self.set_header("Content-Type", "application/x-git-%s-result" % rpc)
        self.set_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        await self.git_response()
        await self.finish()


@register_handler(path="/.*/info/refs", version_specifier=VersionSpecifier.NONE)
class InfoRefsHandler(GitBaseHandler):
    """Request handler for info/refs

    Use this handler to handle example.git/info/refs?service= URLs"""

    async def prepare(self):
        await super().prepare()
        if self.get_status() != 200:
            return
        self.rpc = self.get_argument("service")[4:]
        self.cmd = f'git {self.rpc} --stateless-rpc --advertise-refs "{self.get_gitdir(self.rpc)}"'
        self.log.info(f"Running command: {self.cmd}")
        self.process = Subprocess(
            shlex.split(self.cmd),
            stdin=Subprocess.STREAM,
            stderr=Subprocess.STREAM,
            stdout=Subprocess.STREAM,
        )

    async def get(self):
        self.set_header("Content-Type", "application/x-git-%s-advertisement" % self.rpc)
        self.set_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")

        prelude = f"# service=git-{self.rpc}\n0000"
        size = str(hex(len(prelude))[2:].rjust(4, "0"))
        self.write(size)
        self.write(prelude)
        await self.flush()

        await self.git_response()
        await self.finish()
