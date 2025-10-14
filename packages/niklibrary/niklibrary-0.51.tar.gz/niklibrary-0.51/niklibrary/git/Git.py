import re

import git.exc
from git import Repo, Commit
import os
import time
import datetime
from datetime import datetime
import pytz
from ..helper.F import F
from ..helper.P import P
from ..helper.T import T


class Git:

    def __init__(self, working_tree_dir, enable_push=True):
        os.environ["GIT_CLONE_PROTECTION_ACTIVE"] = 'false'
        self.enable_push = enable_push
        self.working_tree_dir = working_tree_dir
        self.repo_name = None
        if F.dir_exists(self.working_tree_dir):
            self.repo = Repo(working_tree_dir)

    def clone_repo(self, repo_url, branch="main", fresh_clone=True, commit_depth=1):
        try:
            t = T()
            if fresh_clone:
                # for fresh clone, we must clean the directory and clone again
                if F.dir_exists(self.working_tree_dir):
                    print(f"{self.working_tree_dir} already exists, deleting for a fresh clone!")
                    F.remove_dir(self.working_tree_dir)
                if commit_depth == 0:
                    P.green(f"git clone -b {branch} {repo_url}")
                    self.repo = git.Repo.clone_from(repo_url, self.working_tree_dir, branch=branch)
                else:
                    P.green(f"git clone -b {branch} --depth={commit_depth} {repo_url}")
                    self.repo = git.Repo.clone_from(repo_url, self.working_tree_dir, branch=branch, depth=commit_depth)

            else:
                # if it is not a fresh clone, we only clone when directory doesn't exist
                if not F.dir_exists(self.working_tree_dir):
                    print(f"{self.working_tree_dir} doesn't exists, fresh clone is enforced!")
                    P.yellow(f"git clone -b {branch} --depth={commit_depth} {repo_url}")
                    self.repo = git.Repo.clone_from(repo_url, self.working_tree_dir, branch=branch, depth=commit_depth)
            t.taken(f"Time taken to clone -b {branch} {repo_url}")
            self.update_repo_name(repo_url)
            assert self.repo.__class__ is Repo  # clone an existing repository
            assert Repo.init(self.working_tree_dir).__class__ is Repo
            return True
        except Exception as e:
            print("Exception caught while cloning the repo: " + str(e))
        return False

    # this will return commits 21-30 from the commit list as traversed backwards master
    # ten_commits_past_twenty = list(repo.iter_commits('master', max_count=10, skip=20))
    # assert len(ten_commits_past_twenty) == 10
    # assert fifty_first_commits[20:30] == ten_commits_past_twenty
    # repo = git.Repo.clone_from(repo_url, working_tree_dir, branch='master')
    def get_latest_commit_date(self, branch=None, filter_key=None):
        tz_london = pytz.timezone('Europe/London')
        try:
            if branch is not None:
                commits = list(self.repo.iter_commits(branch, max_count=50))
            else:
                commits = list(self.repo.iter_commits('master', max_count=50))
        except git.exc.GitCommandError:
            if branch == "master":
                branch = "main"
            commits = list(self.repo.iter_commits(branch, max_count=50))

        for commit in commits:
            commit: Commit
            # if filter_key = 10, it will look for commits that starts with 10
            # failing will continue looking for latest available commit that starts with 10
            if filter_key is not None and not str(commit.message).startswith(filter_key + ":"):
                continue
            time_in_string = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(commit.committed_date)))
            time_in_object = datetime.strptime(time_in_string, '%Y-%m-%d %H:%M:%S')
            london_time_in_object = time_in_object.astimezone(tz_london)
            london_time_in_string = london_time_in_object.strftime('%Y-%m-%d %H:%M:%S')
            commit_datetime = datetime.strptime(london_time_in_string, '%Y-%m-%d %H:%M:%S')
            return commit_datetime
        return None

    def update_repo_name(self, git_url):
        git_pattern = re.compile(r'git@[^:]+:[^/]+/(.+)\.git')
        https_pattern = re.compile(r'https?://[^/]+/[^/]+/(.+)\.git')
        match = git_pattern.match(git_url) or https_pattern.match(git_url)
        if match:
            self.repo_name = match.group(1)
        else:
            raise ValueError("Invalid Git URL")

    def get_file_commit_date(self, file_path, str_format="%y%m%d%H%M", skip_containing=None):
        commits_touching_path = list(self.repo.iter_commits(paths=file_path))
        if commits_touching_path:
            for commit in commits_touching_path:
                if skip_containing is not None and str(skip_containing).lower() in commit.message.lower():
                    P.blue(f"Skipping commit ({commit.hexsha[:7]}): "
                           f"{commit.message} as it contains '{skip_containing}'")
                    continue
                P.green(f"Commit ({commit.hexsha[:7]}): {commit.message} found for {file_path}")
                return commit.committed_datetime.strftime(str_format)
        else:
            return None

    def get_changed_files(self):
        files_list = []
        files = self.repo.git.diff(None, name_only=True)
        if files != "":
            for f in files.split('\n'):
                files_list.append(f)
        if self.repo.untracked_files.__len__() > 0:
            for f in self.repo.untracked_files:
                files_list.append(f)
        return files_list

    def due_changes(self):
        files = self.repo.git.diff(None, name_only=True)
        if files != "":
            if files.split('\n').__len__() > 0:
                return True
        if self.repo.untracked_files.__len__() > 0:
            return True
        return False

    def git_push(self, commit_message, push_untracked_files=False, debug=False, rebase=False, pull_first=False,
                 post_buffer=None):
        if not self.enable_push:
            print("Git push is disabled, skipping push!")
            return False
        try:
            origin = self.repo.remote(name='origin')
            if post_buffer is not None:
                self.repo.git.config('http.postBuffer', post_buffer)
            if self.repo.is_dirty(untracked_files=True):
                self.repo.git.add(u=True)
                if push_untracked_files:
                    self.repo.git.add(A=True)
                if commit_message is None:
                    commit_message = "Auto Commit"
                self.repo.index.commit(commit_message)
            if pull_first:
                origin.fetch(self.repo.active_branch.name)
                origin.pull(self.repo.active_branch.name)
            if rebase:
                origin.fetch(self.repo.active_branch.name)
                try:
                    self.repo.git.pull('--rebase')
                except git.GitCommandError as e:
                    print(f"Error during rebase: {e}")
                    return False
            if debug:
                remotes = self.repo.remotes
                for remote in remotes:
                    print(f"Remote name: {remote.name}")
                    for url in remote.urls:
                        print(f"URL: {url}")
                P.blue(self.repo.git.status())
            push_info = origin.push(self.repo.active_branch.name)
            for info in push_info:
                if info.flags & (git.PushInfo.REMOTE_REJECTED | git.PushInfo.ERROR):
                    print(f"Push failed for ref {info.local_ref}: {info.summary}")
                    if info.summary.__contains__("remote rejected") and info.summary.__contains__(
                            "is at") and info.summary.__contains__("but expected"):
                        print("Remote rejected, trying to pull!")
                        origin.fetch(self.repo.active_branch.name)
                        origin.pull(self.repo.active_branch.name)
                        # rebase if this fails.
                        push_info = origin.push(self.repo.active_branch.name)
                        for nested_info in push_info:
                            if nested_info.flags & (git.PushInfo.REMOTE_REJECTED | git.PushInfo.ERROR):
                                print(f"Push failed for ref {nested_info.local_ref}: {nested_info.summary}")
                                return False
                    return False

            print("Pushed to origin:", commit_message)
            return True

        except git.exc.GitCommandError as e:
            if "failed to push some refs" in e.stderr:  # Check for the specific error
                self.repo.git.pull("origin", "main")  # Pull changes from remote
                self.repo.git.push()  # Retry the push
            else:
                print(f"Git error: {e}")
                raise e

        except Exception as e:
            print(f"Unexpected error: {e}")
        return False

    def update_config_changes(self, message):
        if self.due_changes():
            print(message)
            self.git_push(message, push_untracked_files=True)
        else:
            print("There is nothing to update!")

    def update_repo_changes(self, message):
        if self.due_changes():
            P.green(message)
            self.git_push(message, push_untracked_files=True)
        else:
            P.red("There is nothing to update!")

    def get_status(self, path):
        changed = [item.a_path for item in self.repo.index.diff(None)]
        if path in self.repo.untracked_files:
            return 'untracked'
        elif path in changed:
            return 'modified'
        else:
            return 'don''t care'
