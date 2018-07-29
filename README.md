# IPWatch

A Mac OSX menu widget that displays your current public IP address and sends a notification alert if the address changes.
This could be useful to those using a VPN and would like to see the current publicly exposed IP address at all times.
The IP address and related information is fetched from the fantastic service https://ipinfo.io.

Two methods for detection is so far supported -
1) Monitor all local adaptors for any changes in the local address.
2) Periodic requests to the external ipinfo.io service. This is set to trigger every two minutes to keep the number of requests under 1000 per 24 hour period (free quota for ipinfo.io)

![Image](https://github.com/packetflare/ipwatch/blob/870b9e9eabe76cae25ca95a6ee76c01325cc4974/images/one.png)
![Image](https://github.com/packetflare/ipwatch/blob/870b9e9eabe76cae25ca95a6ee76c01325cc4974/images/two.png)

A pre-compiled version is found in /bin/ipwatch.app.zip which was bult on Mac OSX 10.13.6.

To run or build from source PyObjC is required. -
```
$ pip install pyobjc-framework-Cocoa
$ pip install pyObjC
```
To run -
```
$ python src/ipwatch.py
```

To build stand alone execuable package -
```
$ python src/build.py py2app
```
## Ideas for improvements
* Self hosted server as an alternative to using https://ipinfo.io
* On detection of a change, have the option to disable traffic to prevent data leaks (for VPN users)
* Various leak checks built in (i.e DNS leaks etc)

## License
MIT
