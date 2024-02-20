# URAScript

An improved (?) script used for WA bloc management.

## Starting Out

To begin, install pynationstates using the following command:
```
pip install nationstates
```
Then, install *all* of the files listed in the repository (main.py, commands.py, config.py, all of the csv files and the dispatch_template.txt file). Place them all inside of the same directory, and then you should be good to run the program, by running main.py.

## Configuration
If any additional configuration is required, the config.py file can be edited. This principally applies to editing the file paths for the csv and txt files; messing with any of the other parts of this file may cause problems in the program's operation.

## Commands

There are a number of commands available within the program. These commands in turn have flags available, through which inputs are available. Whenever an input is expected, it must be provided in [braces]. When multiple values are provided in one argument, separate them by commas; [hello, world, hello world].

---

### **compliance**

Checks the compliance of the given regions in the dossier (default: ``regions.csv``) versus the current recommendations. Flags:

--ga [regions] -> check the list of regions [regions] for ga compliance.

--sc [regions] -> check the list of regions [regions] for sc compliance.

--export -> export non-compliant regions to a file.

if both flags are provided but only one list is, the one list will be checked for both flags.

If no arguments are provided, the regions dossier will be checked.

---

### **dossier**
Update the region dossier file (defailt: ``regions.csv``). flags:

--add [regions] -> adds regions [regions] to the dossier.

--del [regions] -> deletes regions [regions] from the dossier.

---

### **region_list**

List all regions in the regions dossier (default: ``regions.csv``).

---

### **rec_update**

Update recommendations and write them to the recommendations file (default: ``recommendations.csv``). Flags:

--ga [rec] -> update the current SC recommendation.

--sc [rec] -> update the current SC recommendation.

---

### **power_refresh**

Regenerate the voting powers of all regions specified. Flags:

--regions [regions] -> update power for specified regions.

--export            -> export the power ratings into a file.

If no regions are specified, the regions dossier (default: ``regions.csv``) will be used.

---

### **calc_vote**

Calculate vote percentage and recommendation based on given inputs. Flags:

--for     [regions] -> the regions which voted 'FOR'.

--against [regions] -> the regions which voted 'AGAINST'.

--abstain [regions] -> the regions which voted to 'ABSTAIN'.

--input -> be prompted to input each region's vote.

If using --input, any arguments to other flags will be ignored. Don't use them together!

Any region in the dossier but not provided in arguments will be marked as a non-vote.

---

### **make_dispatch**

Create a recommendation dispatch for the current resolution based on the region dossier or a manually provided subset. flags:

--type [type] -> the type of the resolution to fetch (either "sc" or "ga")

--forum [link] a link to the forum post for the resolution

--for [regions] --against [regions] --abstain [regions] -> provide regions for, against or abstaining from the vote

--input -> be prompted to input each region's vote.

If using --input, any arguments to other flags will be ignored. Don't use them together!

This function uses the file-path for the template as defined in ``config.py``.

this command requires certain flags within the dispatch template, a list of which can be found below:
```
    # $name -> proposal name
    # $auth -> author
    # $con -> content of the proposal, author, coauthor 
    # $typ -> type of the proposal (ga/sc) 
    # $for -> forum link 
    # $rec -> recommendation 

    # $aye -> aye % (weighted)
    # $avt -> regions voting aye

    # $nay -> nay % (weighted)
    # $nvt -> regions voting nay

    # $abs -> abstentions
    # $abvt -> regions abstaining

    # $tof -> turnout as a fraction
    # $tow -> turnout % (weighted)
```


---

### **help**

display help for (a) command(s). Flags:

--[name of command] -> display help for [command].

Multiple command flags may be chained together. Providing no flags displays help for all commands.
