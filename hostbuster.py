import requests
import json
import csv
import os
import sys
import getopt

key = None

def main():
    target = None
    global key

    argv = sys.argv[1:]

    try:
        opts, args = getopt.getopt(argv, "i:k:", ["inputfile", "key"])

    except getopt.GetoptError as e:
        print(e)
        opts = []
        sys.exit()

    for opt, arg in opts:
        if opt in ["-i", "--inputfile"]:
            target = arg
        elif opt in ["-k", "--key"]:
            key = arg

    acquire_target(target)

def acquire_target(target):
    try:
        with open(target, "r") as f:
            target = f.read().splitlines()
            for i in target:
                query(i)

    except:
        print("could not open targets.txt. Check if file exists and if it is readable\n")

    finally:
        f.close()

def query(target):
    try:
        print(f"searching for new targets for domain: {target}")
        r = requests.get(f"https://crt.sh/?q={target}&output=json")
        rawdata = json.loads(r.text)
        parse_n_store(rawdata,target)       

    except:
        print(f"Could not find results for {target}. Please check if domain exists")


def parse_n_store(rawdata, target):
    x=0
    output = []
    for i in rawdata:
        output.append(rawdata[x]["common_name"])
        x+=1

    try:
        if os.path.exists(f"./output/{target}.txt"):
            print("FILE EXISTS!")
            compare_results(output, target)

        else:
            with open(f'./output/{target}.txt', 'w') as f:
                for i in output:
                    f.write(i + "\n")

                f.close()
                print("**DONE**")

    except Exception as e:
        print(e)


def compare_results(output, target):
    print("comparing data..")
    with open(f'./output/{target}.txt', 'r') as f:
        x = f.read().splitlines()
        
        #Compare the old and new results and if there are any new targets.
        difference = [item for item in output if item not in x]
        f.close()

        if not difference:
            print("nothing to see here!")
        
        else:
            #Remove duplicates by converting list items to dict keys which need to be unique, then convert back to new list.
            dedup_list = list(dict.fromkeys(difference))

            print(dedup_list)
            print(target)
            report_results(dedup_list, target)

            with open(f'./output/{target}.txt', 'a') as f:
                for i in dedup_list:
                    print(f"writing new result: {i} to file..")
                    f.write(i + "\n")
                f.close()


def report_results(deduplist, target):
    chatid = 251892229
    send_text = f"https://api.telegram.org/bot{key}/sendMessage?chat_id={chatid}&parse_mode=Markdown&text={deduplist}"
    response = requests.get(send_text)

    print(response)

if __name__ == "__main__":
    main()

