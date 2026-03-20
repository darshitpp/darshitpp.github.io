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

## Install

Install[^1] nginx using `apt` command on your Linux system.

```shell
sudo apt update
sudo apt install nginx
```
This will install all of Nginx on the path `/opt/nginx`. All the configuration files we will be editing for two-way SSL would be found within this directory.

## Configure Nginx to start

Before starting up Nginx for use, we need to enable some ports on the firewall that our Nginx can listen incoming connections from.

```shell
sudo ufw app list
```
Output:
```shell
Available applications:
  Nginx Full
  Nginx HTTP
  Nginx HTTPS
  OpenSSH
```

The utility `ufw` can be used to manage our firewall. Though a knowledge of `ufw` is not necessary for us, more information can be found [here](https://www.linux.com/training-tutorials/introduction-uncomplicated-firewall-ufw/).

You can see in the above output that the utility responds us with four profiles. When we installed Nginx, it registered itself with the `ufw` utility with three profiles.

* `Nginx HTTP` allows Nginx to listen through port 80, for normal HTTP traffic.
* `Nginx HTTPS` allows Nginx to listen through port 443, for HTTPS traffic.
* `Nginx Full` is a combination of the above both, enabling port 80 and 443 both.

We will enable `Nginx Full` as we have to use our server for SSL, but using normal HTTP connections is not an uncommon use-case either. To enable it, run:

```shell
sudo ufw allow 'Nginx Full'
```

You should see the activated profile if you run the below command 

```shell
sudo ufw status
```
Output:
```shell
Status: active

To                         Action      From
--                         ------      ----
OpenSSH                    ALLOW       Anywhere                  
Nginx Full                 ALLOW       Anywhere                  
OpenSSH (v6)               ALLOW       Anywhere (v6)             
Nginx Full (v6)            ALLOW       Anywhere (v6)
```

The Nginx service should already be up and running now. You can check by executing

```shell
systemctl status nginx
```
Output:
```shell
● nginx.service - A high performance web server and a reverse proxy server
   Loaded: loaded (/lib/systemd/system/nginx.service; enabled; vendor preset: enabled)
   Active: active (running) since Fri 2018-04-20 16:08:19 UTC; 3 days ago
     Docs: man:nginx(8)
 Main PID: 2369 (nginx)
    Tasks: 2 (limit: 1153)
   CGroup: /system.slice/nginx.service
           ├─2369 nginx: master process /usr/sbin/nginx -g daemon on; master_process on;
           └─2380 nginx: worker process
```

[^1]: The main resource for installing Nginx is this [tutorial by DigitalOcean](https://www.digitalocean.com/community/tutorials/how-to-install-nginx-on-ubuntu-18-04). All the relevant steps have been described in my article.

# Creating Certificates

## Terminology

* **Certificate Authority (CA)**: This is an Organization which provides you a Certificate (the `.crt` file). In reality, anyone (including yourself) can be the CA which issues certificates
* **Certificate Signing Request (CSR `.csr`)**: An "input form" with details (like Name, Organization, Address, etc.) filled by the requester of the certificate which is submitted to the CA
* **Private Key (`.key`)**: The private key file used by the CA in conjunction with CSR to sign and generate the certificates
* **Certificate (`.crt`)**: The certificate generated by the CA
* **Self Signed Certificate**: Consider yourself as a Certificate Authority (CA) and generate the `.crt` files.


Now that we know the terminology, it would be easier to proceed with generating the certificates. The following part of the tutorial requires root/superuser privileges, so switch to the super user using the `sudo su` command.

Create a directory called `certs` under the root of the file-system which will hold all the certificates and related files.


```shell
# Create directory
mkdir /certs 
# Change directory to /certs
cd /certs
# Verify the present working directory
pwd
```

Output:
```shell
/certs
```

In this tutorial, we would be designating ourselves as a Certificate Authority, and then self-sign and generate the certificates.

## Generate Certificate Authority (CA) files

We would be first generating a CA key, which would be the basis for all further certificate generation.

```shell
openssl genrsa -des3 -out ca.key 4096
```
Output:
```shell
Generating RSA private key, 4096 bit long modulus (2 primes)
.............................................................++++
....................................................................................................................................................................................++++
e is 65537 (0x010001)
Enter pass phrase for ca.key:<passphrase>
Verifying - Enter pass phrase for ca.key:<passphrase> 
```
Command options:

* `genrsa`: generate RSA private key
* `-des3`: encrypts the output key using des3 encryption
* `-out`: specifying the output key file
* `4096`: size of private key in bits

This generates a file named `ca.key` in the current directory. You would have to provide a password/passphrase for the key. For the purposes of this tutorial, I'll be using the same passphrase whenever required.

`<passphrase>` = `root`

The next step is the generation of `ca.crt`

```shell
openssl req -new -x509 -days 3650 -key ca.key -out ca.crt
```
Output:
```shell
Enter pass phrase for ca.key:<passphrase>
```
Command options:
* `req`: used for creating certificate requests
* `-new`: generates new certificate request
* `-x509`: outputs a new self-signed certificate instead of a certificate request
* `-days 3650`: validity of certificate (in this case, 10 years/3650 days)
* `-key`: RSA key to be used for generating the certificate
* `-out`: output file for the certificate

Once you enter the passphrase (which is the same as we put in the previous step), it'll ask you to provide more information for the self-signed certificate.

```shell
You are about to be asked to enter information that will be incorporated
into your certificate request.
What you are about to enter is what is called a Distinguished Name or a DN.
There are quite a few fields but you can leave some blank
For some fields there will be a default value,
If you enter '.', the field will be left blank.
-----
Country Name (2 letter code) [AU]:
State or Province Name (full name) [Some-State]:
Locality Name (eg, city) []:
Organization Name (eg, company) [Internet Widgits Pty Ltd]:CertAuth
Organizational Unit Name (eg, section) []:
Common Name (e.g. server FQDN or YOUR name) []:
Email Address []:
```

Note the `Organization Name` parameter is named as `CertAuth` for this example. This is because we are a CA and CAs should ideally be independent to enable other parties to trust other parties and establish a chain of trust.

A PEM file certificate would also be needed. This file is way of encoding the certificates.[^2] To create a PEM file, simply do the following:

[^2]: More info [here](https://serverfault.com/questions/9708/what-is-a-pem-file-and-how-does-it-differ-from-other-openssl-generated-key-file)

```shell
cat ca.key > ca.pem
cat ca.key >> ca.pem
```

The `ca.key` would be something like

```shell
-----BEGIN RSA PRIVATE KEY-----
Proc-Type: 4,ENCRYPTED
DEK-Info: DES-EDE3-CBC,0E2D38C130456B75

3+0Em2EKRkmCCu79bR7E2uFy/G1huIGEGsItwDf0C70Hf2bmUUDYazK/CPZxZCut
PDximngoGaLSdLQ2HWGjjCe59pJxxZknxHu9QVy3mIWLixAZWevDUnoK1q+Wqy0M
-----END RSA PRIVATE KEY-----
-----BEGIN CERTIFICATE-----
MIIFSzCCAzOgAwIBAgIUeawaQJUIAPKOKhrIJDjMVCYVx4MwDQYJKoZIhvcNAQEL
BQAwNTELMAkGA1UEBhMCQVUxEzARBgNVBAgMClNvbWUtU3RhdGUxETAPBgNVBAoM
-----END CERTIFICATE-----
```
## Generating Client/User Certificates

At this point, we have three files in the `certs` directory.
```text
ca.key
ca.crt
ca.pem
```

We now would be generating client/user certificates.
The command to generate the `user.key` is similar to the one used to create the `ca.key`

```shell
openssl genrsa -des3 -out user.key 4096
```
Output:
```shell
Generating RSA private key, 4096 bit long modulus (2 primes)
.....................................................................................................................................................++++
.......................++++
e is 65537 (0x010001)
Enter pass phrase for user.key:
Verifying - Enter pass phrase for user.key:
```

As mentioned earlier, the passphrase to be used for `user.key` is still the same.

The client/user certificate aren't supposed to be self-signed, and we would need to generate a CSR. It means the signing is to be done by a CA(even though in this case, we own the CA!). The way to do this is

```shell
openssl req -new -key user.key -out user.csr
```
Output:
```shell
Enter pass phrase for user.key:<passphrase> 
You are about to be asked to enter information that will be incorporated
into your certificate request.
What you are about to enter is what is called a Distinguished Name or a DN.
There are quite a few fields but you can leave some blank
For some fields there will be a default value,
If you enter '.', the field will be left blank.
-----
Country Name (2 letter code) [AU]:
State or Province Name (full name) [Some-State]:
Locality Name (eg, city) []:
Organization Name (eg, company) [Internet Widgits Pty Ltd]:User
Organizational Unit Name (eg, section) []:
Common Name (e.g. server FQDN or YOUR name) []:
Email Address []:

Please enter the following 'extra' attributes
to be sent with your certificate request
A challenge password []:
An optional company name []:
```
The `Organization Name` would be `User` as this certificate is for a Client/User. **DO NOT** keep it the same as the one for CA.

The next step would be to create a User Certificate from the User CSR.

```shell
openssl x509 -req -days 365 -in user.csr -CA ca.crt -CAkey ca.key -set_serial 01 -out user.crt
```
Output:
```shell
Signature ok
subject=C = AU, ST = Some-State, O = User
Getting CA Private Key
Enter pass phrase for ca.key:<passphrase>
```

Command options:
* `x509`: standard format for public key certificates
* `-CA`: the CA certificate
* `-CAkey`: the key to generate the certificate from
* `-set_serial 01`: the serial version of the certificate to be generated. The user certificate can be regenerated by incrementing the serial number from the same `user.csr` after 365 days when it expires.

You can see that it displays data from the CSR, and then uses the CA key to generate `user.crt`.

To enable us to use the certificate from a web browser, we would need to create the certificate in the PFX file format.

```shell
openssl pkcs12 -export -out user.pfx -inkey user.key -in user.crt -certfile ca.crt
```
Output:
```shell
Enter pass phrase for user.key:<passphrase>
Enter Export Password:<passphrase>
Verifying - Enter Export Password:<passphrase>
```

You can verify if the generated certificate can be decrypted using the CA certificate by the following command

```shell
openssl verify -verbose -CAfile ca.crt user.crt
```
Output:
```shell
user.crt: OK
```

The files that we currently have in the directory are

```text
ca.key
ca.crt
ca.pem
user.key
user.csr
user.crt
user.pfx
```

## Generating Server Certificates

This is similar to generating the User certificates, with the following commands

Generate the Server key. For server certificates, the standard naming convention seems to be `<website-domain-name>`.`<key>`

```shell
openssl genrsa -out nginx.mssl.com.key 4096
```
Output:
```shell
Generating RSA private key, 4096 bit long modulus (2 primes)
.....................................++++
.........................++++
e is 65537 (0x010001)
```

Use the above generated key to generate a CSR.

```shell
openssl req -new -key nginx.mssl.com.key -out nginx.mssl.com.csr
```
Output:
```shell
You are about to be asked to enter information that will be incorporated
into your certificate request.
What you are about to enter is what is called a Distinguished Name or a DN.
There are quite a few fields but you can leave some blank
For some fields there will be a default value,
If you enter '.', the field will be left blank.
-----
Country Name (2 letter code) [AU]:
State or Province Name (full name) [Some-State]:
Locality Name (eg, city) []:
Organization Name (eg, company) [Internet Widgits Pty Ltd]:Server
Organizational Unit Name (eg, section) []:
Common Name (e.g. server FQDN or YOUR name) []:nginx.mssl.com
Email Address []:

Please enter the following 'extra' attributes
to be sent with your certificate request
A challenge password []:
An optional company name []:
```

Make sure to put the `Organization Name` as `Server` and `Common Name` (which is the website name) as `nginx.mssl.com`

We can now use the CSR along with the CA files to generate the CRT for our server.

```shell
openssl x509 -req -days 365 -sha256 -in nginx.mssl.com.csr -CA ca.crt -CAkey ca.key -set_serial 1 -out nginx.mssl.com.crt
```
Output:
```shell
Signature ok
subject=C = AU, ST = Some-State, O = Server, CN = nginx.mssl.com
Getting CA Private Key
Enter pass phrase for ca.key:<passphrase>
```

All the certificates are now ready for our use!

```text
ca.key
ca.crt
ca.pem
user.key
user.csr
user.crt
user.pfx
nginx.mssl.com.key
nginx.mssl.com.csr
nginx.mssl.com.crt
```

# Setting up our "Website" with Nginx

Of course, we aren't setting up a *real* website. But we do want to make our SSL authentication work on the domain `nginx.mssl.com`. We can do this by a little "hack" by changing our `/etc/hosts` file.

Fire up a new shell, and use
```shell
sudo vim /etc/hosts
```

Add the following line to the file and save.

```text
127.0.0.1 nginx.mssl.com
```

This will enable your local machine to resolve the domain `nginx.mssl.com` to your locahost.

The website will not work at the moment -- you'd have to specify the sources/web pages it needs to serve when requested.

Create a file `index.html` on the directory path `/usr/share/nginx/mssl` with the contents:

```html
<html>
  <body>
    <h1>Welcome to nginx!-mutual ssl test</h1>
  </body>
</html>
```

If the TLS handshake is successful, the web server should serve the file created above.

# Configuring the Nginx server to enable two way SSL

All our certificates are at root in `/certs` directory. For simplicity, we would be copying the certificates to `/etc/nginx/certs` directory.

```shell
cp -r /certs /etc/nginx/certs
```

Also ensure that the certificates can be used by nginx service by providing them the access

```shell
chmod 777 -R certs/
```

We would not be fiddling with the default nginx configuration which is present in the `nginx.conf` file. Instead, we would be creating a new file called `proxy.conf` using in the `/etc/nginx/sites-available` directory.

Create the file `proxy.conf` using the command
```shell
cd /etc/nginx/sites-available
touch proxy.conf
```
Enter the contents as the following (Notice the comments have more explanation):

```text
server {
    # Listen on port 443 for HTTPS connections
    listen  443;

    # Turn SSL on
    ssl on;

    # Name of the server/website
    server_name nginx.mssl.com;

    # See https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_ssl_server_name
    proxy_ssl_server_name on;
    
    # This is the server SSL certificate
    ssl_certificate      /etc/nginx/certs/nginx.mssl.com.crt;

    # This is the server certificate key
    ssl_certificate_key /etc/nginx/certs/nginx.mssl.com.key;

    # Important: 
    # This is the CA cert against which the client/user will be validated
    # In our case since the Server and the Client certificate is 
    # generated from the same CA, we use the ca.crt 
    # But in actual production, the Client certificate might be 
    # created from a different CA
    ssl_client_certificate /etc/nginx/certs/ca.crt;

    # Enables mutual TLS/two way SSL to verify the client
    ssl_verify_client on;

    # Number of intermediate certificates to verify. Good explanation of 
    # certificate chaining can be found at
    # https://cheapsslsecurity.com/p/what-is-ssl-certificate-chain/
    ssl_verify_depth 2;

    # Any error during the connection can be found on the following path
    error_log /var/log/nginx/error.log debug;
    
    ssl_prefer_server_ciphers on;
    ssl_protocols TLSv1.1 TLSv1.2;
    ssl_ciphers 'ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES256-GCM-SHA384:kEDH+AESGCM:ECDHE-RSA-AES128-SHA256:ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA:ECDHE-ECDSA-AES128-SHA:ECDHE-RSA-AES256-SHA384:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES256-SHA:ECDHE-ECDSA-AES256-SHA:DHE-RSA-AES128-SHA256:DHE-RSA-AES128-SHA:DHE-RSA-AES256-SHA256:DHE-DSS-AES256-SHA:AES128-GCM-SHA256:AES256-GCM-SHA384:ECDHE-RSA-RC4-SHA:ECDHE-ECDSA-RC4-SHA:RC4-SHA:HIGH:!aNULL:!eNULL:!EXPORT:!DES:!3DES:!MD5:!PSK';

    keepalive_timeout 10;
    ssl_session_timeout 5m;

    # Matches the "root" of the website
    # If TLS handshake is successful, the request is routed to this block
    location / {
        # path from which the website is served from
        root /usr/share/nginx/mssl;
        # index file name
        index index.html index.htm;
    }
}
```

Nginx has a good [Beginner's Guide to Nginx](https://nginx.org/en/docs/beginners_guide.html).

To enable Nginx to use the above configuration, we also have to link the same in the `/etc/nginx/sites-enabled` directory.

To accomplish this, use

```shell
ln -s /etc/nginx/sites-available/proxy.conf /etc/nginx/sites-enabled/proxy.conf
```

This creates a symbolic link into `/etc/nginx/sites-enabled/proxy.conf` from `/etc/nginx/sites-available/proxy.conf`. Consider it as you having many server configurations in the `sites-available`, but only what you chose to "enable" in the `sites-enabled` will be active.

We now just have to restart the Nginx for the configuration to be active!

```shell
systemctl restart nginx
```

I'll be using Postman to test our changes. However, you'll need to configure Postman to send the Client Certificates with the request[^3].

[^3]: [Client Certificates: Postman Learning Center](https://learning.postman.com/docs/postman/sending-api-requests/certificates/)

To configure the Certificates, navigate to Settings -> Certificates Tab.

There will be a section to add the CA Certificate named `CA Certificates`, and this certificate should be a PEM file. Select the `ca.pem` from `/etc/nginx/certs`. A mistake would be to select the file from the root directory `/certs` but this will not work as Postman wouldn't be able to access the file.

There would be another section below for `Client Certificates`. Click on `Add Certificate`, and put the details as the following:

* Host: `nginx.mssl.com`
* CRT File: `/etc/nginx/certs/user.crt`
* KEY File: `/etc/nginx/certs/user.key`
* PFX File: `/etc/nginx/certs/user.pfx`
* Passphrase: `<passphrase>`

Now try to fire a GET request to the domain `https://nginx.mssl.com`. If everything was configured successfully, you'll get the following response:
```html
<html>
  <body>
    <h1>Welcome to nginx!-mutual ssl test</h1>
  </body>
</html>
```

If there's an error in the configuration, you'll get the following error response:
```html
<html>
  <head>
    <title>400 No required SSL certificate was sent</title>
  </head>

  <body bgcolor="white">
    <center>
      <h1>400 Bad Request</h1>
    </center>
    <center>No required SSL certificate was sent</center>
    <hr>
    <center>nginx/1.14.0 (Ubuntu)</center>
  </body>
</html>
```

Hope this post was of some help!!

Reference:

1. [This](https://medium.com/@Jenananthan/nginx-mutual-ssl-one-way-ssl-with-multiple-clients-ae87b3de0935) article is good for the demo part.
2. The post [Client Certificate Auth With Nginx](https://jason.whitehorn.us/blog/2019/02/01/client-certificate-auth-with-nginx/) was instrumental in explaining the `ssl_client_certificate` directive and how to use it.
2. [This](https://fardog.io/blog/2017/12/30/client-side-certificate-authentication-with-nginx/) post is as close to perfection as it gets regarding the steps for generating Certificates, but I couldn't manage to make it work fully with Nginx. (Especially because it skips the demo part + it could be a little more descriptive with generation of the certificates)
3. [This article](https://rollout.io/blog/how-to-set-up-mutual-tls-authentication/) is good, but still unclear for someone starting out.
4. I used [this article](https://www.ssltrust.in/help/setup-guides/client-certificate-authentication) to actually learn about generating the certificates especially because it provides easy commands and decent explanation.
