import os


def resolve_workspace_dir(workspace_dir=None):
    if workspace_dir:
        return os.path.abspath(os.path.expanduser(workspace_dir))

    env_workspace = os.environ.get("TICC_WORKSPACE_DIR") or os.environ.get("OPENCLAW_WORKSPACE")
    if env_workspace:
        return os.path.abspath(os.path.expanduser(env_workspace))

    return os.getcwd()


def resolve_in_workspace(path_value, workspace_dir):
    expanded = os.path.expanduser(path_value)
    if os.path.isabs(expanded):
        return os.path.normpath(expanded)
    return os.path.normpath(os.path.join(workspace_dir, expanded))