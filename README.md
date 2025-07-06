```
Summary of commands :

    main.py
    Commands:
      set-test-name         Set test name
      test-constructor      Performance test constructor load run
      test-destructor       Performance test destructor

    cli-command-module
    Commands:
      deploy-test-at-grafana       deploy test at Grafana
      execute-local-linux-command  Execute local linux command
      execute-ssh-command          Execute remote ssh command
      scp-promdb-to-grafana        scp PromDB to Grafana
      
    openshift-api-module
    Commands:    
      create-namespace  Create namespaces with start and end index.
      create-pvc        Create pvc with start and end index.
      create-vm-cirros  Create VMs with start and end index.
      delete-namespace  Delete namespaces with start and end index.
      delete-vm         Delete vm with start and end index.
      
    openshift-oc-module
    Commands:
      attach-detach-pcv-vm            Attach or detach pvc in the given range to VM.
      create-delete-nncp              Create or delete basic NNCPs on each worker node
      dump-prometheus                 Dump prometheus data base
      empty-prometheus                Empty prometheus data base
      oc-create-vm-golden-image       Create vm from golden image.
      oc-create-vm-golden-image-range Create vm range from golden image.
      oc-get-templates-and-data-source get templates and data_source.
      oc-get-vms-node-spread          get the vms spread on the nodes.
      set-pvc-interface               Set pvc interface in the given range.
      test-maximum-pod                Test maximum pods on a cluster.
      
    virtctl-module
    Commands:
      hotplug-attach-pcv-to-vm  Attach hotplug pvc in the given range to VM.
      hotplug-detach-pcv-to-vm  Detach hotplug pvc in the given range to VM.
      migrate-node              Migrate all VMS from a node.
      start-vms                 Start VMs in the given range.
      stop-vms                  Stop VMs in the given range.
      test-vm-start-time        test_vm_start_time

Copy and run from any system :
Example:
rsync -a -Pav -e "ssh -l kni" --exclude 'cnv-perf/.venv/' /home/guchen/cnv-perf {jump host}:/home/kni/

At jump host :

sudo yum install rsync
sudo subscription-manager register --serverurl=subscription.rhsm.stage.redhat.com:443/subscription --baseurl=https://cdn.stage.redhat.com --username={userame} --password={passwor} --auto-attach
dnf install python3.11
dnf install python3.11-pip
curl -sSL https://install.python-poetry.org | python3.11 -
pip3.11 install poetry
cd /home/kni/cnv-perf/
poetry add paramiko
poetry add kubernetes
poetry add openshift
poetry update package



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
  test --start 1 --end 2 --sleep 1

Options:
  --name TEXT                 set VM name
  --template TEXT             set template name
  --cloud_user_password TEXT  set cloud user password
  --data_source TEXT          get data source name of the image
  --namespace TEXT            set namespace for the VM
  --start INTEGER             Start index for VM creation
  --end INTEGER               End index for VM creation
  -h, --help                  Show this message and exit.

**Performance Grafana and PromDB server :**

All test’s PromDB data is now stored at a designated server and can be viewed at the below portals, by default the last test data is online.
Grafana dashboard’s : http://grafana-scale-test.apps.cnv2.engineering.redhat.com/, user/password view/view or admin / 100yard- 
Prometheus DB : http://promdb-scale-test.apps.cnv2.engineering.redhat.com/graph

Lab of the server :
https://console-openshift-console.apps.cnv2.engineering.redhat.com/
VM access : ssh fedora@10.46.41.94 -p 22000

Procedure to get system matrix :

Before test create new DB -
oc delete po prometheus-k8s-0 -n openshift-monitoring
oc delete po prometheus-k8s-1 -n openshift-monitoring
Check promdb size-
oc exec -n openshift-monitoring prometheus-k8s-0 -- du -sh /prometheus
oc exec -n openshift-monitoring prometheus-k8s-1 -- du -sh /prometheus

After test dump db and tar it -
mkdir -p {test_name}
oc cp -n  openshift-monitoring prometheus-k8s-0:/prometheus -c prometheus  {test_name}
tar -czvf {test_name}.tar.gz {test_name}
rm -rf {test_name}

send db -
sshpass -p 100yard- scp -P 22000 {test_name}.tar.gz fedora@10.46.41.94:/home/fedora

Upload db on 10.46.41.94 -
sudo systemctl stop prometheus
sudo rm -rf /var/lib/prometheus/*
sudo cp {test_name}.tar.gz tmp_{test_name}.tar.gz
sudo tar -xvf tmp_{test_name}.tar.gz
sudo cp -R {test_name}/* /var/lib/prometheus/
sudo chown -R prometheus:prometheus /var/lib/prometheus/*
sudo rm -rf tmp_{test_name}.tar.gz
sudo rm -rf {test_name}
sudo systemctl start prometheus

Automation for procedure to get system matrix :
full automation -
poetry run python main.py test-constructor {test_name}
poetry run python main.py {all commands will trigger full procedure}

Single action automation -
poetry run python main.py set-test-name {test_name}
poetry run python main.py openshift-oc-module empty-prometheus
after test is finished :
poetry run python main.py openshift-oc-module dump-prometheus {test_name}
poetry run python main.py cli-command-module scp-promdb-to-grafana {test_name}
poetry run python main.py cli-command-module deploy-test-at-grafana {test_name}




