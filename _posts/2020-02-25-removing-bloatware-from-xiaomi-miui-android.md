---
layout: post
title:  "Removing all unnecessary bloatware from Xiaomi MIUI 11 (Android 9) without root"
tags: [android,xiaomi,miui]
---

*TLDR: If you just want the list of bloatware app package names on Xiaomi MIUI - it is in the end of the artice.*

Xiaomi phones have impressive parameters for given price, but they come with a lot of unnecessary software. It eats battery and memory, sometimes shows annoying advertisement, and may have security issues. You can not uninstall this pre-installed apps like usual ones, and you can not even disable them from settings like in earlier Android versions.

Here is how to remove or disable unnecessary software without rooting phone. Works for MIUI 11 (based on Android 9), should work for other phones for recent Android versions. Thanks to [this](https://stackoverflow.com/a/56968886/890863) very useful but severely under-voted stackoverflow answer.

**NOTE**: I do not guarantee that this instructions won't break your phone, blow it to flaming pieces or cause a sentient machines rebellion against humanity. You were warned.

To manage phone from command-line via USB you need `adb` - Android Debug Bridge, part of Android platform-tools. You can download the recent one for your OS [here](https://developer.android.com/studio/releases/platform-tools). If you are on Windows, you also need [USB drivers](https://developer.android.com/studio/run/oem-usb.html) for your device.

* ⚙️ Settings - About phone. Tap "MIUI version" multiple times. Now Developer Options are unlocked.
* ⚙️ Settings - Additional settings - Developer Options. Turn on [x] USB debugging.
* Connect the phone to your computer via USB. Choose "File Transfer" mode instead of default "No data transfer".
* Open console in a directory where you unpacked platform tools.
* `./adb devices`
* Phone will prompt to add your computer's key to allowed, agree to it.
* `./adb shell`   you have a shell on your device.

Now you need app package names, like `com.miui.yellowpage` for Mi Yellow Pages. 

* ⚙️ Settings - Apps - Manage Apps. Tap on application, then tap info(ℹ️) button in the right corner. There you can see "APK name", that's what we need.

There are 2 options: disable app and uninstall app. I prefer disabling them, it's easier to enable them back if you've broken something.

```bash
# Disable app
pm disable-user app.package.name
# Re-enable it
pm enable app.package.name

# Uninstall app
# Sometimes uninstall command may not work without -k option on un-rooted devices
pm uninstall --user 0 app.package.name
# Install uninstalled system app
pm install --user 0 $(pm dump app.package.name | awk '/path/{ print $2 }')
# Another way to install uninstalled system app
pm install-existing app.package.name
```
To be able to install apps back, you need to enable

* ⚙️ Settings - Additional settings - Developer Options - [x] Install via USB

On Xiaomi phone to enable this setting you need to sign in into Mi Account. You may just use your Google account to sign into it and then sign-out when you don't need it anymore:

* ⚙️ Settings - Mi Account - sign-out.

Here is a list of Xiaomi and Google apps that I find unnecessary:

**Xiaomi**:

* GetApps - app store like Google Play from Xiaomi. The most annoying one, periodically shows advertisement.  
`com.xiaomi.mipicks`
* Cloud  
`com.miui.cloudservice`
* Cloud Backup  
`com.miui.cloudbackup`
* Games  
`com.xiaomi.glgm`
* Mi Credit  
`com.xiaomi.payment`
* Mi DocViewer(Powered by WPS Office)  
`cn.wps.xiaomi.abroad.lite`
* Mi ShareMe  
`com.xiaomi.midrop`
* Mi YellowPages  
`com.miui.yellowpage`
* MIUI Gallery - if you use another gallery app  
`com.miui.gallery`
* Wallpaper Carousel  
`com.miui.android.fashiongallery`
* Default Browser - not necessary if you use Firefox or Chrome  
`com.android.browser`

**WARNING**: you should not uninstall or disable "Xiaomi Find Device" `com.xiaomi.finddevice`. On next reboot your phone will enter endless loop, and after some time it will ask to erase device and start over. Guess how I learned that?

**Google**:

* Google Movies  
`com.google.android.videos`
* Google Music  
`com.google.android.music`
* Google Photos  
`com.google.android.apps.photos`
* Youtube - I prefer to use a browser  
`com.google.android.youtube`
* Google Duo  
`com.google.android.apps.tachyon`
* Google Lens  
`com.google.ar.lens`

**Facebook**:

What the @#$%? I just got a fresh phone, didn't install any Facebook apps and I still have a bunch of Facebook services eating my battery and memory.

* Facebook Services  
`com.facebook.services`
* Facebook App Installer  
`com.facebook.system`
* Facebook app manager  
`com.facebook.appmanager`

And some additional steps to disable Xiaomi ads and collecting data:

* ⚙️ Settings - Passwords & Security - Authorization & revocation. Revoke authorization from msa(MIUI System Ads) application.
* ⚙️ Settings - Passwords & Security - Privacy. Disable "User Experience Program" and "Send diagnostic data automatically".
* ⚙️ Settings - Passwords & Security - Privacy - Ad services. Disable "Personalized ad recommendations".
