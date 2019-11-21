Title: RFC IP Address Blocks
Date: 2019-09-15
Slug: 9413
Category: weblog
Tags: reference, networking, ip4
Status: draft


IP Address Blocks for Documentation
[RFC 5737](https://tools.ietf.org/html/rfc5737)
192.0.2.0/24  TEST-NET-1
198.51.100.0/24  TEST-NET-2
203.0.11.3.0/24  TEST-NET-3


IP Address Blocks for Private Multisite
[RFC 1918](https://tools.ietf.org/html/rfc1918)
10.0.0.0        -   10.255.255.255  (10/8 prefix)
172.16.0.0      -   172.31.255.255  (172.16/12 prefix)
192.168.0.0     -   192.168.255.255 (192.168/16 prefix)

> We will refer to the first block as "24-bit block", the second as
"20-bit block", and to the third as "16-bit" block. Note that (in
pre-CIDR notation) the first block is nothing but a single class A
network number, while the second block is a set of 16 contiguous
class B network numbers, and third block is a set of 256 contiguous
class C network numbers.

IPv4 Multicast Address Space
224.0.0.0 through 239.255.255.255
