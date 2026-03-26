from roboflow import Roboflow


def download_data(api_key, workspace, project, version, format):
    rf = Roboflow(api_key=api_key)
    proj = rf.workspace(workspace).project(project)
    dataset = proj.version(version).download(format)
    return dataset.location
