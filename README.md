```
setup :

curl -sSL https://install.python-poetry.org | python -
pip install poetry
poetry add paramiko
poetry add kubernetes
poetry add openshift


copy and run from any system :
Example:
rsync -a -Pav -e "ssh -l kni" /home/guchen/cnv-perf {hostname}:/home/kni/guchen/

**To get all modules in the program:**

poetry run python main.py -h 
Usage: main.py [OPTIONS] COMMAND [ARGS]...

  A command-line tool with multiple functions.

Options:
  -h, --help  Show this message and exit.

Commands:
  cli-command-module
  openshift-api-module
  openshift-oc-module
  virtctl-module

**To get all commands in a module :**

poetry run python main.py openshift-oc-module -h 
Usage: main.py openshift-oc-module [OPTIONS] COMMAND [ARGS]...

Options:
  -h, --help  Show this message and exit.

Commands:
  oc-create-vm-golden-image       Create vm from golden image.
  oc-create-vm-golden-image-range
                                  Create vm range from golden image.
  oc-get-templates-and-data-source
                                  get templates and data_source.

**To get command :**

poetry run python main.py openshift-oc-module oc-create-vm-golden-image-range -h
Usage: main.py openshift-oc-module oc-create-vm-golden-image-range [OPTIONS]

  Create vm range from golden image.

  Example: poetry run python main.py openshift_oc_module oc-create-vm-golden-image-range --name fedora-test --template
  fedora-desktop-tiny  Example: poetry run python main.py openshift_oc_module oc-create-vm-golden-image-range --name
  fedora-test --template fedora-desktop-tiny  --cloud_user_password 100yard- --data_source fedora --namespace scale-
  test --start 1 --end 2

Options:
  --name TEXT                 set VM name
  --template TEXT             set template name
  --cloud_user_password TEXT  set cloud user password
  --data_source TEXT          get data source name of the image
  --namespace TEXT            set namespace for the VM
  --start INTEGER             Start index for VM creation
  --end INTEGER               End index for VM creation
  -h, --help                  Show this message and exit.
