Step 1: Create a cluster on GKE. 'connect' to this cluster by adding it to
kubectl config file. GKE provides a command to do this.

Step 2: Create storage resources by executing the `start_disk.sh` script in
the kubernetes directory.
$ cd kubernetes
$ ./start_disk

Step 3: Edit the job.yaml.jinja2 file by replacing the IP of the nfs-server
to the one that was assigned in your cluster.

Step 4: Launch a workload:
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
$ cd kubernetes
$ python render_template.py     # passing in any arguments you would like

To scale up, you can execute the `scale_up.sh`. First parameter is number of
images to render. Second parameter is the number of parallel workers per
image. Currently, all workers just save the final image with the same name
'final_image.png' on the server. If we want to allow multiple different
images to get saved (with randomized scenes), then that can easily be
implemented. It was left this way to save space on disk, b/c for demonstration
purposes, that is not necessary to get the point across.
