#set_project_name("ocko")
#set_project_name("dutta")

def set_project_name(project_name):
    RE.md['project_name'] = project_name
    current_dir = proposal_path() + f"projects/{project_name}/"
    print(f'currently working at {current_dir}')

# project_name is used by prefect to create the paths inside the porposal directory.
# The repository that creates the project directories is handled by this repository: https://github.com/NSLS2/opls-workflows
# Prefect run the workflows from https://app.prefect.cloud
