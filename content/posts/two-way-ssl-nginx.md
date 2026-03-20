---
title: "How To Implement Two Way SSL With Nginx"
date: 2020-06-13T18:30:13+05:30
tags: ["ssl", "ngnix", "tls"]
categories: []
draft: false
cover:
    image: "img/two-way-ssl-nginx/nginx-logo.png"
    alt: "Nginx Logo (Courtesy: Wikimedia Commons)"
    relative: false
---

A couple of weeks ago, I was tasked with figuring out a way to enable two way SSL. I am a programmer, and have had only a limited experience with networking concepts like SSL/TLS in my short career. So I turned up blank on how I could make it possible. Moreover, the terminology you'd find online is not uniform. From a programming point of view, the term "Two way SSL" led me to limited  results, and I soon realized that other communities have different terminology. For example the "Two way SSL" is also known as "Mutual TLS" or "mTLS" or "Client Certificate Authentication" in Cloud/DevOps communitites. This makes finding the right resources online more difficult.

Our services have SSL enabled, but only the usual one -- similar to the one you'd find while visiting this website, but this was a unique thing for me as I didn't even know two way SSL existed. I figured out how it works. However, there were more problems with trying to understand how to implement this. Most guides that I found on the internet were very incomplete, and straight away skipped many parts for someone who'd be new to this. This is my attempt at explaining what I have learned, and documenting the same for future reference. It will not explain how two way SSL works, but how to make it work. If you need a quick refresher however, I would direct you to this [easy to understand article by Cloudflare]( https://blog.cloudflare.com/introducing-tls-client-auth/) explaining where and how mTLS is used.

This guide is only for Unix like systems like macOS or Linux. Though I tried this on Windows, but could not make it work.

# Prerequisites
1. Nginx
2. sudo privileges on your system


# Installing and Configuring Nginx 

If you are on macOS:
`brew install nginx`

If you are on Ubuntu/Debian:
`sudo apt-get install nginx`

After installation, ensure that nginx is running. You can check the status by:
`sudo service nginx status` or `sudo systemctl status nginx`

To start it:
`sudo service nginx start` or `sudo systemctl start nginx`

Navigate to `http://localhost`. If everything went well, you'd see the default Nginx page.

Now that we have Nginx, we'll configure it.

1. Locate the `nginx.conf` file. Usually it is at `/usr/local/etc/nginx/nginx.conf` or `/etc/nginx/nginx.conf`.
2. Add a `server` block.

```nginx
server {
    listen       443 ssl;
    server_name  localhost;

    ssl_certificate      /path/to/server.crt;
    ssl_certificate_key  /path/to/server.key;

    ssl_client_certificate /path/to/ca.crt;
    ssl_verify_client on;

    location / {
        root   html;
        index  index.html index.htm;
    }
}
```

This is a basic configuration for Nginx. I'll explain the lines we just added:
- `listen 443 ssl;`: This tells nginx to listen on port 443 (default for HTTPS) and use SSL.
- `server_name localhost;`: This is the hostname for our server.
- `ssl_certificate /path/to/server.crt;`: This is the path to the server certificate.
- `ssl_certificate_key /path/to/server.key;`: This is the path to the server key.
- `ssl_client_certificate /path/to/ca.crt;`: This is the path to the CA certificate that signed the client's certificate.
- `ssl_verify_client on;`: This is the magic line that enables Two Way SSL. It tells Nginx to request a certificate from the client and verify it against the `ssl_client_certificate`.


# Generating Certificates

Wait, we do not have the certificates yet! Let's generate them using `openssl`.

## 1. Create a Certificate Authority (CA)
Firstly, we need to create a CA which will sign our certificates.

Generate a key for the CA:
`openssl genrsa -des3 -out ca.key 4096`

You'll be asked for a passphrase. Remember it!

Now generate the CA certificate:
`openssl req -new -x509 -days 365 -key ca.key -out ca.crt`

Fill in the details as prompted.

## 2. Generate Server Certificate
Now we'll generate a certificate for our server, and get it signed by our CA.

Generate a key for the server:
`openssl genrsa -out server.key 2048`

Generate a CSR (Certificate Signing Request) for the server:
`openssl req -new -key server.key -out server.csr`

Fill in the details. **Ensure that the Common Name (CN) is `localhost`.**

Sign the server CSR with our CA:
`openssl x509 -req -days 365 -in server.csr -CA ca.crt -CAkey ca.key -set_serial 01 -out server.crt`


## 3. Generate Client Certificate
Similar to the server, we'll generate a certificate for the client.

Generate a key for the client:
`openssl genrsa -out client.key 2048`

Generate a CSR for the client:
`openssl req -new -key client.key -out client.csr`

Fill in the details.

Sign the client CSR with our CA:
`openssl x509 -req -days 365 -in client.csr -CA ca.crt -CAkey ca.key -set_serial 02 -out client.crt`


# Testing the Setup

Reload Nginx:
`sudo nginx -s reload`

Now try to access the server using `curl`:
`curl https://localhost`

You'll get an error like: `curl: (60) SSL certificate problem: self signed certificate in certificate chain`. This is because we're using self-signed certificates.

To bypass this, use the `-k` or `--insecure` flag:
`curl -k https://localhost`

Now you'll get a `400 Bad Request` with the message `No required SSL certificate was sent`. This is because Nginx is expecting a client certificate, but we haven't provided one.

Let's provide the client certificate and key:
`curl -k --cert client.crt --key client.key https://localhost`

Voila! You should now see the "Welcome to nginx!" message.

-----

# Summary of Files

For a quick reference, here are the commands to generate the files:

```bash
# CA
openssl genrsa -des3 -out ca.key 4096
openssl req -new -x509 -days 365 -key ca.key -out ca.crt

# Server
openssl genrsa -out server.key 2048
openssl req -new -key server.key -out server.csr
openssl x509 -req -days 365 -in server.csr -CA ca.crt -CAkey ca.key -set_serial 01 -out server.crt

# Client
openssl genrsa -out client.key 2048
openssl req -new -key client.key -out client.csr
openssl x509 -req -days 365 -in client.csr -CA ca.crt -CAkey ca.key -set_serial 02 -out client.crt
```

And your `nginx.conf` should look something like:

```nginx
ssl_certificate      /path/to/server.crt;
ssl_certificate_key  /path/to/server.key;

ssl_client_certificate /path/to/ca.crt;
ssl_verify_client on;
```

# Using the Client Certificate in a Browser

If you want to use the client certificate in a browser (like Chrome or Firefox), you'll need to export it to a `.p12` (PKCS#12) format.

```bash
openssl pkcs12 -export -clcerts -in client.crt -inkey client.key -out client.p12
```

Now import the `client.p12` file into your browser's certificate store. When you navigate to `https://localhost`, the browser will prompt you to select a certificate. Select the one you just imported, and you're good to go!

-----

I hope this helps you in implementing Two Way SSL with Nginx. If you have any questions or feedback, feel free to reach out to me on Twitter!
