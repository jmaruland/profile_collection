#proposal_id("2021_3","307695_ocko")
#proposal_id("2022_1","308307_dutta")
#proposal_id("2022_1","309161_zhang")
#proposal_id("2022_1","309891_tu")
#proposal_id("2022_1","309773_ocko")
#proposal_id("2022_2","310472_zhang")
#proposal_id("2022_2","310190_arjunkrishna")
#proposal_id("2022_2","309891_tu")
#proposal_id("2022_2","309773_ocko")

#proposal_id("2022_3","311547_ocko")
#proposal_id("2022_3","309891_tu")
#proposal_id("2022_3","308307_dutta")
#proposal_id("2022_3","310472_zhang")
#proposal_id("2022_3","311090_arjunkrishna")
#proposal_id("2022_3","309773_ocko")
#proposal_id("2022_3","310438_satija")

# proposal_id("2023_2","311915_opls")
# proposal_id("2023_2","311053_dutta")

# proposal_id("2023_3","312622_satija")

# proposal_id("2024_1","312622_satija")

# proposal_id("2024_1","314053_venkatesan")

#proposal_id("2024_1","313704_tu")





def proposal_id(cycle_id, proposal_id):
    RE.md['cycle'] = cycle_id
    RE.md['proposal_number'] = proposal_id.split('_')[0]
    RE.md['main_proposer'] = proposal_id.split('_')[1]
    print(f'Currently working in the cycle of {cycle_id} and the proposal of {proposal_id}')

    # 2018-04-10: Maksim asked Tom about why this 'put' does not create the folder,
    # Tom suggested to ask PoC to update AD installation.
    import stat
    # newDir = "/nsls2/xf12id1/users/" + str(cycle_id) + "/" + str(proposal_id) + "/scan_plots"
    # try:
    #     os.stat(newDir)
    # except FileNotFoundError:
    #     os.makedirs(newDir)
    #     os.chmod(newDir, stat.S_IRWXU + stat.S_IRWXG + stat.S_IRWXO)

    newDir = "/nsls2/xf12id1/users/" + str(cycle_id) + "/" + str(proposal_id) + "/GISAXS_data"
    try:
        os.stat(newDir)
    except FileNotFoundError:
        os.makedirs(newDir)
        os.chmod(newDir, stat.S_IRWXU + stat.S_IRWXG + stat.S_IRWXO)
    
    newDir = "/nsls2/xf12id1/users/" + str(cycle_id) + "/" + str(proposal_id) + "/GISAXS_analysis"
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

    newDir = "/nsls2/xf12id1/users/" + str(cycle_id) + "/" + str(proposal_id) + "/XRR_analysis/data3"
    try:
        os.stat(newDir)
    except FileNotFoundError:
        os.makedirs(newDir)
        os.chmod(newDir, stat.S_IRWXU + stat.S_IRWXG + stat.S_IRWXO)
       


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


    # newDir = "/nsls2/xf12id1/users/" + str(cycle_id) + "/" + str(proposal_id) + "/kibron"
    # try:
    #     os.stat(newDir)
    # except FileNotFoundError:
    #     os.makedirs(newDir)
    #     os.chmod(newDir, stat.S_IRWXU + stat.S_IRWXG + stat.S_IRWXO)

    newDir = "/nsls2/xf12id1/users/" + str(cycle_id) + "/" + str(proposal_id) + "/Jupyter_notebooks"
    try:
        os.stat(newDir)
    except FileNotFoundError:
        os.makedirs(newDir)
        os.chmod(newDir, stat.S_IRWXU + stat.S_IRWXG + stat.S_IRWXO)