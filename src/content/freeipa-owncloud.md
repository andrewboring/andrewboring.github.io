Title: OwnCloud LDAP Authentication Using FreeIPA
Date: 2019-09-15
Category: weblog
Status: draft
Tags: technotes, ldap, freeipa, owncloud

The ownCloud software is a bit challenging to configure for LDAP-based authentication and authorization. The configuration screen uses Javascript to save the settings without clicking a "save" button, and some settings don't quite go away just because you unchecked the parent box. If you configure a setting with multiple attributes and then want to disable that setting, it's best to disable any attributes (if possible) when disabling the setting itself. I don't have a ready example of this right now, unfortunately.

In this scenario, I want to require an email address for the username, and restrict it to the members of the group "owncloud".

The object classes selectors may not be absolutely necessary, but they may reduce search time if you have a large directory with many objects.


```
Server:
- Server: ipa.sys.example.com
- Bind DN: uid=owncloud-system,cn=users,cn=accounts,dc=sys,dc=example,dc=com
- Password:
- Base DN: dc=sys,dc=example,dc=com

Users:
- Only these object classes: posixaccount

Login Attributes:
- LDAP / AD Email Address

Groups:
- Only these object classes: posixgroup
- Only from these groups: owncloud
```
