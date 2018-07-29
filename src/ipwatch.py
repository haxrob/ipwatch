"""
ipwatch.py - version 0.0.1
Released under MIT license
https://github.com/packetflare/ipwatch/

OSX Menu widget that displays the user's current public IP address and  
associated informaton as detected by the service https://ipinfo.io/.

A request to ipinfo.io is triggered if the application detects a change 
in any local interface addresses. A scheduled request is also sent 
every two minutes. On detection in a change of the public address, 
a notification is invoked.

For dependencies -
> pip install pyobjc-framework-Cocoa
> pip install pyObjC
"""

from Foundation import *
from AppKit import *
from PyObjCTools import AppHelper
from Foundation import NSUserNotification
from Foundation import NSUserNotificationCenter
from Foundation import NSUserNotificationDefaultSoundName

from SystemConfiguration import *
from collections import namedtuple

import httplib
import json

# check every 2 minutes. ipinfo.io allows for upto 1000 free requests a day.
PERIODIC_CHECK_INTERVAL = 120

class AppDelegate(NSObject):

    state = 'idle'

    # interval timer
    timerStartFlag = False

    # timer start time
    startTime = NSDate.date()

    def infoMenu(self) :
        """
        Sub-menu "Details" which displays information such as hostname, ASN, etc.
        """
        print "in infoMenu()"
        self.detailMenuItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Details...", None, '')
        detailSubMenu = NSMenu.alloc().init()
        
        # data is dictionary of the JSON response from ipinfo.io/json
        for k, v in self.ipWatchApp.data.items() :
            
            # TODO: order the listing 
            item = "%s: %s" % (k, v)
            detailSubMenu.addItemWithTitle_action_keyEquivalent_(item, None, '')

        self.detailMenuItem.setSubmenu_(detailSubMenu)

        # position 0 specified as info sub-menu deleted and re-added later when updated
        self.menu.insertItem_atIndex_(self.detailMenuItem, 0)

    def applicationDidFinishLaunching_(self, sender):
        """
        Render status bar 
        """
        NSLog("Application did finish launching.")
        NSApp.setActivationPolicy_(NSApplicationActivationPolicyProhibited)
        
        # item visible on status bar "IP x.x.x.x"
        self.statusItem = NSStatusBar.systemStatusBar().statusItemWithLength_(NSVariableStatusItemLength)
        self.statusItem.setTitle_(u"IP")
        self.statusItem.setHighlightMode_(TRUE)
        self.statusItem.setEnabled_(TRUE)

        self.menu = NSMenu.alloc().init()
        self.infoMenu()

        # force probe to be sent to update public IP information
        menuitem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Update now', 'updateNow:', '')
        
        # self.menu.addItem_(menuitem)
        #menuitem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('test', 'test:', '')
        
        self.menu.addItem_(menuitem)

        self.statusItem.setMenu_(self.menu)

        # seperator line
        self.menu.addItem_(NSMenuItem.separatorItem())
        
        # default action is quit
        menuitem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Quit', 'terminate:', '')
        self.menu.addItem_(menuitem)

        # probe periodic check timer
        addedDate = self.startTime.dateByAddingTimeInterval_(30)

        print "now date:" + str(self.startTime)
        print "Added date:" + str(addedDate)
        self.timer = NSTimer.alloc().initWithFireDate_interval_target_selector_userInfo_repeats_(
                                                addedDate, PERIODIC_CHECK_INTERVAL, self, 
                                                'checkTimerCallback:', None, True)

        NSRunLoop.currentRunLoop().addTimer_forMode_(self.timer, NSDefaultRunLoopMode)
        #self.timer.fire()


        # local interface check timer. Currently set to 1/2 a second
        self.ifaceCheckTimer = NSTimer.alloc().initWithFireDate_interval_target_selector_userInfo_repeats_(
                                                    self.startTime, 1/2., self, 
                                                    'ifaceTimerCallback:', None, True)

        NSRunLoop.currentRunLoop().addTimer_forMode_(self.ifaceCheckTimer, NSDefaultRunLoopMode)
        self.ifaceCheckTimer.fire()

    def ifaceTimerCallback_(self, notification) :
        """
        Callback for interface address check timer
        """
        self.ipWatchApp.checkForIfaceChange()

    def test_(self, notification) :
        """ not used 
        """
        self.ipWatchApp.testing()
        return 

    def updateNow_(self, notification):
        """
        callback when user clicks update menu item
        """
        self.ipWatchApp.updateNow()                

    def checkTimerCallback_(self, notification):
        """
        callback for periodic check of the public IP address
        """
        self.ipWatchApp.updateNow()


class IPWatchApp :

    # public IP address in last check
    prevIPAddress = None

    # Keep track of adaptor interface addresses. If changed, will triger a check 
    prevIFaceAddrs = []

    def __init__(self) :
        #self.data = {u'loc': u'33.1000,122.9830', u'city': u'Tokyo', u'country': u'JP', u'region': u'Kanto', u'hostname': u'hn-10-010.level.ne.jp', u'ip': u'192.7.90.130', u'org': u'AS11111 NetVCOm Co.,Ltd.'}
        self.data = {'ip' : ''}
        app = NSApplication.sharedApplication()
        delegate = AppDelegate.alloc().init()

        # delegate has to be able to access members of this class
        delegate.ipWatchApp = self

        # and vice-versa
        self.nsapp = delegate
        app.setDelegate_(delegate)
        return

    def fetchIPDetails(self) :
        """
        Preforms query to https://ipinfo.io/ which returns user's public IP address and other
        details in JSON format
        """
        try :
            conn = httplib.HTTPSConnection("ipinfo.io")
            conn.request("GET", "/json")
            response = conn.getresponse()
            self.data = json.load(response)
        except Exception as e :
            self.data = {'ip' : 'Error'}

        if 'error' in self.data :
            self.data['ip'] = 'Error'

        print self.data

    def sendNotification(self, title, body) :
        """
        Notification pop-up when IP address change detected
        """
        notification = NSUserNotification.alloc().init()
        center = NSUserNotificationCenter.defaultUserNotificationCenter()
        notification.setTitle_(title)
        notification.setInformativeText_(body)
        center.deliverNotification_(notification)

    def updateNow(self) : 
        print "In updateNow() " + self.data['ip']
        self.fetchIPDetails()

        currentIPAddress = self.data['ip']

        # public IP address has changed
        if self.prevIPAddress != currentIPAddress :

            # if prevIPAddress is None, then assume program has just been initialised and
            # user does not want to see a notification
            if self.prevIPAddress is not None :
                textBody = "Was %s\nNow %s" % (self.prevIPAddress, currentIPAddress)
                self.sendNotification("Public IP address changed", textBody)
            
            # update the details menu item
            self.nsapp.menu.removeItem_(self.nsapp.detailMenuItem)
            self.nsapp.infoMenu()

            # update the title on the menu bar
            self.nsapp.statusItem.setTitle_(u"IP: " + currentIPAddress)

        self.prevIPAddress = currentIPAddress   
        return currentIPAddress   

    def checkForIfaceChange(self) :
        """
        Enumerates all interface addresses on the host
        # see: http://kbyanc.blogspot.com/2010/10/python-enumerating-ip-addresses-on.html
        """
        ds = SCDynamicStoreCreate(None, 'GetIPv4Addresses', None, None)
        # Get all keys matching pattern State:/Network/Service/[^/]+/IPv4
        pattern = SCDynamicStoreKeyCreateNetworkServiceEntity(None, kSCDynamicStoreDomainState, kSCCompAnyRegex, kSCEntNetIPv4)
        patterns = CFArrayCreate(None, (pattern, ), 1, kCFTypeArrayCallBacks)
        valueDict = SCDynamicStoreCopyMultiple(ds, None, patterns)

        # Approach to detech a change is to store addresses in a list and calculate the intersection of the prior address
        # list. If number of elements that intersect is differnet to the list size then they are different

        currentIFaceAddrs = []
        for serviceDict in valueDict.values():
            for address in serviceDict[u'Addresses']:
                currentIFaceAddrs.append(address)  

        # use the max length of either list as the length
        if len(set(currentIFaceAddrs).intersection(self.prevIFaceAddrs)) != max(len(self.prevIFaceAddrs), len(currentIFaceAddrs)) :
            self.updateNow()

        self.prevIFaceAddrs = list(currentIFaceAddrs)

if __name__ == "__main__":
    ipWatchApp = IPWatchApp()
    AppHelper.runEventLoop()
