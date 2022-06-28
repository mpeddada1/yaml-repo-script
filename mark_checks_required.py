import os
import ruamel.yaml
import tempfile

def mark_all_required():
  with open("repos.txt") as repos_file:
    repos = [line.rstrip() for line in repos_file.readlines()]
    for repo_name in repos:
      mark_required(repo_name)

def mark_required(repo_name):
  temporary_directory = tempfile.mkdtemp()
  git_url = "git@github.com:googleapis/" + repo_name

  # clone repo
  os.system("git clone " + git_url)
  os.system("mv " + repo_name + " " + temporary_directory)
  repo_destination = temporary_directory + "/" + repo_name
  os.chdir(repo_destination)

  # branch_name = 'require-graal'
  os.system("git checkout -b require-graal-check")

  # parse settings yaml file and set Kokoro Native Image tests as required.
  yaml = ruamel.yaml.YAML()
  sync_repo_yaml = os.path.join(repo_destination, ".github/sync-repo-settings.yaml")
  with open(sync_repo_yaml) as repo_settings:
    contents = yaml.load(repo_settings)
    for ruleDict in contents["branchProtectionRules"]:
      if ruleDict["pattern"] == "main":
        required_checks_list = ruleDict["requiredStatusCheckContexts"]
        required_checks_list.append("Kokoro - Test: Java GraalVM Native Image")
        required_checks_list.append("Kokoro - Test: Java 17 GraalVM Native Image")

  # To ensure that our indentation is okay
  yaml.indent(sequence=4, offset=2)

  with open(sync_repo_yaml, 'w') as repo_settings:
    yaml.dump(contents, repo_settings)

  # Add on github, commit and push
  os.system("git add " + sync_repo_yaml)
  os.system("git commit -m 'chore: add native image checks as required'")
  os.system("git push origin require-graal-check")
  os.system("gh pr create --title 'chore: mark native image checks as required' --body ''")


mark_all_required()