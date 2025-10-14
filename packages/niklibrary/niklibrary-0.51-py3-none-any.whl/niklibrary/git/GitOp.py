import json
from .Git import Git
from .GitStatics import GitStatics
from ..helper.F import F
from ..helper.Statics import Statics


class GitOp:

    @staticmethod
    def setup_tracker_repo(fresh_clone=True):
        return GitOp.setup_repo(GitStatics.tracker_repo_dir, GitStatics.tracker_repo_url, "main", fresh_clone)

    @staticmethod
    def setup_repo(repo_dir, repo_url, branch="main", fresh_clone=True, commit_depth=50):
        print()
        print("Repo Dir: " + repo_dir)
        repo = Git(repo_dir)
        result = repo.clone_repo(repo_url, branch=branch, fresh_clone=fresh_clone, commit_depth=commit_depth)
        return repo if result else None

    @staticmethod
    def clone_overlay_repo(android_version, fresh_clone=False, branch="main", source=False, enable_push=False):
        if float(android_version) > 12:
            overlay_source_dir = (Statics.pwd + Statics.dir_sep + f"overlays_{android_version}"
                                  + ("_source" if source else ""))
            overlay_source_repo = (("git@gitlab.com:nikgapps/" if enable_push else "https://gitlab.com/nikgapps/")
                                   + f"overlays_{android_version}"
                                   + ("_source" if source else "") + ".git")
            return GitOp.setup_repo(overlay_source_dir, overlay_source_repo, branch, fresh_clone)
        else:
            print(f"Cloning Overlay repo not needed for android {android_version}")
            return None

    @staticmethod
    def clone_apk_repo(android_version, arch="arm64", fresh_clone=False, branch="main",
                       cached=False, use_ssh_clone=False):
        arch = "" if arch == "arm64" else "_" + arch
        cache = "_cached" if cached else ""
        apk_source_directory = Statics.pwd + Statics.dir_sep + str(android_version) + arch + cache
        apk_source_repo = (GitStatics.apk_source_repo_ssh if use_ssh_clone else GitStatics.apk_source_repo) + str(
            android_version) + arch + cache + ".git"
        return GitOp.setup_repo(apk_source_directory, apk_source_repo, branch, fresh_clone, commit_depth=1)

    # Following method is new method of cloning the apk source from Gitlab - based on release type
    @staticmethod
    def clone_apk_source(android_version, arch="arm64", release_type="stable", fresh_clone=False, cached=False,
                         use_ssh_clone=False):
        url = f"{android_version}{('_' + arch if arch != 'arm64' else '')}_{release_type}"
        url = url + ("_cached" if cached else "")
        return GitOp.clone_apk_url(url, fresh_clone, use_ssh_clone)

    @staticmethod
    def clone_apk_url(url, fresh_clone=False, use_ssh_clone=False):
        apk_source_directory = Statics.pwd + Statics.dir_sep + url
        apk_source_repo = ((GitStatics.apk_source_repo_ssh if use_ssh_clone else GitStatics.apk_source_repo) + url
                           + ".git")
        return GitOp.setup_repo(apk_source_directory, apk_source_repo, branch="main", fresh_clone=fresh_clone,
                                        commit_depth=1)

    @staticmethod
    def get_last_commit_date(branch, repo_dir=Statics.cwd, repo_url=None, android_version=None, use_ssh_clone=False):
        last_commit_datetime = None
        if android_version is not None:
            repository = GitOp.clone_apk_repo(android_version, branch=branch, use_ssh_clone=use_ssh_clone)
        else:
            repository = Git(repo_dir)
            if repo_url is not None:
                repository.clone_repo(repo_url=repo_url, fresh_clone=False, branch=branch)
        if repository is not None:
            last_commit_datetime = repository.get_latest_commit_date(branch=branch)
        return last_commit_datetime

    @staticmethod
    def get_release_repo(release_type):
        release_repo = Git(GitStatics.release_history_dir)
        if not F.dir_exists(GitStatics.release_history_dir):
            if release_type == "canary":
                GitStatics.release_repo_url = "git@github.com:nikgapps/canary-release.git"
            release_repo.clone_repo(GitStatics.release_repo_url, branch="master", commit_depth=50)
            if not F.dir_exists(GitStatics.release_history_dir):
                print(GitStatics.release_history_dir + " doesn't exist!")
        return release_repo

    @staticmethod
    def get_website_repo_for_changelog(repo_dir=GitStatics.website_repo_dir, repo_url=GitStatics.website_repo_url,
                                       branch="main"):
        repo = Git(repo_dir)
        if repo_url is not None:
            repo.clone_repo(repo_url=repo_url, fresh_clone=False, branch=branch)
        if not F.dir_exists(GitStatics.website_repo_dir):
            print(f"Repo {repo_dir} doesn't exist!")
        return repo

    @staticmethod
    def mark_a_release(android_version, release_type):
        tracker_repo = GitOp.setup_tracker_repo(False)
        if tracker_repo is not None:
            release_tracker = tracker_repo.working_tree_dir + Statics.dir_sep + "release_tracker.json"
            decoded_hand = {}
            if F.file_exists(release_tracker):
                with open(release_tracker, "r") as file:
                    decoded_hand = json.load(file)
                if release_type not in decoded_hand:
                    decoded_hand[release_type] = {}
                decoded_hand[release_type][android_version] = Statics.time
            else:
                decoded_hand[release_type] = {}
                decoded_hand[release_type][android_version] = Statics.time
            print(f"Marking a release with {decoded_hand}")
            with open(release_tracker, "w") as file:
                json_str = json.dumps(decoded_hand, indent=2, sort_keys=True)
                file.write(json_str)
            if tracker_repo.due_changes():
                tracker_repo.git_push(
                    f"Updated release_tracker.json with latest {release_type} release date: " + Statics.time,
                    pull_first=True)
            else:
                print("No changes to commit!")
