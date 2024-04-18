import git
import json
import os
import subprocess
import datetime
import glob


GITHUB_REF_NAME = os.getenv("GITHUB_REF_NAME", None)
GITHUB_ACTION_PATH = os.getenv("GITHUB_ACTION_PATH")
ACTION_TEMP_DIR = os.path.join(GITHUB_ACTION_PATH, "jarvis", "temp", "outputs")

JARVIS_WORKSPACE = os.getenv("JARVIS_WORKSPACE")
JARVIS_OUTPUT_DIR = os.path.join(JARVIS_WORKSPACE, "JARVIS", "workspace", "outputs")
JARVIS_TARGET= os.getenv("JARVIS_TARGET")
GITHUB_REPOSITORY = os.getenv("GITHUB_REPOSITORY")
GITHUB_WORKSPACE = os.getenv("GITHUB_WORKSPACE", "/home/cat/git/jarvis/actions-runner/_work/JARVIS_demo_test/JARVIS_demo_test")

PR_INFO = dict()


def construct_pr_info():
    with open(os.path.join(ACTION_TEMP_DIR, "issue_link")) as f:
        PR_INFO["issue_link"] = f.read().strip()
    PR_INFO["issue_number"] = PR_INFO["issue_link"].split("/")[-1]
    
    print(f"[DEBUG] generate pr title", flush=True)
    pr_title = f"Fixed #{PR_INFO['issue_number']}"
    PR_INFO["title"] = pr_title


def _gen_diff_list():
    output_dir = ACTION_TEMP_DIR
    print(f"Output temp dir: {output_dir}")
    diff_list=glob.glob(f"{output_dir}/**/*.diff", recursive=True)
    print(diff_list)

    return diff_list


def create_pull_request(patch_branch):
    pr_title = PR_INFO["title"]
    commit = os.getenv('GITHUB_SHA')
    print("[DEBUG] PR")
    pr_body = f"This PR is auto-patch by JARVIS for commit: {commit} Fixed #{PR_INFO['issue_number']}"
    #pr_command = f"gh pr create -B {GITHUB_REF_NAME} -H {patch_branch} -t \"{pr_title}\" -b\"{pr_body}\""
    #os.system(pr_command)

    token_path = f"{GITHUB_ACTION_PATH}/token.txt"
    with open(token_path, 'r') as token_file:
        token = token_file.read().strip()

    logout_result = subprocess.run(['gh', 'auth', 'logout', '-h', 'github.com', '-u', 'github-actions[bot]'], capture_output=True, text=True)
    print("Logout STDOUT:", logout_result.stdout)
    print("Logout STDERR:", logout_result.stderr)

    env = os.environ.copy()
    env['GH_TOKEN'] = token

    subprocess.run(['gh', 'auth', 'login', '--with-token'], input=env['GH_TOKEN'], text=True, env=env)
    result = subprocess.run(['gh', 'auth', 'status'],capture_output=True)
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)
    pr_command = [
        "gh", "pr", "create",
        "-B", GITHUB_REF_NAME,
        "-H", patch_branch,
        "-t", pr_title,
        "-b", pr_body
    ]
    result = subprocess.run(pr_command, text=True, capture_output=True)

    if result.returncode == 0:
        print("PR Success", result.stdout)
    else:
        print("PR Failed", result.stderr)


# def py_dos2unix(inf):
#     with open(inf, 'rt', encoding='UTF8',  errors='ignore') as f:
#         text = f.read().replace("r\r\n", "r\n")
#     with open(inf, 'wt', encoding='UTF8',  errors='ignore') as f:
#         f.write(text)


def run():
    print(f"[DEBUG] create pr", flush=True)

    try:

        # patch_path = f"{ACTION_TEMP_DIR}/fix_violation.patch"
        # print(f"Patch path: {patch_path}")
        
        # os.system("git clean -xdf")
        os.system(f"git checkout {GITHUB_REF_NAME}")
        os.system("git checkout .")
        now = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
        patch_branch = f"{GITHUB_REF_NAME}-auto-patch-{now}"
        os.system(f"git checkout -b {patch_branch}")
        # print("find . -type f -exec dos2unix {{}} \;")
        # os.system("find . -type f -exec dos2unix {{}} \;")
        diff_list = _gen_diff_list()
        for diff in diff_list:
            print(diff)
            # print(diff.replace(".diff", "").replace("/outputs", JARVIS_TARGET))
            # os.system(f"dos2unix {diff.replace('.diff', '').replace('/outputs', JARVIS_TARGET)}")
            target_path = GITHUB_WORKSPACE + diff.split("outputs")[1].replace('.diff', '')
            print(target_path)
            # py_dos2unix(target_path)
            os.system(f"git apply < {diff}")
        os.system(f"git add .")
        os.system(f"git commit -m \"Fixed automatically #{PR_INFO['issue_number']} by JARVIS\"")

        os.system("echo debugging!!!")
        os.system(f"ls {GITHUB_ACTION_PATH}")
        # os.system(f"gh auth login --with-token < {GITHUB_ACTION_PATH}/token.txt")
        os.system(f"git push origin {patch_branch}")
        create_pull_request(patch_branch)
        os.system(f"git checkout {GITHUB_REF_NAME}")
    
    except Exception as e:
        print(f"[Error] {e}")

print(f"[+] github_action_path : {GITHUB_ACTION_PATH}")
construct_pr_info()
run()
