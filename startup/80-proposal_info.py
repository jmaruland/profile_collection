#set_project_name("ocko")
#set_project_name("dutta")

def set_project_name(project_name, folder_num=1):
    RE.md['project_name'] = project_name
    current_dir = proposal_path() + f"projects/{project_name}/"
    print(f'currently working at {current_dir}')
    ## add md below to keep consistent with previous data collection routine.
    RE.md['proposal_number'] = RE.md['proposal']['proposal_id']
    if folder_num == 1:
        RE.md['main_proposer'] = RE.md['proposal']['pi_name'].split(' ')[-1]
    else:
        RE.md['main_proposer'] = f"{RE.md['proposal']['pi_name'].split(' ')[-1]}{folder_num}"

# project_name is used by prefect to create the paths inside the porposal directory.
# The repository that creates the project directories is handled by this repository: https://github.com/NSLS2/opls-workflows
# Prefect run the workflows from https://app.prefect.cloud
