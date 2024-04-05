with open('pibooth_bu.cfg','r') as f:
    get_all=f.readlines()

with open('parsed_cfg.json','w') as f:
    f.writelines('{\n')
    for idx, line in enumerate(get_all):
        if not line.startswith('#') and ('=' in line):
            confkey = line.split("=")[0].strip()
            arg = line.split("=")[1].strip()
            if idx == (len(get_all)-1):
                f.writelines(f'"{confkey}":"{arg}"\n')
            else:
                f.writelines(f'"{confkey}":"{arg}",\n')
    f.writelines('}\n')

with open('parsed_cfg_exp.json','w') as f:
    f.writelines('{\n')
    for idx, line in enumerate(get_all):
        if line.startswith('#'):
            conf_info = line.strip()
        elif '=' in line:
            confkey = line.split("=")[0].strip()
            if idx == (len(get_all)-1):
                f.writelines(f'"{confkey}":"{conf_info}"\n')
            else:
                f.writelines(f'"{confkey}":"{conf_info}",\n')
    f.writelines('}\n')
