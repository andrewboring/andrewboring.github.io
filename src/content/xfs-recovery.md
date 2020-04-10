Title: Recovering Data From XFS
Date: 2020-04-06
Slug: xfs-recovery
Category: weblog
Tags: tech, xfs, data recovery

Monday morning.  
I should stop right there, really. That tells you everything you need to know.

But to continue the narrative, I had to deal with a server whose RAID-1 mirror crapped itself.
It's a legacy server, running some old legacy stuff that hadn't been converted to a more scalable, cloud-like service. I asked the data center techs to hook up a remote IP-KVM so I could get eyes on it, but Lantronix Java + macOS is an exercise in futility and frustration.

The server was inaccessible from console (using crash cart) when I arrived at the data center.
Rebooted, and found that the main RAID-1 mirror (hosting the primary OS, cPanel, and accounts) was marked as a "Foreign" configuration by the Dell PERC card.

Entered system RAID utility. Disk 2 was marked as offline, and configuration was marked "Foreign" instead of "Degraded".

I removed failed Disk 2 drive, replaced with new Disk 2 from another server, but it wasn't similar enough for the PERC card to allow it to be used as replacement to rebuild the mirror. Still marked "Foreign".

I tried re-seating the original Disk 2, and eventually found the "Clear Foreign Configuration" option (not to be confused with the more prominent "Clear Configuration" option, which wipes everything including the other RAID mirrors installed on the server). It started "rebuilding" disk 1. WTF? I don't want to rebuild Disk 1 from failed Disk 2!

Reboot, since there's no "stop" button.

Recreated mirror with just Disk 1, but did not initialize.

Rebooted and it booted up into OS/cPanel, but apparently the files were dated from 2017 and Disk 1 was not being mirrored since then. My assumption is that the failed disk 2 was receiving all the writes from the RAID controller and had the current files.

Anyway, time to recover.

---

High-level steps:

1. Use xfs_repair -n to check without modification, like fsck -n.
2. Try to use xfs_repair to fix.
3. If prompted to mount the partition to replay the log, unmount, and then re-run xfs_repair, try that. But you're probably in this situation because you *can't* mount the filesystem.
4. If prompted to run with -L to delete the log (a destructive, last-resort operation), try to test it on a copy of the metadata first.
    - xfs_metadump [partition] /path/to/file.metadump
    - xfs_mdrestore /path/to/file.metadump /path/to/file.img
    - losetup --show --find /path/to/file.img
    - xfs_repair -L /dev/loop0
    - mount /dev/loop0 /mnt
    - check the damage
    - (note, this is an image of file system layout, but not the actual data)
5. Finally, copy the partition data to an image file using ddrescue, and then try to repair the copy.
    - ddrescue -f -n [partition] /path/to/rescued.img rescue.log
    - ddrescue -d -f -r3 [partition] /path/to/rescued.img rescue.log
    - losetup --show --find /path/to/rescued.img
    - xfs_repair -L /dev/loop0
    - mount /dev/loop0 /mnt
    - check the damage
6. If that doesn't work, you can try xfs_repair -L directly on the affected partition, but not before you pray to your deity of choice.

Since macOS sucks for working with non-Apple partitions/data, I used a Raspberry Pi 3B+ running Arch Linux. I connected the SATA drive to a SATA-to-USB adapter, and later attached a second external USB drive for copying data to.

Plugged in the bad drive first. Registers as /dev/sda.
Take a look at the partitions and try to mount it:

```
[root@alarmpi ~]# fdisk -l /dev/sda
Disk /dev/sda: 149.5 GiB, 160041885696 bytes, 312581808 sectors
Disk model: 00AAJS-60PSA0   
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disklabel type: dos
Disk identifier: 0x00070f16

Device     Boot   Start       End   Sectors  Size Id Type
/dev/sda1  *       2048   1026047   1024000  500M 83 Linux
/dev/sda2       1026048 311427071 310401024  148G 8e Linux LVM

[root@alarmpi ~]# mount /dev/sda2 /mnt
mount: /mnt: unknown filesystem type 'LVM2_member'.
```

Oh, right. LVM volume. Duh.
Let's install LVM tools.

```
[root@alarmpi ~]# pacman -S lvm2
resolving dependencies...
looking for conflicting packages...

Packages (3) libaio-0.3.112-2  thin-provisioning-tools-0.8.5-3  lvm2-2.02.186-5

Total Download Size:   1.51 MiB
Total Installed Size:  7.30 MiB

:: Proceed with installation? [Y/n] y
:: Retrieving packages...
 libaio-0.3.112-2-armv7h                                               6.0 KiB   604 KiB/s 00:00 [########################################################] 100%
 thin-provisioning-tools-0.8.5-3-armv7h                              326.1 KiB  3.18 MiB/s 00:00 [########################################################] 100%
error: failed retrieving file 'lvm2-2.02.186-5-armv7h.pkg.tar.xz' from fl.us.mirror.archlinuxarm.org : The requested URL returned error: 404
warning: failed to retrieve some files
error: failed to commit transaction (failed to retrieve some files)
Errors occurred, no packages were upgraded.
```

Of course. It's Arch. Gotta upgrade the OS first.

```
[root@alarmpi ~]# pacman -Syu
:: Synchronizing package databases...
...
:: Retrieving packages...
```

Let's find the logical volumes on this LVM partition and activate them:

```
[root@alarmpi ~]# lvscan
  WARNING: Failed to connect to lvmetad. Falling back to device scanning.
  inactive          '/dev/centos/swap' [7.88 GiB] inherit
  inactive          '/dev/centos/home' [90.12 GiB] inherit
  inactive          '/dev/centos/root' [50.00 GiB] inherit

[root@alarmpi ~]# vgchange -ay
  WARNING: Failed to connect to lvmetad. Falling back to device scanning.
  3 logical volume(s) in volume group "centos" now active
```

Try to mount the root partition first:

```
[root@alarmpi ~]# mount /dev/centos/root /mnt
[root@alarmpi ~]# ls /mnt
aquota.group  backup  boot  error_log  home   lib    media  opt   quota.group  razor-agent.log	run   scripts  sys  usr
aquota.user   bin     dev   etc        home2  lib64  mnt    proc  quota.user   root		sbin  srv      tmp  var
```

Success!
Home is a different LVM2 volume, mounted onto the /home directory on the original disk.

```
[root@alarmpi ~]# ls /mnt/home
[root@alarmpi ~]#

[root@alarmpi ~]# mount /dev/centos/home /server6/home
mount: /server6/home: mount(2) system call failed: No data available.

[root@alarmpi ~]# ls /mnt/home*
home/  home2/
```

Maybe mount it directly on the Pi, rather than inside the mounted root partition?

```
[root@alarmpi ~]# mkdir /mnt/home3

[root@alarmpi ~]# mount /dev/centos/home /mnt/home3
mount: /mnt/home3: mount(2) system call failed: No data available.
```

Nope.
Well, the databases are more important, since a lot of the /home directories are just web content, and that's stored in version control. Let's check /var/lib/mysql on the root partition.

```
[root@alarmpi ~]# cd /mnt/var/lib/mysql/
[root@alarmpi mysql]# ls
RPM_UPGRADE_HISTORY	 user2_wp		     modsec		 user11_aclstudygroup	     user11_linct_prod	     user11_sddocs       user0_prod
RPM_UPGRADE_MARKER-LAST  user3_production	     mysql		 user11_aclstudygroup_vanilla  user11_magedemo	     user11_staging      user0_redesign
auto.cnf		 user3_test		     mysql.sock		 user11_share	     user11_marketingplaybook  user11_staging_old  user0_staging
user1_brody		 user6_prod		     mysql_upgrade_info  user11_bddocs	     user11_minerva	     user11_surge        user0_test
user1_gasexcrimes	 ib_logfile0		     user11_pack688	 user11_captainplanet	     user11_mcorp	     user11_unboundary
user1_prod		 ib_logfile1		     performance_schema  user11_citysaga		     user11_pbndocs	     user11_wtefdocs
cphulkd			 ibdata1		     	 user11_cmp		     user11_playbacknow	     user5_prod
user3_dev		 server6.example.com.err    user11_edc		     user11_prod		     user0_dev
user3_prod		 server6.example.com.pid  roundcube		 user11_user10	     user11_prod_wordpress     user0_drupal
user0_survey		 leechprotect		     user11_aboutplay	 user11_dev		     user11_scrum		     user0_main
```

Sweet! Poked around a bit to look at file sizes (no 0 bytes fiiles, etc). Things look good.
Let's rsync it off directly to a network storage device...

```
root@alarmpi mysql]# rsync -avz /mnt/var/lib/mysql bkup@192.168.1.15:/mnt/data/bkup/server6/
This rsync lacks old-style --compress due to its external zlib.  Try -zz.
Continuing without compression.

The authenticity of host '192.168.1.15 (192.168.1.15)' can't be established.
ECDSA key fingerprint is SHA256:vFpXHAorzqVTuQKSL2WyP5EtE+MwKPyT1Xij1Hz1fCA.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '192.168.1.15' (ECDSA) to the list of known hosts.
bkup@192.168.1.15's password:
sending incremental file list
created directory /mnt/data/bkup/server6
mysql/
mysql/RPM_UPGRADE_HISTORY
mysql/RPM_UPGRADE_MARKER-LAST
mysql/auto.cnf
...
...
```

Now, let's install the packages to get xfs_repair on Arch.

```
[root@alarmpi ~]# pacman -S xfsprogs
resolving dependencies...
looking for conflicting packages...
```

Let's try to mount it again.

```
[root@alarmpi ~]# mount /dev/centos/home /mnt/home
mount: /mnt/home: mount(2) system call failed: No data available.
```

And run xfs_repair -n to see what would happen (edited for brevity).

```
[root@alarmpi ~]# xfs_repair -n /dev/centos/home
Phase 1 - find and verify superblock...
Phase 2 - using internal log
        - zero log...
ALERT: The filesystem has valuable metadata changes in a log which is being
ignored because the -n option was used.  Expect spurious inconsistencies
which may be resolved by first mounting the filesystem to replay the log.
        - scan filesystem freespace and inode maps...
sb_fdblocks 1723017, counted 1731714
        - found root inode chunk
Phase 3 - for each AG...
        - scan (but don't clear) agi unlinked lists...
        - process known inodes and perform inode discovery...
        - agno = 0
xfs_repair: read failed: No data available
bad magic number 0x6d65 on inode 5840900
bad version number 0x6f on inode 5840900
bad next_unlinked 0x2f5a656e on inode 5840900
bad magic number 0x2f68 on inode 5840906, would reset magic number
bad version number 0x65 on inode 5840906, would reset version number
bad next_unlinked 0x6172792f on inode 5840906, would reset next_unlinked
bad inode format in inode 5840927
would have cleared inode 5840927
        - agno = 1
        - agno = 2
        - agno = 3
        - process newly discovered inodes...
Phase 4 - check for duplicate blocks...
        - setting up duplicate extent list...
        - check for inodes claiming duplicate blocks...
        - agno = 0


Phase 7 - verify link counts...
xfs_repair: read failed: No data available
xfs_imap_to_bp: xfs_trans_read_buf() returned error -61.
couldn't map inode 5840917, err = 61, can't compare link counts
xfs_repair: read failed: No data available
xfs_imap_to_bp: xfs_trans_read_buf() returned error -61.
couldn't map inode 5840925, err = 61, can't compare link counts
No modify flag set, skipping filesystem flush and exiting.
```

Well, there were some I/O errors in my output, so I'm not holding my breath for the repair:

```
[root@alarmpi ~]# xfs_repair /dev/centos/home
Phase 1 - find and verify superblock...
Phase 2 - using internal log
        - zero log...
ERROR: The filesystem has valuable metadata changes in a log which needs to
be replayed.  Mount the filesystem to replay the log, and unmount it before
re-running xfs_repair.  If you are unable to mount the filesystem, then use
the -L option to destroy the log and attempt a repair.
Note that destroying the log may cause corruption -- please attempt a mount
of the filesystem before doing this.

[root@alarmpi ~]# mount -t xfs /dev/centos/home /mnt/home
mount: /mnt/home: mount(2) system call failed: No data available.
```

Yeah. Not so great. I already know I can't mount the partition to replay the log, and the -L switch is a destructive operation.

Let's unmount the root filesystem for a moment and attach a second, external USB drive to copy home data off to. We'll put it onto '/mnt' instead.

```
[ 4451.182458] sd 1:0:0:0: [sdb] Attached SCSI disk
[root@alarmpi ~]# umount /mnt
[root@alarmpi ~]# mount /dev/sdb1 /mnt
```

First, we'll dump the metadata and restore it to a disk image on the USB drive.

```
[root@alarmpi ~]# xfs_metadump /dev/centos/home /mnt/server6-home.metadump
xfs_metadump: read failed: Input/output error
xfs_metadump: cannot read inode block 0/365056
xfs_metadump: Warning: log recovery of an obfuscated metadata image can leak unobfuscated metadata and/or cause image corruption.  If possible, please mount the filesystem to clean the log, or disable obfuscation.
cache_purge: shake on cache 0xfe5320 left 1 nodes!?
cache_purge: shake on cache 0xfe5320 left 1 nodes!?
cache_zero_check: refcount is 1, not zero (node=0x17820c8)

[root@alarmpi ~]# ls -l /mnt/server6-home.metadump  
-rwxr-xr-x 1 root root 844619776 Apr  6 18:48 /mnt/server6-home.metadump
[root@alarmpi ~]# xfs_mdrestore /mnt/server6-home.metadump /mnt/server6-home.img
xfs_mdrestore: cannot set filesystem image size: File too large
```

Oh yeah, the USB drive is FAT32. Can't handle large image files (4GB is the limit).
Wipe it and format it as ext4.

```
[root@alarmpi ~]# umount /mnt

[root@alarmpi ~]# mkfs.ext4 /dev/sdb1
mke2fs 1.45.6 (20-Mar-2020)
/dev/sdb1 contains a vfat file system labelled 'UNTITLED'
Proceed anyway? (y,N) y
Creating filesystem with 61049645 4k blocks and 15269888 inodes
Filesystem UUID: 50818e1c-e8a9-42a9-a126-405f9d5fa8a0
Superblock backups stored on blocks:
	32768, 98304, 163840, 229376, 294912, 819200, 884736, 1605632, 2654208,
	4096000, 7962624, 11239424, 20480000, 23887872

Allocating group tables: done                            
Writing inode tables: done                            
Creating journal (262144 blocks): done
Writing superblocks and filesystem accounting information: done     

[root@alarmpi ~]# mount /dev/sdb1 /mnt
```

Now, let's try this again.

```
[root@alarmpi ~]# xfs_metadump /dev/centos/home /mnt/server6-home.metadata
xfs_metadump: read failed: Input/output error
xfs_metadump: cannot read inode block 0/365056
xfs_metadump: Warning: log recovery of an obfuscated metadata image can leak unobfuscated metadata and/or cause image corruption.  If possible, please mount the filesystem to clean the log, or disable obfuscation.
cache_purge: shake on cache 0x1cb6320 left 1 nodes!?
cache_purge: shake on cache 0x1cb6320 left 1 nodes!?
cache_zero_check: refcount is 1, not zero (node=0x24520c8)
```

That `read failed: Input/Output` error doesn't sound good, but let's try to restore the metadata to an image file anyway.

```
[root@alarmpi ~]# xfs_mdrestore /mnt/server6-home.metadata /mnt/server6-home.img
[root@alarmpi ~]# xfs_repair /mnt/server6-home.img
Cannot get host filesystem geometry.
Repair may fail if there is a sector size mismatch between
the image and the host filesystem.
Phase 1 - find and verify superblock...
Cannot get host filesystem geometry.
Repair may fail if there is a sector size mismatch between
the image and the host filesystem.
Phase 2 - using internal log
        - zero log...
ERROR: The filesystem has valuable metadata changes in a log which needs to
be replayed.  Mount the filesystem to replay the log, and unmount it before
re-running xfs_repair.  If you are unable to mount the filesystem, then use
the -L option to destroy the log and attempt a repair.
Note that destroying the log may cause corruption -- please attempt a mount
of the filesystem before doing this.
```

Actually, we shouldn't really try to do this directly on an image file. Better to do this on a loopback device.

```
[root@alarmpi ~]# ls /mnt
server6-home.img  server6-home.metadata  lost+found

[root@alarmpi ~]# losetup --show --find /mnt/server6-home.img
/dev/loop0
```

```
[root@alarmpi ~]# xfs_repair -L /dev/loop0
Cannot get host filesystem geometry.
Repair may fail if there is a sector size mismatch between
the image and the host filesystem.
Phase 1 - find and verify superblock...

[snipped]

Phase 7 - verify and correct link counts...
Note - quota info will be regenerated on next quota mount.
done

[root@alarmpi ~]# mkdir /loopy
[root@alarmpi ~]# mount /dev/loop0 /loopy
[root@alarmpi ~]# ls /loopy
''$'\003''kovu'		      'Gb0'$'\016''n'$'\021''k'$'\033'	      'bcCa-D'$'\005\023''C'$'\032''m'	'ryN'$'\004''xVX'$'\024'
''$'\a''hat5'		      'GpzR_Ksp'$'\001\264''J0E'	      'h'$'\t''rro\'			 user11
''$'\016''cpal'		      'Hwp-hBh'$'\b''?;% '		      'j'$'\003''pajK'			'y7jG8CU4bonN2aujzfJamyN3xY'$'\a\v\034''cs'
'-Xqcr'$'\016''2o'$'\005''k'  'N6'$'\001\343''vdA'		      'mF88U1Y-'$'\016\033''Hs,'	'yv8UsY'$'\002\036''#R3'
'76q67pR'$'\002''>]YT'	      'UROC0Bh9c'$'\001''B'$'\027'':'$'\177'  'n'$'\001''tesb'
'8n-B'$'\001''CItv'	      'WP4c'$'\016''~Ia'$'\037'		      'qsw77'$'\016''D7x@'
```

This is just a copy of the metadata, but doesn't look so good. I expected to at least see file names.
Let's try to copy the partition itself and work from that copy. That way, we can use destructive operations and we can ease up on slamming a failing disk with all this activity.

```
[root@alarmpi /]# dd if=/dev/centos/home of=/mnt/server6-home-real.img bs=128k
dd: error reading '/dev/centos/home': Input/output error
11408+0 records in
11408+0 records out
1495269376 bytes (1.5 GB, 1.4 GiB) copied, 78.6088 s, 19.0 MB/s

[root@alarmpi /]# ls mnt
server6-home-real.img  server6-home.img  server6-home.metadata  lost+found

```

Nope. I/O errors. Let's try ddrescue.

We need to make 2 passes: one pass to read just the good blocks (those without read errors), and a second pass to try to read the bad the blocks three times before giving up:

```
[root@alarmpi /]# ddrescue -f -n /dev/centos/home /mnt/server6-home-rescue.img rescue.log
GNU ddrescue 1.25
Press Ctrl-C to interrupt
     ipos:    1495 MB, non-trimmed:        0 B,  current rate:   30720 B/s
     opos:    1495 MB, non-scraped:     3072 B,  average rate:  17486 kB/s
non-tried:        0 B,  bad-sector:     1024 B,    error rate:     256 B/s
  rescued:   96770 MB,   bad areas:        2,        run time:  1h 32m 14s
pct rescued:   99.99%, read errors:        3,  remaining time:          1s
                              time since last successful read:          0s
Finished         

[root@alarmpi /]# ddrescue -d -f -r3 /dev/centos/home /mnt/server6-home-rescue.img rescue.log
GNU ddrescue 1.25
Press Ctrl-C to interrupt
Initial status (read from mapfile)
rescued: 96770 MB, tried: 4096 B, bad-sector: 1024 B, bad areas: 2

Current status
     ipos:    1495 MB, non-trimmed:        0 B,  current rate:       0 B/s
     opos:    1495 MB, non-scraped:        0 B,  average rate:     398 B/s
non-tried:        0 B,  bad-sector:      512 B,    error rate:     170 B/s
  rescued:   96770 MB,   bad areas:        1,        run time:          9s
pct rescued:   99.99%, read errors:        4,  remaining time:         n/a
                              time since last successful read:          3s
Finished  
```

Now, let's try to grab the metadata from this copied partition image.
Mount the image, and then dump/restore the metadata to yet *another* image.



```
[root@alarmpi /]# losetup --find --show /mnt/server6-home-rescue.img
/dev/loop1


[root@alarmpi /]# xfs_metadump /dev/loop1 /mnt/server6-rescued-img.metadump
xfs_metadump: Warning: log recovery of an obfuscated metadata image can leak unobfuscated metadata and/or cause image corruption.  If possible, please mount the filesystem to clean the log, or disable obfuscation.

[root@alarmpi /]# xfs_mdrestore /mnt/server6-rescued-img.metadump /mnt/server6-rescued-metadata.img

[root@alarmpi /]# xfs_repair /mnt/server6-rescued-metadata.img
Cannot get host filesystem geometry.
Repair may fail if there is a sector size mismatch between
the image and the host filesystem.
Phase 1 - find and verify superblock...
Cannot get host filesystem geometry.
Repair may fail if there is a sector size mismatch between
the image and the host filesystem.
Phase 2 - using internal log
        - zero log...
ERROR: The filesystem has valuable metadata changes in a log which needs to
be replayed.  Mount the filesystem to replay the log, and unmount it before
re-running xfs_repair.  If you are unable to mount the filesystem, then use
the -L option to destroy the log and attempt a repair.
Note that destroying the log may cause corruption -- please attempt a mount
of the filesystem before doing this.

[root@alarmpi /]# losetup --show --find /mnt/server6-rescued-metadata.img
/dev/loop2


[root@alarmpi /]# xfs_repair /dev/loop2
Phase 1 - find and verify superblock...
Phase 2 - using internal log
        - zero log...
ERROR: The filesystem has valuable metadata changes in a log which needs to
be replayed.  Mount the filesystem to replay the log, and unmount it before
re-running xfs_repair.  If you are unable to mount the filesystem, then use
the -L option to destroy the log and attempt a repair.
Note that destroying the log may cause corruption -- please attempt a mount
of the filesystem before doing this.

[root@alarmpi /]# mkdir /mnt2
[root@alarmpi /]# mount /dev/loop2 /mnt2
mount: /mnt2: mount(2) system call failed: Structure needs cleaning.

```

Okay. We expected that.  
Let's do the last-resort, fully destructive repair operation. Remember, we're still operating on the on the *metadata* image from the *copied* partition image.

```
[root@alarmpi /]# xfs_repair -L /dev/loop2
Phase 1 - find and verify superblock...
Phase 2 - using internal log
        - zero log...
ALERT: The filesystem has valuable metadata changes in a log which is being
destroyed because the -L option was used.
        - scan filesystem freespace and inode maps...
sb_fdblocks 1723017, counted 1731714
        - found root inode chunk
Phase 3 - for each AG...
        - scan and clear agi unlinked lists...
        - process known inodes and perform inode discovery...
        - agno = 0
Metadata corruption detected at 0x51b650, xfs_inode block 0x2c9000/0x2000
bad magic number 0x0 on inode 5840900
bad version number 0x0 on inode 5840900
bad next_unlinked 0x0 on inode 5840900
bad magic number 0x0 on inode 5840901
bad version number 0x0 on inode 5840901
bad next_unlinked 0x0 on inode 5840901
bad magic number 0x0 on inode 5840900, resetting magic number
bad version number 0x0 on inode 5840900, resetting version number
bad next_unlinked 0x0 on inode 5840900, resetting next_unlinked
imap claims a free inode 5840900 is in use, correcting imap and clearing inode
cleared inode 5840900
bad magic number 0x0 on inode 5840901, resetting magic number
bad version number 0x0 on inode 5840901, resetting version number
bad next_unlinked 0x0 on inode 5840901, resetting next_unlinked
imap claims a free inode 5840901 is in use, correcting imap and clearing inode
cleared inode 5840901
        - agno = 1
Metadata corruption detected at 0x50cd48, xfs_dir3_block block 0x2d24dd0/0x1000
        - agno = 2
        - agno = 3
        - process newly discovered inodes...
Phase 4 - check for duplicate blocks...
        - setting up duplicate extent list...
        - check for inodes claiming duplicate blocks...
        - agno = 0
entry "yW5knH-uj-UcvFmnM5CXvwZHrx?=0" at block 1238 offset 2992 in directory inode 13508451 references free inode 5840901
	clearing inode number in entry at offset 2992...
entry "Ja_rLm8K4VNoEIN8CR3ujtnulyRarKI1kIgwud6m	15t" at block 0 offset 344 in directory inode 66696251 references free inode 5840900
	clearing inode number in entry at offset 344...
        - agno = 1
Metadata corruption detected at 0x50cd48, xfs_dir3_block block 0x2d24dd0/0x1000
        - agno = 2
        - agno = 3
Phase 5 - rebuild AG headers and trees...
        - reset superblock...
Phase 6 - check inode connectivity...
        - resetting contents of realtime bitmap and summary inodes
        - traversing filesystem ...
rebuilding directory inode 13508451
bad hash table for directory inode 66696251 (no data entry): rebuilding
rebuilding directory inode 66696251
Metadata corruption detected at 0x50cd48, xfs_dir3_block block 0x2d24dd0/0x1000
bad hash table for directory inode 134370432 (hash value mismatch): rebuilding
rebuilding directory inode 134370432
...
```

Survey says....*hoooonk*

```
[root@alarmpi /]# mount /dev/loop2 /mnt2
[root@alarmpi /]# ls /mnt2
''$'\003''kovu'		      'Gb0'$'\016''n'$'\021''k'$'\033'	      'bcCa-D'$'\005\023''C'$'\032''m'	'ryN'$'\004''xVX'$'\024'
''$'\a''hat5'		      'GpzR_Ksp'$'\001\264''J0E'	      'h'$'\t''rro\'			 user11
''$'\016''cpal'		      'Hwp-hBh'$'\b''?;% '		      'j'$'\003''pajK'			'y7jG8CU4bonN2aujzfJamyN3xY'$'\a\v\034''cs'
'-Xqcr'$'\016''2o'$'\005''k'  'N6'$'\001\343''vdA'		      'mF88U1Y-'$'\016\033''Hs,'	'yv8UsY'$'\002\036''#R3'
'76q67pR'$'\002''>]YT'	      'UROC0Bh9c'$'\001''B'$'\027'':'$'\177'  'n'$'\001''tesb'
'8n-B'$'\001''CItv'	      'WP4c'$'\016''~Ia'$'\037'		      'qsw77'$'\016''D7x@'
```


Fine. Let's just try the operation directly on the copied partition image created from ddrescue.

```
[alarm@alarmpi /]# losetup --find --show /mnt/server6-home-rescue.img
/dev/loop3

[alarm@alarmpi /]$ sudo xfs_repair /dev/loop3
Phase 1 - find and verify superblock...
Phase 2 - using internal log
        - zero log...
ERROR: The filesystem has valuable metadata changes in a log which needs to
be replayed.  Mount the filesystem to replay the log, and unmount it before
re-running xfs_repair.  If you are unable to mount the filesystem, then use
the -L option to destroy the log and attempt a repair.
Note that destroying the log may cause corruption -- please attempt a mount
of the filesystem before doing this.

[alarm@alarmpi /]# mkdir /mnt3  
[root@alarmpi ~]# mount /dev/loop3 /mnt3
mount: /mnt3: mount(2) system call failed: Structure needs cleaning.
```

Okay. As expected.  
Let's go straight to -L.

```
[root@alarmpi ~]# xfs_repair -L /dev/loop3
Phase 1 - find and verify superblock...
Phase 2 - using internal log
        - zero log...
ALERT: The filesystem has valuable metadata changes in a log which is being
destroyed because the -L option was used.
        - scan filesystem freespace and inode maps...
sb_fdblocks 1723017, counted 1731714
        - found root inode chunk
Phase 3 - for each AG...
        - scan and clear agi unlinked lists...
        - process known inodes and perform inode discovery...
        - agno = 0
Metadata corruption detected at 0x553650, xfs_inode block 0x2c9000/0x2000
bad magic number 0x0 on inode 5840900
bad version number 0x0 on inode 5840900
bad next_unlinked 0x0 on inode 5840900
bad magic number 0x0 on inode 5840901
bad version number 0x0 on inode 5840901
bad next_unlinked 0x0 on inode 5840901
bad magic number 0x0 on inode 5840900, resetting magic number
bad version number 0x0 on inode 5840900, resetting version number
bad next_unlinked 0x0 on inode 5840900, resetting next_unlinked
imap claims a free inode 5840900 is in use, correcting imap and clearing inode
cleared inode 5840900
bad magic number 0x0 on inode 5840901, resetting magic number
bad version number 0x0 on inode 5840901, resetting version number
bad next_unlinked 0x0 on inode 5840901, resetting next_unlinked
imap claims a free inode 5840901 is in use, correcting imap and clearing inode
cleared inode 5840901
        - agno = 1
        - agno = 2
        - agno = 3
        - process newly discovered inodes...
Phase 4 - check for duplicate blocks...
        - setting up duplicate extent list...
        - check for inodes claiming duplicate blocks...
        - agno = 0
entry "sess_57usp4fkeg1icc0pbkmju3nn34" at block 1238 offset 2992 in directory inode 13508451 references free inode 5840901
	clearing inode number in entry at offset 2992...
entry "zend_cache---internal-metadatas---artist_skin" at block 0 offset 344 in directory inode 66696251 references free inode 5840900
	clearing inode number in entry at offset 344...
        - agno = 1
        - agno = 2
        - agno = 3
Phase 5 - rebuild AG headers and trees...
        - reset superblock...
Phase 6 - check inode connectivity...
        - resetting contents of realtime bitmap and summary inodes
        - traversing filesystem ...
rebuilding directory inode 13508451
bad hash table for directory inode 66696251 (no data entry): rebuilding
rebuilding directory inode 66696251
        - traversal finished ...
        - moving disconnected inodes to lost+found ...
Phase 7 - verify and correct link counts...
Note - quota info will be regenerated on next quota mount.
done
```

Let's give it a try...

```
[root@alarmpi ~]# mount /dev/loop3 /mnt3

[root@alarmpi ~]# ls /mnt3
0_README_BEFORE_DELETING_VIRTFS  aquota.user	user1    user2	 user3  user4  quota.user  user5	 user0 cPanelInstall	cpanelsolr  user10  user6  user7  user9  quota.group 	 virtfs
```

WTF? Success?
I honestly did not expect that.  

Some of the files themselves may be corrupted (probably from being in an inconsistent state when all this went down), but after poking around a bit, it appears that this does indeed contain sufficient data to make the recovery efforts worthwhile.

Copy the homedirs out of the mounted image and onto the external USB drive to upload later.

```
[root@alarmpi ~]# cd /mnt3
[root@alarmpi mnt3]# for i in user1 user10 user3 user6 user7 user9 user4 user5 user0 user2; do echo $i; tar -cf /mnt/$i.tar $i; echo "$i done!"; done
```


References:
https://serverfault.com/questions/777299/proper-way-to-deal-with-corrupt-xfs-filesystems
https://wiki.archlinux.org/index.php/Disk_cloning#Using_ddrescue
https://wiki.archlinux.org/index.php/XFS#Repair_XFS_Filesystem
https://jlk.fjfi.cvut.cz/arch/manpages/man/xfs_repair.8

Happily, did not have to do this one:
https://serverfault.com/a/834853
