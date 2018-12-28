# Deploying Django App on an AWS EC2 instance

## Summary
Use [these instructions](https://github.com/gschool/dsi-project-proposals/blob/master/host_app_on_amazon.md) as your guide if you need one.

* Set up an AWS instance
* Set up environment on your EC2 instance
* Push your code to github
* SSH into the instance and clone your repo
* Set up Nginx
* Switch to Gunicorn
* Run Django app on instance

## 1. Set up AWS EC2 instance
Background on using AWS can be found [here](https://docs.google.com/presentation/d/1VRUjgDXMz5uayMcJMF3YOQg7QpQF9RJ0zUO984SG3N8/edit).

1. Go to [Amazon EC2](https://console.aws.amazon.com/ec2)

2. Click on `Launch Instance`.

3. In the `Quick Start` menu, select the Ubuntu Server.

4. Choose the smallest instance necessary to run your app, most likely this will be a Micro. Micro is on the free tier (if you're in the first year of using AWS) and is likely to be plenty for your purposes.

5. Click `Configure Instance` and select `IAM role`.

6. Cick `Configure Security Group`. Select existing or create new security group that allows SSH (port 22), HTTP (port 80), and HTTPS (port 443) traffic.

7. Click `Review and Launch`.

8. Create a key-pair if you don't have one already. This should download a file called `<something>.pem`

7. Move .pem file to ~/.ssh/ and change the permissions of your key-pair with this command:

    ```bash
    mv <something>.pem ~/.ssh/<something>.pem
    chmod 400 <something>.pem
    ```

## 2. Add HTTP Access

You need to set up your instance so that it allows HTTP requests.

1. Click on `View Instances`.

2. Scroll down to `Security Groups` to see which one it is.

3. Go to `Security Groups` (on the left). Check the correct one and go to `Actions` and "Edit Inbound Rules".

4. Click `Add Rule` and choose "HTTP". Note that the port is 80, this is the port that is accessed by a browser by default.

## 3. Allocate Elastic IP Address
It will be nice to not need to check on the IP address of your instance every time you launch. This will also be very helpful if you buy a domain name for your web app.

1. Go to `Elastic IPs` (on the left).

2. Click on `Allocate New Address`.

3. Once you get the address, select it, click on `Actions` and choose "Associate Address". Click in the "Instance" box, and choose your instance.

## 4. Connect to instance
SSH can be used to access a remote machine via the terminal. SSH can be used between any 2 computers as long as ssh-server and ssh-client are installed and machines are reachable via internet.

SSH is used with either public-private key encryption or a password (less secure). With public-private key encryption:
- A public and private key pair is generated
- Anyone with the public key can encrypt, but only you can decrypt with the private key
- Use a key pair for each resource you want to access

To set up a key pair:
- Create and import key pairs as described in [AWS docs](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html#having-ec2-create-your-key-pair).
- Store private keys on every computer you want to use to access the remote resource
- Set permissions of key file on computer:

  ```bash
  chmod 400 ~/.ssh/private_key.pem
  ```

To ssh into instance:

  ```bash
  ssh -i ~/.keys/key-pair.pem -X -o TCPKeepAlive=yes ubuntu@ec2=123.456.78.9
```

- You can create an alias ssh config for frequently accessed instances

*~/.ssh/config*

```sh
Host ec2_instance1
  HostName ec2-18-221-82-151.us-east-2.compute.amazonaws.com
  User ubuntu
  ForwardX11 yes
  TCPKeepAlive yes (keeps idle connection alive)
  IdentityFile ~/.keys/ec2_instance1.pem
```

Accessed by

  ```bash
  ssh ec_instance1
```

## 5. Set up environment

You use `ssh` (secure shell) to connect to your machine. You will then be in the world of terminal. You will only have editors that run in terminal (like `vi` or `emacs`). It's good to get comfortable doing at least small edits in one of those, but you can also do the edits on your machine and then use `scp`.

1. Download miniconda: `wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh`
2. Install anaconda: `bash Miniconda3-latest-Linux-x86_64.sh`
3. `conda` or `pip` install whatever other libraries your app needs to run. Create a `conda` environment if needed.

  ```bash
  conda create -n <env-name> python=3.6
  source activate <env-name>
  conda install django>=2.1.2
  conda install --yes --file requirements.txt
  ```

4. Install any programs you are using (like git):

    ```bash
    sudo apt-get update
    sudo apt-get install git
    ```

## 6. Set up ports
Run the following line of code at the command line on the instance:

  ```bash
  sudo iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-ports 8000
  sudo apt-get install iptables-persistent
  ```

The first line forwards requests at port 80 to port 8000. This is important.

The second line makes it so you can persist your iptable settings. When you run it you should be prompted to save your current iptable settings. Choose yes.

### 7. Clone github respository
Clone github repository onto your EC2 instance to keep your code and compure resources synced.
    - You can go straight ahead and `git clone https://github.com/username/reponame` to your EC2 instance and your done.  
    - To remove the friction of supplying your username/password every time you push/pull, run the following commands **on your remote machine**:
        - Create an SSH key: `ssh-keygen -b 4096`
        - Tell SSH to use it. (this assumes that there's no existing SSH config on the instance) `echo "IdentityFile ~/.ssh/id_rsa" > ~/.ssh/config`
        - Then copy and paste the public key as a new authorized SSH key on GitHub `cat ~/.ssh/id_rsa.pub`
        - Then `git clone git@github.com:username/reponame` just works.

## 8. Configure Django for deployment
1. export SITENAME=staging.engmatthew.com
2. in `<app>/settings.py` change `ALLOWED_HOSTS = ['*']`
3. Migrate database `python manage.py migrate --noinput`

# Settings for Production

## 9. Set up Nginx and Gunicorn
1. Install Nginx on Server

  ```bash
  sudo apt install nginx
  sudo systemctl start nginx OR $sudo service nginx start
  ```

2. You should now be able to go to the URL address and see a Welcome to Nginx page. If not, you may need to configure your AWS security group to allow the server to open on port 80 and relaunch the instance to ensure it has taken affect.

3. Configure Nginx to send requests for staging site along to Django. Create the file on server `/etc/nginix/sites-available/<site-name>` that says it will only listen for our staging domain and will proxy all requests to the local port 8000 where it expects Django waiting to respond.

  ``` sh
  server {
    listen 80;
    sever_name staging.engmatthew.com

    location /static {
            alias /home/ubuntu/<git-repository-folder>/static;
    }

    location / {
            proxy_pass http://unix:/tmp/staging.engmatthew.socket;
            }
    }
  ```
4. Create a symlink to the config file to add it to the enabled sites using Debian/Ubuntu. The real config file is in `sites-available`, and a symlink is in `sites-enabled`, which makes it easier to switch sites on and off.

  ```bash
  export SITENAME=staging.engmatthew.com
  cd /etx/nginx/sites-enabled
  sudo ln -s /etc/nginx/sites-available/$SITENAME $SITENAME
  ```

Can remove default 'Welcome to Nginx config' to avoid confusion:

  ```bash
  $sudo rm /etc/nginx/sites-enabled/default
  ```

5. Reload nginx and restart server

  ```bash
  $sudo systemctl reload nginx
  $cd ~/<repository or site location>
  $python manage.py runserver 8000
  ```

[Troubleshooting on EC2 instance](https://stackoverflow.com/questions/16054407/having-trouble-running-nginx-on-ec2-instance)

## 10. Switch to Gunicorn

1. `conda` or `pip install gunicorn`
2. Provide path to a WSGI server, usually a function called `application`. `gunicorn tdd-python-book.wsgi:application`

  ```bash
  gunicorn <django-app-name>.wsgi:application
  ```

3. Get Nginx to serve static files by collecting static files

  ```
  python manage.py collectstatic --noinput
  ```

4. Add `location` directive to the config file


5. Also, change location to use Unix socket domain so Nginx and Gunicorn can talk to each other by changing proxy settings

  ``` sh
  server {
    listen 80;
    sever_name staging.engmatthew.com

    location /static {
            alias /home/ubuntu/<git-repository-folder>/static;
    }

    location / {
            proxy_pass http://unix:/tmp/staging.engmatthew.com.socket;
            }
    }
  ```
5. Reload Nginix and restart Gunicorn, telling it to listen on a socket instead of default port (otherwise use `gunicorn <project-name>.wsgi:application`)

*python-tdd-book/*

  ```bash
  sudo systemctl reload nginx
  gunicorn --bind \ unix:/tmp/staging.engmatthew.com.socket superlists.wsgi:application
  ```

## 12. Change Django settings for production
Todo

## 11. Managing sessions with Tmux
```bash
$sudo apt-get install screen tmux
$screen -ls (list screen sessions)
$screen -S session_name commands_of_choice
Detach using CTRL+a CTRL+d
$screen -r session_name (attach to a certain session)
