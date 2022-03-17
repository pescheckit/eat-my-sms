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
