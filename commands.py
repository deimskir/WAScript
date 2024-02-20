import csv
import time
import os 

import nationstates

import config

def _ReadFile(filepath : str, flat_list : bool=True) -> list:
    with open(filepath, "r") as file:
        file_reader = csv.reader(file, delimiter=",")

        starting_list = [row for row in file_reader]
        output = []

        if not flat_list:
            return starting_list
        
        for row in starting_list:
            output.extend(row) 

        return output

def _MatchFlagsArgs(flags : list, arguments : list, do_duplication : bool=False) -> dict:
    if len(arguments) == 0 and not all(flag in config.nonargument_flags for flag in flags):
        return (-1, "No arguments were provided")
    
    output = {}
    for idx, flag in enumerate(flags):
        if flag in config.nonargument_flags:
            continue

        try:
            output[flag] = arguments[idx]
        except IndexError:
            if not do_duplication:
                output[flag] = []
                continue

            output[flag] = arguments[idx-1]

    return output

def _DoInputLoop(regions_list : list,) -> tuple:
    print("Vote options are: FOR, AGAINST, ABSTAIN or NONE (or a blank input). Options are case insensitive.")

    for_power, against_power, abstain_power, nonvote_power = 0, 0, 0, 0
    nonvoters = []
    flags_args = {"--for" : [], "--against" : [], "--abstain" : []}
    
    for region in regions_list:
        user_input = input(f"{region[0].replace("_", " ").title()}'s Vote: ").lower().strip()

        match user_input:
            case "for":
                for_power += int(region[3])
                flags_args["--for"].append(region[0])
            case "against":
                against_power += int(region[3])
                flags_args["--against"].append(region[0])
            case "abstain":
                abstain_power += int(region[3])
                flags_args["--abstain"].append(region[0])
            case _:
                nonvote_power += int(region[3])
                nonvoters.append(region[0])

    return for_power, against_power, abstain_power, nonvote_power, flags_args, nonvoters


def _CalcVotePercent(side_power : int, total_power : int) -> float:
    return round(((side_power/total_power) * 100), 2)

def CheckCompliance(client : nationstates.Nationstates, flags : list, *args) -> str | int:
    """Checks the compliance of the given regions in the versus the current recommendations. Flags:
    \n--ga [regions] -> check the list of regions [regions] for ga compliance.\n--sc [regions] -> check the list of regions [regions] for sc compliance.\n--export -> export non-compliant regions to a file.
    \nif both flags are provided but only one list is, the one list will be checked for both flags.\nIf no arguments are provided, the regions dossier will be checked.\n"""
    
    # if no specific arguments are provided, read the region file 
    if args == ([],):
        args = [_ReadFile(config.region_file)]
    else:
        args = args[0]

    # match the order of args to flags
    flag_args = _MatchFlagsArgs(flags, args, True)

    # check for flags, and collect the right output depending on which ones we have 
    writing_ga, writing_sc = False, False

    if "--ga" in flags:
        writing_ga = True
        ga_region_objects = [client.region(region) for region in flag_args["--ga"]]
        ga_delegates = [client.nation(region.delegate) for region in ga_region_objects]



    if "--sc" in flags:
        writing_sc = True
        sc_region_objects = [client.region(region) for region in flag_args["--sc"]]
        sc_delegates = [client.nation(region.delegate) for region in sc_region_objects]

    # extract the current recs in the format "GA" : "FOR", etc
    current_recs  = {i[0] : i[1] for i in _ReadFile(config.recommendations_file, flat_list=False)} 

    # initialise temp variables 
    noncompliant_ga, noncompliant_sc = [], []

    if writing_ga:
        for idx, nation in enumerate(ga_delegates): 
            compliance = True if ((nation.gavote == current_recs["GA"]) or (current_recs["GA"] is None)) else False

            if not compliance:
                noncompliant_ga.append([nation.nation_name, ga_region_objects[idx].region_name, nation.gavote])

    if writing_sc:
        for idx, nation in enumerate(sc_delegates):
            compliance = True if ((nation.scvote == current_recs["SC"]) or (current_recs["SC"] is None)) else False

            if not compliance:
                noncompliant_sc.append([nation.nation_name, sc_region_objects[idx].region_name, nation.scvote])

    compliance_out = ""
    
    # create an output depending on which regions are not complying as calculated earlier
    if writing_ga:
        compliance_out += ("The following regions are non-compliant in the GA:\n")

        for item in noncompliant_ga:
            compliance_out += f"{item[1]}{' '*(30-len(item[1]))}-> (current delegate: {item[0]}, current vote: {item[2]})" + "\n"

        if noncompliant_ga == []:
            compliance_out += ("None\n")

    if writing_sc:
        compliance_out += ("The following regions are non-compliant in the SC:\n")

        for item in noncompliant_sc:
            compliance_out += f"{item[1]}{' '*(30-len(item[1]))}-> (current delegate: {item[0]}, current vote: {item[2]})" + "\n"
        
        if noncompliant_sc == []:
            compliance_out += ("None\n")
    
    # if we did not include export flags, then just return the string for print-out
    # otherwise, write all of the output to the file
    if "--export" not in flags:
        return compliance_out
    
    with open("compliance_report.txt", "w") as compliance_report:
        compliance_report.write(compliance_out)

    return 0

def ModifyDossier(client : nationstates.Nationstates, flags : list, *args):
    """Update the region dossier file as specified in the configuration file. flags:\n\n--add [regions] -> adds regions [regions] to the dossier.\n--del [regions] -> deletes regions [regions] from the dossier.\n"""
    current_dossier = _ReadFile(config.region_file)

    flags_args = _MatchFlagsArgs(flags, args[0])

    if type(flags_args) == tuple:
        return flags_args
    
    try:
        for region in flags_args["--add"]:
            current_dossier.append(region)
    except KeyError:
        pass

    try:
        for region in flags_args["--del"]:
            current_dossier.remove(region)
    except (KeyError, ValueError):
        pass

    with open(config.region_file, "w") as region_dossier:
        for idx, region in enumerate(current_dossier):
            if idx != len(current_dossier) -1 :
                region_dossier.write(f"{region},")
                continue

            region_dossier.write(region)

    return 0
            
def ListRegions(client : nationstates.Nationstates, flags : list, *args):
    "List all regions in the regions dossier.\n"
    regions = _ReadFile(config.region_file)
    print("Current regions in dossier:")

    for region in regions:
        print(region)

    return 0

def UpdateRecs(client : nationstates.Nationstates, flags : list, *args):
    """Update recommendations and write them to the recommendations.csv file. Flags:\n\n--ga [rec] -> update the current SC recommendation.\n--sc [rec] -> update the current SC recommendation."""
    current_recs  = {i[0] : i[1] for i in _ReadFile(config.recommendations_file, flat_list=False)} 
    flags_args = _MatchFlagsArgs(flags, args[0])

    if any(len(value) > 1 for value in flags_args.values()):
        return (-1, "Too many values provided for recommendation (expected max 1 per flag)")
    
    if "--ga" in flags:
        current_recs["GA"] = flags_args["--ga"][0].upper()

    if "--sc" in flags:
        current_recs["SC"] = flags_args["--sc"][0].upper()

    with open(config.recommendations_file, "w") as recommendations:
        recommendations.write(f"GA,{current_recs["GA"]}\n")
        recommendations.write(f"SC,{current_recs['SC']}")
    
    return 0


def RefreshPower(client : nationstates.Nationstates, flags : list, *args):
    """Regenerate the voting powers of all regions specified. Flags:\n\n--regions [regions] -> update power for specified regions.\n--export -> export the power ratings into a file.\n\nIf no regions are specified, the regions dossier will be used."""
    
    if args == ([],):
        args = [_ReadFile(config.region_file)]
    else:
        args = args[0]

    if (flags == []) or (flags == ["--export"]):
        flags_args = {"--regions" : args[0]}
    else:
        flags_args = _MatchFlagsArgs(flags, args)

    raw_output = []
    string_out = ""

    total_delegate_votes, total_wa_nations, total_power = 0,0,0

    for region in flags_args["--regions"]:
        current_region = client.region(region)
        delegate_votes = int(current_region.delegatevotes)
        numwanations   = int(current_region.get_shards("numwanations")["numunnations"])
        total_regional_power    = delegate_votes + numwanations

        total_delegate_votes += delegate_votes
        total_wa_nations += numwanations
        total_power += total_regional_power
        raw_output.append([region, delegate_votes, numwanations, total_regional_power])

    raw_output.append(["TOTAL", total_delegate_votes, total_wa_nations, total_power])

    for row in raw_output:
        string_out += "{:25}{:6}{:6}{:6}\n".format(row[0], row[1], row[2], row[3])

    if "--export" in flags:
        with open(config.votepower_file, "w", newline="") as votepower_file:
            writer = csv.writer(votepower_file,delimiter=",")
            writer.writerows(raw_output)

    return string_out

def CalculateVotes(client : nationstates.Nationstates, flags : list, nums_only=False, *args):
    """Calculate vote percentage and recommendation based on given inputs. Flags:\n\n--for [regions] -> the regions which voted 'FOR'.\n--against [regions] -> the regions which voted 'AGAINST'.\n--abstain [regions] -> the regions which voted to 'ABSTAIN'.\n--input -> be prompted to input each nation INSTEAD OF PROVIDING VALUES TO OTHER FLAGS FOR THE VOTES\n\nAny region in the dossier but not provided in arguments will be marked as a non-vote."""
    flags_args = _MatchFlagsArgs(flags, args[0] if args else [])
    if isinstance(flags_args, tuple):
        return flags_args
    
    regions_power = _ReadFile(config.votepower_file, False)
    total_power = int(regions_power[-1][3])

    for_power, against_power, abstain_power, nonvote_power = 0, 0, 0, 0
    nonvoters = []
    if "--input" in flags:
        for_power, against_power, abstain_power, nonvote_power, flags_args, nonvoters = _DoInputLoop(regions_power[:-1],)
    else:
        for flag in ("--for", "--against", "--abstain"):
            if flag not in flags:
                flags_args[flag] = []

        for region in regions_power[:-1]:
            if region[0] in flags_args["--for"]:
                for_power += int(region[3])
            elif region[0] in flags_args["--against"]:
                against_power += int(region[3])
            elif region[0] in flags_args["--abstain"]:
                abstain_power += int(region[3])
            else:
                nonvote_power += int(region[3])
                nonvoters.append(region[0])

    for_percent, against_percent, abstain_percent, nonvote_percent = (_CalcVotePercent(power, total_power) for power in (for_power, against_power, abstain_power, nonvote_power))
    max_percent, recommendation = None, None, 
    mandatory = "NON-BINDING"

    string_out = ""

    if for_percent > max(against_percent, abstain_percent):
        max_percent, recommendation = for_percent, "FOR"
    elif against_percent > abstain_percent:
        max_percent, recommendation = against_percent, "AGAINST"
    else:
        max_percent, recommendation = abstain_percent, "NO RECOMMENDATION"
    
    if max_percent > 50:
        mandatory = "BINDING"

    string_out += f"{mandatory} vote {recommendation}, by a vote of {for_percent}% FOR, {against_percent}% AGAINST, and {nonvote_percent}% ({len(nonvoters)} members) absent.\n\n"
    string_out += f"vote, power, percentage, regions\n"
    string_out += f"FOR, {for_power}, {for_percent}, {','.join(flags_args['--for']) if flags_args['--for'] else None},\nAGAINST, {against_power}, {against_percent}, {','.join(flags_args['--against']) if flags_args['--against'] else None},\nABSTAIN, {abstain_power}, {abstain_percent}, {','.join(flags_args['--abstain']) if flags_args['--abstain'] else None},\nNon-Voting, {nonvote_power}, {nonvote_percent}, {','.join(nonvoters) if nonvoters != [] else "None"}"
    
    if nums_only:
        return {"consensus" : recommendation, "aye" : [for_percent, [x.replace("_", " ").title() for x in flags_args["--for"]]], "nay" : [against_percent, [x.replace("_", " ").title() for x in flags_args["--against"]]], "abstain" : [abstain_percent, [x.replace("_", " ").title() for x in flags_args["--abstain"]]], "turnout" : [len(regions_power[:-1])-len(nonvoters), len(regions_power[:-1]), 100.0-nonvote_percent]}
    if not "--export":
        return string_out

    with open(f"{time.strftime("%Y%M%d%H%M%S", time.gmtime())}_vote_report.csv", "w") as report_file:
        report_file.write(string_out)
        return string_out

def MakeDispatch(client : nationstates.Nationstates, flags : list, *args):
    """Create a recommendation dispatch for the current resolution based on the region dossier or a manually provided subset. flags:\n\n--type [type] -> the type of the resolution to fetch (either "sc" or "ga")\n--forum [link] a link to the forum post for the resolution\n--for [regions] --against [regions] --abstain [regions] -> manually provide regions for, against or abstaining from the vote\n--input -> be prompted to input each nation's vote INSTEAD OF PROVIDING INPUT TO OTHER FLAGS FOR THE VOTES.\n\nThis function uses the file-path for the template as defined in config.py"""
    flags_args = _MatchFlagsArgs(flags, args[0] if args else [])
    if isinstance(flags_args, tuple):
        return flags_args
    
    match flags_args["--type"]:
        case ["ga"]:
            wa_object = client.wa(1)
            res_type = "GENERAL ASSEMBLY"
        case ["sc"]:
            wa_object = client.wa(2)
            res_type = "SECURITY COUNCIL"
        case ["ga", "sc"]:
            return (-1, "A resolution can only be one of 'ga' and 'sc', not both")
        case _:
            return (-1, f"Unknown flag provided: '{flags[0]}'")
        
    if any(x in flags for x in ["--for", "--against", "--abstain"]):
        numbers_output = CalculateVotes(client, ["--for", "--against", "--abstain"], True, flags_args["--for"], flags_args["--against"], flags_args["--abstain"])
    else:
        numbers_output = CalculateVotes(client, ["--input"], True)

    for x in ("aye", "nay", "abstain"):
        numbers_output[x][1] = "".join([f"[*] [region]{region}[/region]\n" for region in numbers_output[x][1]])

    resolution = wa_object.resolution
    prop_name = resolution["name"]
    author = resolution["proposed_by"]
    res_content = resolution["desc"]
    forum_link = flags_args["--forum"][0] if flags_args["--forum"] else "https://forum.nationstates.net/viewforum.php?f=8"
    
    res_content = res_content.replace("&#146;", "'")
    res_content = res_content.replace("&quot;", "\"")
    
    try:
        coauthor = ", ".join([f"[nation]{x}[/nation]" for x in resolution["coauthor"].values()])
    except KeyError:
        coauthor = ""

    full_contents = res_content + f"{"\n\nCoauthor: " if coauthor != "" else ""}{coauthor}"

    tags = ["$name", "$auth", "$con", "$typ", "$for","$aye", "$avt","$nay", "$nvt", "$abs", "$abvt","$tof", "$tow"]
    replace_values = [prop_name, author, full_contents, res_type, forum_link, round(numbers_output["aye"][0], 2), numbers_output["aye"][1], round(numbers_output["nay"][0], 2), numbers_output["nay"][1], round(numbers_output["abstain"][0],2), numbers_output["abstain"][1], f"{numbers_output["turnout"][0]}/{numbers_output["turnout"][1]}", numbers_output["turnout"][2]]
    replace_values = [str(x) for x in replace_values]

    with open(config.reccomendation_dispatch_file, "r") as dispatch_file:
        contents = dispatch_file.read()

        match numbers_output["consensus"]:
            case "FOR":
                contents = contents.replace("$rec", "[color=#2fc657][u]FOR[/u][/color]")
                contents = contents.replace("AYES: $aye%", "[b]AYES: $aye%[/b]")
            case "AGAINST":
                contents = contents.replace("$rec", "[color=#ea4335][u]AGAINST[/u][/color]")
                contents = contents.replace("NAYS: $nay%", "[b]NAYS: $nay%[/b]")
            case "NO RECOMMENDATION":
                contents = contents.replace("vote [/color]$rec", "[/color] [u]ABSTAIN ON[/u]")
                contents = contents.replace("ABSTENTIONS: $abs%", "[b]ABSTENTIONS: $abs%[/b]")

        for item in tuple(zip(tags, replace_values)):
            contents = contents.replace(*item)

        with open(f"{time.strftime("%Y%m%d%H%M%S", time.gmtime())}_recommendation_dispatch.txt", "w") as output:
            output.write(contents)

    return 0

    # dispatch template tokens:
    # $name -> proposal name
    # $auth -> author
    # $con -> content of the proposal, author, coauthor [NOFLAG]
    # $typ -> type of the proposal (ga/sc) [NOFLAG]
    # $for -> forum link [FLAGGED]
    # $rec -> recommendation [NOFLAG -> GET FROM CSV]

    # $aye -> aye % (weighted)
    # $avt -> regions voting aye

    # $nay -> nay % (weighted)
    # $nvt -> regions voting nay

    # $abs -> abstentions
    # $abvt -> regions abstaining

    # $tof -> turnout as a fraction
    # $tow -> turnout % (weighted)


def DisplayHelp(client : nationstates.Nationstates, flags : list, *args):
    "display help for (a) command(s). Flags:\n\n--[name of command] -> display help for [command].\n\nMultiple command flags may be chained together. No flags displays help for all commands."
    os.system("clear" if os.name == "posix" else "cls")
    if not flags:
        for item in list(config.commands_list.keys()):
            print(item)
            print(config.commands_list[item].__doc__+ "\n" +("-"*10)+"\n")
    else:
        for item in flags:
            print(item)
            print(config.commands_list[item.strip("--")].__doc__ + "\n" +("-"*10)+"\n")

    return 0

def Exit(client, flags, *args) -> None:
    os._exit(0)

if __name__ == "__main__":
    client = nationstates.Nationstates("Deims Kir testing script")
    print(CalculateVotes(client, ["--input"], True, ["0"]))
    

    

