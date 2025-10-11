import re
import sys
import urllib.parse
from urllib.error import HTTPError

import osc.commandline
import osc.commandline_git


class ForkCommand(osc.commandline.OscCommand):
    """
    Fork a project or a package with sources managed in Gitea
    """

    name = "fork"

    # inject some git-obs methods to avoid duplicating code
    add_argument_new_repo_name = osc.commandline_git.GitObsCommand.add_argument_new_repo_name
    post_parse_args = osc.commandline_git.GitObsMainCommand.post_parse_args
    print_gitea_settings = osc.commandline_git.GitObsCommand.print_gitea_settings

    def quiet(self):
        if self.main_command.args.quiet:
            return True
        if self.gitea_login and self.gitea_login.quiet:
            return True
        return False

    def init_arguments(self):
        # inherit global options from the main git-obs command
        osc.commandline_git.GitObsMainCommand.init_arguments(self)

        self.add_argument(
            "project",
            help="Name of the project",
        )

        self.add_argument(
            "package",
            nargs="?",
            help="Name of the package",
        )

        self.add_argument(
            "--target-project",
            help="Name of the target project (defaults to home:$user:branches)",
        )

        self.add_argument(
            "--target-package",
            help="Name of the package (defaults to $package)",
        )

        self.add_argument_new_repo_name()

        self.add_argument(
            "--no-devel-project",
            action="store_true",
            help="Fork the specified package instead the package from the devel project (which is the place where the package is developed)",
        )

    def run(self, args):
        from osc import conf as osc_conf
        from osc import core as osc_core
        from osc import gitea_api
        from osc import obs_api
        from osc.git_scm import GitStore
        from osc.output import tty

        # make a copy of project, package; if we change them, the original values remain in args
        project = args.project
        package = args.package

        if project and "/" in project:
            self.parser.error(f"Invalid project: {project}")

        if package and "/" in package:
            self.parser.error(f"Invalid package: {package}")

        is_package = package is not None
        use_devel_project = False

        if not is_package and args.target_package:
            self.parser.error("The '--target-package' option requires the 'package' argument to be set")

        if not is_package and args.no_devel_project:
            self.parser.error("The '--no-devel-project' option can be used only when forking a package")

        if is_package:
            # get the package meta from the OBS API first
            pkg = obs_api.Package.from_api(args.apiurl, project, package)

            if not args.no_devel_project:
                devel_project, devel_package = osc_core.show_devel_project(args.apiurl, project, package)
                if devel_project:
                    # override the package we're cloning with the one from the devel project
                    pkg = obs_api.Package.from_api(args.apiurl, devel_project, devel_package)
                    use_devel_project = True

            if not pkg.scmsync:
                print(f"{tty.colorize('ERROR', 'red,bold')}: Forking is possible only with packages managed in Git (the <scmsync> element must be set in the package meta)")
                sys.exit(1)

        else:
            # get the project meta from the OBS API first
            project = obs_api.Project.from_api(args.apiurl, project)
            if not project.scmsync:
                raise RuntimeError(
                    "Forking is possible only with projects managed in Git (the <scmsync> element must be set in the project meta)"
                )

        # parse gitea url, owner, repo and branch from the scmsync url
        if is_package:
            url_scmsync = pkg.scmsync
        else:
            url_scmsync = project.scmsync
        parsed_scmsync_url = urllib.parse.urlparse(url_scmsync, scheme="https")
        url = urllib.parse.urlunparse((parsed_scmsync_url.scheme, parsed_scmsync_url.netloc, "", "", "", ""))
        owner, repo = parsed_scmsync_url.path.strip("/").split("/")

        # remove trailing ".git" from repo
        if repo.endswith(".git"):
            repo = repo[:-4]

        # temporary hack to allow people using fork atm at all, when packages
        # are managed via git project.
        # fallback always to default branch for now, but we actually need to 
        # parse the right branch instead from .gitmodules
        #branch = parsed_scmsync_url.fragment or None
        branch = None
        parsed_scmsync_url_query = urllib.parse.parse_qs(parsed_scmsync_url.query)
        if "trackingbranch" in parsed_scmsync_url_query:
            branch = parsed_scmsync_url_query["trackingbranch"][0]

        # find a credentials entry for url and OBS user (there can be multiple users configured for a single URL in the config file)
        gitea_conf = gitea_api.Config(args.gitea_config)
        gitea_login = gitea_conf.get_login_by_url_user(url=url, user=osc_conf.get_apiurl_usr(args.apiurl))
        gitea_conn = gitea_api.Connection(gitea_login)

        # store the attributes for self.print_gitea_settings()
        self.gitea_conf = gitea_conf
        self.gitea_login = gitea_login
        self.gitea_conn = gitea_conn

        self.print_gitea_settings()
        print(f"Forking git repo {owner}/{repo} ...", file=sys.stderr)

        # the branch was not specified, fetch the default branch from the repo
        if not branch:
            repo_obj = gitea_api.Repo.get(gitea_conn, owner, repo)
            branch = repo_obj.default_branch
        fork_branch = branch

        # check if the scmsync branch exists in the source repo
        parent_branch_obj = gitea_api.Branch.get(gitea_conn, owner, repo, fork_branch)

        try:
            repo_obj = gitea_api.Fork.create(gitea_conn, owner, repo, new_repo_name=args.new_repo_name)
            fork_owner = repo_obj.owner
            fork_repo = repo_obj.repo
            print(f" * Fork created: {fork_owner}/{fork_repo}")
        except gitea_api.ForkExists as e:
            fork_owner = e.fork_owner
            fork_repo = e.fork_repo
            print(f" * Fork already exists: {fork_owner}/{fork_repo}")

        # XXX: implicit branch name should be forbidden; assumptions are bad
        fork_scmsync = urllib.parse.urlunparse(
            (parsed_scmsync_url.scheme, parsed_scmsync_url.netloc, f"{fork_owner}/{fork_repo}", "", parsed_scmsync_url.query, fork_branch)
        )

        print()
        if is_package:
            print(f"Forking OBS package {project}/{package} ...")
            if use_devel_project:
                print(f" * {tty.colorize('NOTE', 'bold')}: Forking from the devel project instead of the specified {args.project}/{args.package}")
        else:
            print(f"Forking OBS project {project} ...")
        print(f" * OBS apiurl: {args.apiurl}")
        # we use a single API endpoint for forking both projects and packages (project requires setting package to "_project")
        status = obs_api.Package.cmd_fork(
            args.apiurl,
            project,
            package if is_package else "_project",
            scmsync=fork_scmsync,
            target_project=args.target_project,
            target_package=args.target_package if is_package else None,
        )
        # XXX: the current OBS API is not ideal; we don't get any info whether the new package exists already; 404 would be probably nicer
        target_project = status.data["targetproject"]
        if is_package:
            target_package = status.data["targetpackage"]
            print(f" * Fork created: {target_project}/{target_package}")
        else:
            print(f" * Fork created: {target_project}")
        print(f" * scmsync URL: {fork_scmsync}")

        # check if the scmsync branch exists in the forked repo
        fork_branch_obj = gitea_api.Branch.get(gitea_conn, fork_owner, fork_repo, fork_branch)

        parent_commit = parent_branch_obj.commit
        fork_commit = fork_branch_obj.commit
        if parent_commit != fork_commit:
            print()
            print(f"{tty.colorize('ERROR', 'red,bold')}: The branch in the forked repo is out of sync with the parent")
            print(f" * Fork: {fork_owner}/{fork_repo}#{fork_branch}, commit: {fork_commit}")
            print(f" * Parent: {owner}/{repo}#{fork_branch}, commit: {parent_commit}")
            print(" * If this is not intentional, please clone the fork and fix the branch manually")
            sys.exit(1)
