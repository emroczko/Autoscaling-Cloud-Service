apt-get install -y nginx
echo "Hello $1!" > /var/www/index.html

cat <<CONF > /etc/nginx/nginx.conf
worker_processes  1;

events {
    worker_connections  1024;
}

http {
    include       mime.types;

    server {
        listen       9103;
        server_name  localhost;

        location / {
            root   /var/www;
            index  index.html index.htm;
        }
    }
}
CONF

systemctl restart nginx
