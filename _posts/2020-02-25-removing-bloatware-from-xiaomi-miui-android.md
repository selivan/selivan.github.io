---
layout: post
title:  "Removing all unnecessary bloatware from Xiaomi MIUI 11/12 (Android 9/10) without root"
tags: [android,xiaomi,miui]
comments_by_utterance: true
---

*TLDR: If you just want the list of bloatware app package names for Xiaomi MIUI - scroll to the end of the artice.*

**UPDATE 2020-05-09**: Added SIM Toolkit description.  
**UPDATE 2020-07-04** Added some apps, thanks to @thecrazyblack.  
**UPDATE 2020-11-23** Updated list of apps, thanks to new comments by @toast254, @swiesmann, @MarcelloDM, @satnited.

Xiaomi phones have impressive parameters for given price, but they come with a lot of unnecessary software. It eats battery and memory, sometimes shows annoying advertisement, and may have security issues. You can not uninstall this pre-installed apps like usual ones, and you can not even disable them from settings like in earlier Android versions.

Here is how to remove or disable unnecessary software without rooting phone. Works for MIUI 11 and 12 (based on Android 9 and 10), should work for other phones for recent Android versions. Thanks to [this](https://stackoverflow.com/a/56968886/890863) very useful but severely under-voted stackoverflow answer.

**NOTE**: I do not guarantee that this instructions won't break your phone, blow it to flaming pieces or cause a sentient machines rebellion against humanity. You were warned.

To manage phone from command-line via USB you need `adb` - Android Debug Bridge, part of Android platform-tools. You can download the recent one for your OS [here](https://developer.android.com/studio/releases/platform-tools).

If you are on Windows, you also need [USB drivers](https://developer.android.com/studio/run/oem-usb.html) for your device. You may also try [Universal Adb Driver](https://github.com/koush/UniversalAdbDriver). If you are using [chocolatey](https://chocolatey.org/) package manager, you can get both like that:

`choco install -y adb universal-adb-drivers`

* ⚙️ Settings - About phone(or My Device). Tap "MIUI version" multiple times. Now Developer Options are unlocked.
* ⚙️ Settings - Additional settings - Developer Options - [✔️] USB debugging.
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
# -k: Keep the data and cache directories around after package removal. 
pm uninstall --user 0 app.package.name
# Install uninstalled system app
pm install --user 0 $(pm dump app.package.name | awk '/path/{ print $2 }')
# Another way to install uninstalled system app
pm install-existing app.package.name
```

More details here: [pm commad manual](https://developer.android.com/studio/command-line/adb#pm).

To be able to install apps back, you need to enable

* ⚙️ Settings - Additional settings - Developer Options - [✔️] Install via USB

On Xiaomi phone to enable this setting you need to sign in into Mi Account. You may just use your Google account to sign into it and then sign-out when you don't need it anymore:

* ⚙️ Settings - Mi Account - sign-out.

Here is a list of Xiaomi and Google apps that I find unnecessary:

**UNSAFE TO DISABLE/UNINSTALL**

| `com.xiaomi.finddevice` | Result: endless boot loop, some time after it will ask to erase the phone and start over. Guess how I learned that? |
| `com.miui.securitycenter` | Result: phone reboots only in recovery mode |
| `com.android.contacts` | Result: you lose the phone icon |
| `com.mi.android.globalminusscreen` | Xiaomi App Vault. Result: if you are logged in with Mi account, device becomes locked, to unlock you should bring it to Xiaomi Services Center. Settings -> Home Screen crashes Settings app. See comment by @satnited. |

---
**Xiaomi**:

| `com.miui.analytics` | Mi Analytics (Spyware?) |
| `com.xiaomi.mipicks` | GetApps - app store like Google Play from Xiaomi. The most annoying one, periodically shows advertisement. |
| `com.miui.msa.global` | MIUI Ad Services - also responsible for showing ads. |
| `com.miui.cloudservice` `com.miui.cloudservice.sysbase` `com.miui.newmidrive` | Mi Cloud |
| `com.miui.cloudbackup` | Mi Cloud Backup |
| `com.miui.backup` | MIUI Backup |
| `com.xiaomi.glgm` | Games |
| `com.xiaomi.payment` `com.mipay.wallet.in` | Mi Credit |
| `com.tencent.soter.soterserver` | Authorize payments in WeChat and other Chinese services, useless if you don't live in China. |
| `cn.wps.xiaomi.abroad.lite` | Mi DocViewer(Powered by WPS Office) |
| `com.miui.videoplayer` | Mi Video |
| `com.miui.player` | Mi Music |
| `com.mi.globalbrowser` | Mi Browser |
| `com.xiaomi.midrop` | Mi ShareMe |
| `com.miui.yellowpage` | Mi YellowPages. Some kind of caller id app. |
| `com.miui.gallery` | MIUI Gallery - if you use another gallery app *WARNING*: @nihalanand697 reports disabling it isn't safe. But I had no problems after uninstalling it. |
| `com.miui.android.fashiongallery` | Wallpaper Carousel |
| `com.miui.bugreport` `com.miui.miservice` | Mi Bug Report - if you not using this feature |
| `com.miui.weather2` | MIUI Weather. I prefer another weather app. |
| `com.miui.hybrid` `com.miui.hybrid.accessory` | Quick apps. |
| `com.miui.global.packageinstaller` | MIUI package installer. Without it Play Store app will be used. It shows ads, but I like that you can manage app permissions before starting it. |
| `com.xiaomi.joyose` | ?? Some junk |

---
**Google**:

| `com.google.android.gms.location.history` | Location History |
| `com.google.android.videos` | Google Movies |
| `com.google.android.music` | Google Music |
| `com.google.android.apps.photos` | Google Photos |
| `com.google.android.youtube` | Youtube - I prefer to use a browser |
| `com.google.android.apps.tachyon` | Google Duo - video calling app |
| `com.google.ar.lens` | Google Lens - identify things on camera |
| `com.google.android.googlequicksearchbox` | Google search box - I prever to use a browser or widget |
| `com.google.android.apps.wellbeing` | Digital wellbeing |
| `com.google.android.apps.googleassistant` | Google Assistant |

---
**Facebook**:

What the @#$%? I just got a fresh phone, didn't install any Facebook apps and I still have a bunch of Facebook services eating my battery and memory.

| `com.facebook.katana` | Facebook mobile app |
| `com.facebook.services` | Facebook Services |
| `com.facebook.system` | Facebook App Installer |
| `com.facebook.appmanager` | Facebook app manager |

---
**Default Android Apps**

| `com.android.browser` | Default Browser - not necessary if you use Firefox or Chrome |
| `com.android.wallpaper.livepicker` | Wallpaper live picker |
| `com.android.dreams.basic` | Screen saver |
| `com.android.dreams.phototable` | Screen saver |
| `com.android.providers.downloads.ui` | Downloads UI. Periodically show notifications about files you downloaded. I find no use for it.  |

---
**Miscelanneous Promoted Apps**

| `com.netflix.partner.activation` | Some Netflix stuff |
| `com.zhiliaoapp.musically` | TikTok |
| `ru.yandex.searchplugin` | Yandex Search |
| `com.yandex.zen` | Yandex Zen |
| `com.ebay.mobile` `com.ebay.carrier` | Ebay Store |
| `ru.ozon.app.android` | Ozon Store |
| `com.alibaba.aliexpresshd` | Aliexpress Store |
| `sg.bigo.live` | Some social media  |
| `ru.auto.ara` | auto.ru app |

And some additional steps to disable Xiaomi ads and collecting data:

* ⚙️ Settings - Passwords & Security - Authorization & revocation. Revoke authorization from msa(MIUI System Ads) application. Not necessary if you already disabled `com.miui.msa.global`.
* ⚙️ Settings - Passwords & Security - Privacy. Disable "User Experience Program" and "Send diagnostic data automatically".
* ⚙️ Settings - Passwords & Security - Privacy - Ad services. Disable "Personalized ad recommendations".

**SIM Toolkit**

Some Russian mobile operators use SIM card built-in application to promote paid services. They show pop-up windows with OK/Cancel buttons. Hit the wrong button - and you are suddenly subscribed to some freaking SMS horoscope with daily fee.

| `com.android.stk` | SIM Toolkit |
| `com.android.stk2` | SIM Toolkit for the second SIM card |

Note, that some mobile operators may use SIM toolkit for useful things, and you will lose that functions. In my experience I have never seen anything useful there.

Another good articles on de-bloating MIUI:

* [technastic.com/xiaomi-bloatware-list-miui/](https://technastic.com/xiaomi-bloatware-list-miui/)
* [devcondition.com/article/removing-unneeded-miui-applications/](https://devcondition.com/article/removing-unneeded-miui-applications/)
