import pandas as pd

def parse_cfg(cfg_file,tags=None):
    """Function that returns config file with given tags as dictionar

    Parameters
    ----------
    cfg_file : str
        full directory to config file
    tags : list, optional
        list of tags to search the cgf_file

    Returns
    -------
    config_dict : dict
        dictionary with keys given in tags, and values
        extracted from cfg_file. If one tag doesn't exist,
        value corresponded will be None, else value is of
        type str, or list if multiple values exist for
        same key.
    """
    if tags == None:
        tags = []
        with open(cfg_file) as o:
            for line in o:
                if line[0] in ["\n","#"]: continue
                tag = line.split()[0]
                if tag in tags:
                    raise RuntimeError("Tag <%s> appears twice in cfg"+\
                            "file <%s>" %(tag, cfg_file))
                tags.append(tag)
    config_dict = {}
    print tags
    with open(cfg_file) as o:
        for line in o:
            if line[0] in ["\n","#"]: continue
            linesplit = line.split()
            readLineTag = line.split()[0]
            for tag in tags:
                if tag == readLineTag:
                    config_dict[tag] = []
                    for val in linesplit[1:]:
                        if val.startswith("#"): 
                            break
                        elif "#" in val:
                            val = val[:val.index("#")]
                            config_dict[tag].append(val)
                            break
                        if val == "=":
                            continue
                        config_dict[tag].append(val)
                    if len(config_dict[tag]) == 1:
                        config_dict[tag] = config_dict[tag][0]
                    tags.remove(tag)
    for tag in tags:
        logging.warning("Couldn't parse <"+tag+"> from "+cfg_file)
        config_dict[tag] = None
    return config_dict

def get_all_candidates(path_to_cands, header=None):
    """
    Parse all_candidates.dat file as a pandas DataFrame
    """
    if header == None:
        header = 'infer'
    return pd.read_table(path_to_cands, names=header)

