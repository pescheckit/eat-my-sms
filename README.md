# Eat My SMS

A daemon to work with some funky 8-way GSM modem to read SMS messages and send them to a webhook

## Building Debian package

To build this project as a Debian package, run the following commands on a Debian machine:

```sh
apt install debhelper-compat config-package-dev
dpkg-buildpackage -uc -us
```

The `.deb` file will then be created in the parent folder.
To clean the generated files after building the package, run the following command instead:

```sh
dpkg-buildpackage -uc -us --post-clean
```

## Installing

Install and run the package with the following commands:

```sh
dpkg -i eat-my-sms.deb
apt --fix-broken install
```

## Configuration

After installing the package, the [eat-my-sms.conf](eat-my-sms.conf) config file is installed at `/etc/eat-my-sms/eat-my-sms.conf`.
There you can set default configuration values and override them for specific modems.

## Running

To start (and enable) the script for a specific modem, use the `eat-my-sms@<device>.service` systemd unit as the following example:

```sh
systemctl start eat-my-sms@ttyACM0.service
systemctl enable eat-my-sms@ttyACM0.service

systemctl start eat-my-sms@ttyACM1.service
# ...
```

Systemd (after version 209) supports globbing in the template value (as the parameter is called).
Please make sure to add the quotes since your shell might expand the `*` to something else.
And also only use this to restart, stop and disable instances since systemd doesn't know which instances can exist.
This can be done as follows:

```sh
systemctl restart 'eat-my-sms@*.service'
systemctl stop 'eat-my-sms@*.service'
```
