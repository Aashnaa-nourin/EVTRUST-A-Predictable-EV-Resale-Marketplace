# AWS Free Tier Deployment Guide for EVTrust

Follow these steps to deploy your Django project to an AWS EC2 instance.

## 1. Launch an AWS EC2 Instance
1.  Log in to the [AWS Management Console](https://aws.amazon.com/console/).
2.  Navigate to **EC2** and click **Launch Instance**.
3.  **Name**: `EVTrust-Server`
4.  **OS**: Ubuntu 22.04 LTS (Free Tier Eligible).
5.  **Instance Type**: `t2.micro` (or `t3.micro` if available in your region).
6.  **Key Pair**: Create a new key pair (RSA, .pem) and download it.
7.  **Network Settings**: 
    - Check **Allow SSH traffic from Anywhere** (or your IP).
    - Check **Allow HTTP traffic from the internet**.
    - Check **Allow HTTPS traffic from the internet**.

## 2. Server Initial Setup
Connect to your server via SSH:
```bash
ssh -i "your-key.pem" ubuntu@your-ec2-public-ip
```

Update system and install dependencies:
```bash
sudo apt update
sudo apt install -y python3-pip python3-venv nginx git
```

### [CRITICAL] Setup Swap File (Memory Management)
Because `t2.micro` has only 1GB RAM and this project uses **TensorFlow**, you MUST set up a swap file to avoid Out-Of-Memory errors:
```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fetc/fstab
```

## 3. Deployment Steps on Server
1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/your-username/your-repo-name.git
    cd your-repo-name
    ```
2.  **Create Virtual Environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
3.  **Install Requirements**:
    ```bash
    pip install --upgrade pip
    pip install -r requirements.txt
    ```
4.  **Configure Environment Variables**:
    ```bash
    cp .env.example .env
    nano .env
    ```
    *Update `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=False`, and `DJANGO_ALLOWED_HOSTS` with your EC2 Public IP.*

5.  **Run Migrations and Collect Static Files**:
    ```bash
    python manage.py migrate
    python manage.py collectstatic --noinput
    ```

## 4. Configure Gunicorn (Application Server)
Copy the template from the `deploy/` directory to your system:
```bash
sudo cp deploy/gunicorn.service /etc/systemd/system/gunicorn.service
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
```

## 5. Configure Nginx (Reverse Proxy)
1.  Copy Nginx config:
    ```bash
    sudo cp deploy/nginx.conf /etc/nginx/sites-available/evtrust
    ```
2.  Update the `server_name` in `/etc/nginx/sites-available/evtrust` with your IP.
3.  Link and Restart Nginx:
    ```bash
    sudo ln -s /etc/nginx/sites-available/evtrust /etc/nginx/sites-enabled
    sudo nginx -t
    sudo systemctl restart nginx
    ```

## 6. Verify Deployment
Open your browser and navigate to `http://your-ec2-public-ip`. Your EVTrust marketplace should now be live!
