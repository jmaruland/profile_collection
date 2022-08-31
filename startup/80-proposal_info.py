#proposal_id("2021_3","307695_ocko")
#proposal_id("2022_1","308307_dutta")
#proposal_id("2022_1","309161_zhang")
#proposal_id("2022_1","309891_tu")
#proposal_id("2022_1","309773_ocko")
#proposal_id("2022_2","310472_zhang")
#proposal_id("2022_2","310190_arjunkrishna")
#proposal_id("2022_2","309891_tu")
#proposal_id("2022_2","309773_ocko")




def proposal_id(cycle_id, proposal_id):
    RE.md['cycle'] = cycle_id
    RE.md['proposal_number'] = proposal_id.split('_')[0]
    RE.md['main_proposer'] = proposal_id.split('_')[1]

    # 2018-04-10: Maksim asked Tom about why this 'put' does not create the folder,
    # Tom suggested to ask PoC to update AD installation.
    import stat
    newDir = "/nsls2/xf12id1/users/" + str(cycle_id) + "/" + str(proposal_id) + "/scan_plots"
    try:
        os.stat(newDir)
    except FileNotFoundError:
        os.makedirs(newDir)
        os.chmod(newDir, stat.S_IRWXU + stat.S_IRWXG + stat.S_IRWXO)
    
    newDir = "/nsls2/xf12id1/users/" + str(cycle_id) + "/" + str(proposal_id) + "/GID_data"
    try:
        os.stat(newDir)
    except FileNotFoundError:
        os.makedirs(newDir)
        os.chmod(newDir, stat.S_IRWXU + stat.S_IRWXG + stat.S_IRWXO)
    
    newDir = "/nsls2/xf12id1/users/" + str(cycle_id) + "/" + str(proposal_id) + "/GID_analysis"
    try:
        os.stat(newDir)
    except FileNotFoundError:
        os.makedirs(newDir)
        os.chmod(newDir, stat.S_IRWXU + stat.S_IRWXG + stat.S_IRWXO)

    newDir = "/nsls2/xf12id1/users/" + str(cycle_id) + "/" + str(proposal_id) + "/XRR_analysis"
    try:
        os.stat(newDir)
    except FileNotFoundError:
        os.makedirs(newDir)
        os.chmod(newDir, stat.S_IRWXU + stat.S_IRWXG + stat.S_IRWXO)
        
    newDir = "/nsls2/xf12id1/users/" + str(cycle_id) + "/" + str(proposal_id) + "/XRR_data"
    try:
        os.stat(newDir)
    except FileNotFoundError:
        os.makedirs(newDir)
        os.chmod(newDir, stat.S_IRWXU + stat.S_IRWXG + stat.S_IRWXO)

    newDir = "/nsls2/xf12id1/users/" + str(cycle_id) + "/" + str(proposal_id) + "/XRF_analysis"
    try:
        os.stat(newDir)
    except FileNotFoundError:
        os.makedirs(newDir)
        os.chmod(newDir, stat.S_IRWXU + stat.S_IRWXG + stat.S_IRWXO)
        
    newDir = "/nsls2/xf12id1/users/" + str(cycle_id) + "/" + str(proposal_id) + "/XRF_data"
    try:
        os.stat(newDir)
    except FileNotFoundError:
        os.makedirs(newDir)
        os.chmod(newDir, stat.S_IRWXU + stat.S_IRWXG + stat.S_IRWXO)

    newDir = "/nsls2/xf12id1/users/" + str(cycle_id) + "/" + str(proposal_id) + "/XRR_analysis/data"
    try:
        os.stat(newDir)
    except FileNotFoundError:
        os.makedirs(newDir)
        os.chmod(newDir, stat.S_IRWXU + stat.S_IRWXG + stat.S_IRWXO)

    newDir = "/nsls2/xf12id1/users/" + str(cycle_id) + "/" + str(proposal_id) + "/XRR_analysis/data2"
    try:
        os.stat(newDir)
    except FileNotFoundError:
        os.makedirs(newDir)
        os.chmod(newDir, stat.S_IRWXU + stat.S_IRWXG + stat.S_IRWXO)

\
    newDir = "/nsls2/xf12id1/users/" + str(cycle_id) + "/" + str(proposal_id) + "/XRR_analysis/q_plots"
    try:
        os.stat(newDir)
    except FileNotFoundError:
        os.makedirs(newDir)
        os.chmod(newDir, stat.S_IRWXU + stat.S_IRWXG + stat.S_IRWXO)

    newDir = "/nsls2/xf12id1/users/" + str(cycle_id) + "/" + str(proposal_id) + "/XRR_analysis/checks_plots"
    try:
        os.stat(newDir)
    except FileNotFoundError:
        os.makedirs(newDir)
        os.chmod(newDir, stat.S_IRWXU + stat.S_IRWXG + stat.S_IRWXO)


    newDir = "/nsls2/xf12id1/users/" + str(cycle_id) + "/" + str(proposal_id) + "/XRR_analysis/summaries"
    try:
        os.stat(newDir)
    except FileNotFoundError:
        os.makedirs(newDir)
        os.chmod(newDir, stat.S_IRWXU + stat.S_IRWXG + stat.S_IRWXO)