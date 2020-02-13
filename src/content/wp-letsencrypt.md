Title: Let's Encrypt with Wordpress Multisite
Date: 2019-10-03
Slug: wp-letsencrypt
Category: weblog
Tags: tech, apache, httpd, wordpress, letsencrypt


With Wordpress Multisite on a single webroot (eg, /var/www/html), we can define multiple domain namespaces and point them at any internal directory structure we want. That is, we can easily configure Apache such that a request for the domain/path goes anywhere on the server:

example.com -> /var/www/html  
example.com/path -> /var/www/html/path  
example.com/path2 -> /home/data/path2  
example2.com -> /var/www/html/example2  
subdomain.example2.com -> /var/www/subdomain-example2  

For letsencrypt, let's point all requests for /.well-known/acme-challenge validation - *irrespective of the domain* - to a single directory that certbot can write to. That means we do not have to run a separate validation for each domain renewal, and we don't have to stop/start the web server so Certbot can respond to the the challenge independently (and don't even *think* about futzing with TXT records for DNS validation).

**Assumptions:**
Single-tenant host system (VPS, physical server, EC2 instance, etc, NOT cPanel shared hosting)
Apache web server  
ModAlias
ModSSL
Certbot


I used CentOS 7 and Apache on a single virtual machine instance for this.


In your webroot, create the validation directory. Certbot will write all challenge files here.
```
# mkdir -p /var/www/html/.well-known/acme-challenge
```

**Default** Apache Virtualhost Config for Wordpress Multi-site
Apache will read all .conf files in alphabetical order, and the very first Virtualhost configuration in that order will be the "default" vhost served for a hostname if none other matches. Name this  file 00-default.conf or similar to ensure that it is the first one read by Apache (the number "0" comes before the letter "a" in computing) if you have other sites served by Apache.

```
[root@s html]# cat /etc/httpd/conf.d/00-default.conf

# This rewrites configures all requests to a single challenge root.
AliasMatch ^/.well-known/acme-challenge/(.*)$ /var/www/html/.well-known/acme-challenge/$1


SSLStrictSNIVHostCheck off

# I run Wordpress [grudgingly] out of the wp directory.
# I keep a few host-specific files under /var/www/html.

<VirtualHost 198.51.100.57:80>
 ServerName example.com
 DocumentRoot /var/www/html/wp
 ServerAdmin goaway@example.com
 ErrorLog logs/example.com-error_log
 LogLevel alert rewrite:trace3
 TransferLog logs/example.com-access_log
</VirtualHost>


<VirtualHost 198.51.100.57:443>
 DocumentRoot "/var/www/html/wp"
 ServerName example.com:443
 ErrorLog logs/example.com-ssl_error_log
 TransferLog logs/example.com-ssl_access_log
 LogLevel warn

 SSLEngine on
 SSLProtocol all -SSLv2 -SSLv3
 SSLCipherSuite HIGH:3DES:!aNULL:!MD5:!SEED:!IDEA
 SSLCertificateFile /etc/letsencrypt/live/example.com/fullchain.pem
 SSLCertificateKeyFile /etc/letsencrypt/live/example.com/privkey.pem
</VirtualHost>                                  
```

The AliasMatch directive will map the ACME validation path to each domain that Apache serves.

So as long as Apache or Wordpress is configured to respond against that domain name (eg, with the domain mapping entry already applied to a given Wordpress site), it will match all URL paths of the form ".well-known/acme-challenge" to whatever domain is being requested.

When it's time to run certbot, use something like this:
```
certbot certonly --webroot -w /var/www/html --cert-name example.com \  
  -d example.com -d www.example.com \  
  -d example2.com -d www.example2.com \  
  -d example3.com -d www.example3.com --dry-run
```

I spread this across four lines for readability, but this is entered as one line.

* The certonly directive tells certbot not to mess with our web server config.
* --webroot means use the webroot challenge, not DN
* -w tells us the main webroot where it can find the /.well-known directory to write the challenge files.
* --cert-name is the primary cert for the wordpress multisite. Here, it's example.com.
* -d [domain] adds the domain(s) to the certificate.
* --dry-run uses EFF's test servers, rather than slamming their production servers with failed requests causing them to rate-limit you to prevent a denial-of-service attack.
