Title: Boot Images for Arch Linux ARM
Date: 2019-11-21
Slug: alarm-Images
Category: weblog
Tags: tech, archlinux, archlinuxarm, automation, devops, ci
Status: draft

## The Problem

I've been working a bit with Raspberry Pi lately, both the 3B and 3B+ and soon, the Pi 4. Most of this was originally to support a client using the 3B to drive media displays and interactive kiosks. Since they were using Arch Linux ARM, I began using it, too.

Arch Linux ARM (ALArm, for short) provides a compressed tarball of the root filesystem, and you're responsible for preparing the SD card with the partitions and filesystems and unpacking the tarball onto the SD card from another computer before you can boot it. There's no installer in the traditional sense.

This is fine for a one-off, but if you're building a provisioning tool or install script, you probably want a clean image each time. You can simply duplicate your card, either by using an SD Card duplicator or by writing the SD Card to an image file and back. If you don't have a duplicator (most people don't), then writing an image is the solution.

Except...the smallest conventional card you can by these days is 32GB. The 8GB/16GB cards are still available, but are older units and are more expensive (per-GB). Keeping a 32GB image file on disk takes up considerable disk space, while writing the file *back* to SD card can easily take a good four hours to complete.

## Solution

The solution is prepared 8GB image files, built directly from the upstream Arch Linux ARM projects distribution files.

This is easy enough on Linux; but if you're using macOS, working with Arch Linux-based systems is challenging at best:
- Creating BIOS partitions on UEFI/GPT Macs is a pain, and even more so on raw image files.
- No [official] macOS support for Ext4 file systems. Third-party / FUSE options only.
- Arch uses extended attributes in the bsdtar program, which is not the same as BSD tar, apparently, and certainly not GNU tar. I still don't get this one, personally.
- Seting up nullfs (bind mounts in the Linux world) using the loopback device is not well documented on macOS.

The simplest solution I found to create images is to use Vagrant+Virtualbox to spin up an Arch Linux virtual machine (any other distro will work, too), create the image file, mount it via loop dev, and then download/unpack the tarball into the image file via the bind mounts. After than, you can unmount the image file, copy it off somewhere, and destroy the Vagrant box. [This blog post](https://disconnected.systems/blog/raspberry-pi-archlinuxarm-setup/) has the details, as I just modified from his guide.

## Automation

However, I wanted to update these images periodically and hate Hate HATE!!! repetitive, manual tasks. I know I would let this crap get way out of date if I a) wasn't getting paid to pay attention to it and b) if I can get along without doing the extra work. I'm just lazy that way.

Happily, Disconnected Systems [solved this one](https://disconnected.systems/blog/custom-rpi-image-with-github-travis/), too, and after a bit of tinkering, I now have a working source repo that allows me to a) build images locally using Vagrant and b) automatically build and deploy releases directly to Github. using Travis CI.

At the moment, I still need to manually create a release in Github, and then push a commit to trigger a build in Travis. The next improvement might be to have a monitor script that checks the upstream distribution for changes, then automatically creates a new build and release.

Until then, current releases can be found here: https://github.com/andrewboring/alarm-images/releases
And the source repo can be found here: https://github.com/andrewboring/alarm-images
