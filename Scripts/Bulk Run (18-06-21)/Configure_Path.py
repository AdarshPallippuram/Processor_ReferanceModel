import configparser
cnfg = configparser.ConfigParser()
cnfg.optionxform = str
cnfg['PATHS'] = {'DIR': r"C:\Modeltech_pe_edu_10.4a\examples\SAC\Instructions",
        'PM_LOCATE': r"C:\Modeltech_pe_edu_10.4a\examples\SAC\pm_file.txt",
        'DM_LOCATE': r"C:\Modeltech_pe_edu_10.4a\examples\SAC\dm_file.txt",
        'DMrdfl_LOCATE': r"C:\Modeltech_pe_edu_10.4a\examples\SAC\DMrd_files",
        'MEMfail_LOCATE': r"C:\Modeltech_pe_edu_10.4a\examples\SAC\MEMfail_LOCATE"}
cnfg['IDENTIFIER'] = {'idntfr': "_"}
cnfg['AVOID'] = {'pm_file.txt': "",
        'dm_file.txt': "",
        "README.md.":"",
        "Owner.md":""}
with open('Path.ini', 'w') as pathfl:
    cnfg.write(pathfl)
