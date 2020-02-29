Title: SuiteCRM LDAP Authentication Using FreeIPA
Date: 2019-09-15
Category: weblog
Tags: technotes, ldap, freeipa, suitecrm

SuiteCRM LDAP Authentication Using FreeIPA.

The biggest problem with SuiteCRM in LDAP configuration is that there is no "test connection" button to validate the configuration is correct before saving it. Your only testing option is to save the configuration, then open a new window (Incognito mode or a different browser entirely) to test the login while you make additional changes.

This can be an extensive trial-and-error process, especially if you lack expertise in x509 directory schemas.  Most of the documentation and online forum questions relate to Active Directory or OpenLDAP, rather than FreeIPA.

Requirements:
SuiteCRM user authenticates using a user ID (uid).
Authorized User is a staff member (member of the Staff group).
Internal LDAP realm is "sys.example.com".

```
Enable LDAP Authentication: checked

- Server: ipa.sys.eriscape.com
- Port Number:
- User DN: cn=users,cn=accounts,dc=sys,dc=example,dc=com
  User Filter:
- Bind Attribute: dn
- Login Attribute: uid

Authentication
- User Name: uid=crm-system,cn=users,cn=accounts,dc=sys,dc=example,dc=com
- Password: *******
```

Get this working first. You must be able to login using a username before mucking with group membership.
The "crm-system" user is a general system account for accessing the FreeIPA directory, and this is expressed as a DN rather than the user@REALM format you might enter for Active Directory. I like to create a separate system user for each service authenticating against LDAP to aid in troubleshooting/log analysis.

There are two general schemas in use, RFC2307 and RFC2307bis, and the biggest difference (to us) is how it identifies group membership. I haven't poked at this extensively, but I typically use memberOf on most systems that support 2307bis. This may not be supported by SuiteCRM, or it may be that other attributes need to be adjusted to support memberOf. [I wrote about this for a different blog](https://unofficialaciguide.com/2019/07/31/ldap-schemas-for-aci-administrators-rfc2307-vs-rfc2307bis/), so I won't detail it here.

To authorize only specific group members, configure the Group Membership section (where "staff" is the name of the group you want to restrict):

```
Group Membership
- Group DN: cn=groups,cn=accounts,dc=sys,dc=example,dc=com
- Group Name: cn=staff
- User attribute: uid
- Group Attribute: member
- With User DN: checked

Auto Create Users: checked
```

The "Auto Create Users" must be checked so that SuiteCRM can create the necessary local database entries in order to apply roles/policies. SuiteCRM does not support policy/role definitions in LDAP.
