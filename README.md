# IPWatch

A Mac OSX menu widget that displays your current public IP address and sends a notification alert if the address changes.
This could be useful to those using VPNs for example. The IP adress and related information is fetched from the fantastic service, https://ipinfo.io.

![Image](images/1.png)
![Image](images/2.png)

Install dependencies -
```
$ pip install pyobjc-framework-Cocoa
$ pip install pyObjC

```
To run -
```
$ python src/ipwatch.py
```

To build stand alone execuable -
```
$ python src/build.py py2app
```

A pre-compiled version is found in /bin/ipwatch.app.zip which was bult on mac osx 10.13.6