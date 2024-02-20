import commands
from types import FunctionType

commands_list : dict[str, FunctionType] = {"compliance"    : commands.CheckCompliance, 
                                           "dossier"       : commands.ModifyDossier,
                                           "region_list"   : commands.ListRegions,
                                           "rec_update"    : commands.UpdateRecs,
                                           "power_refresh" : commands.RefreshPower,
                                           "calc_vote"     : commands.CalculateVotes,
                                           "make_dispatch" : commands.MakeDispatch,
                                           "help"          : commands.DisplayHelp, 
                                           "exit"          : commands.Exit}

acceptable_flags : dict[str, list] = {"compliance"    : ["--ga", "--sc", "--export"], 
                                      "dossier"       : ["--add", "--del"],
                                      "region_list"   : None,
                                      "rec_update"    : ["--ga", "--sc"],
                                      "power_refresh" : ["--regions", "--export"],
                                      "calc_vote"     : ["--input", "--for", "--against", "--abstain", "--export"],
                                      "make_dispatch" : ["--type", "--input", "--forum", "--for", "--against", "--abstain"],
                                      "help"          : None,
                                      "exit"          : None}

nonargument_flags : list[str]     = ["--export", "--input"]

region_file          : str = "regions.csv"
recommendations_file : str = "recommendations.csv"
votepower_file       : str = "votepower.csv"
reccomendation_dispatch_file : str = "dispatch_template.txt"

