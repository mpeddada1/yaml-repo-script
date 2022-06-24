import os

import ruamel.yaml
import tempfile
from git import Repo

def mark_required(repo_name):
  temporary_directory = tempfile.mkdtemp()
  git_url = "git@github.com:googleapis/" + repo_name

  # clone repo into temporary directory
  repo_destination = temporary_directory + "/" + repo_name
  repo_instance = Repo.clone_from(git_url, repo_destination)
  branch_name = 'require-graal'
  repo_instance.git.checkout('-b', branch_name)

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
  repo_instance.index.add(sync_repo_yaml)
  repo_instance.index.commit("chore: add native image checks as required")
  push_output = repo_instance.git.push('--set-upstream', repo_instance.remote().name, branch_name)
  print(push_output)

mark_required()