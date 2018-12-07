# Step 1: Create a cluster on GKE.

# Step 2: Create storage resources by executing the `start_disk.sh` script in
# the kubernetes directory.
$ cd kubernetes
$ ./start_disk

# Step 3: Edit the job.yaml.jinja2 file by replacing the IP of the nfs-server
# to the one that was assigned in your cluster.

# Step 4: Launch a workload:
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
$ cd kubernetes
$ python render_template.py     # passing in any arguments you would like

# To scale up, you can execute the `scale_up.sh`. First parameter is number of
# images to render. Second parameter is the number of parallel workers per
# image.
