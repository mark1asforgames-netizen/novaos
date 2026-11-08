// NovaOS default desktop layout: top bar + floating dock + NovaOS wallpaper.
//
// Written against the Plasma desktop scripting API. Properties that may not exist in every
// Plasma version are set through trySet() so that a missing property can never abort the
// whole layout (an aborted layout script would leave the user with an empty desktop).

function trySet(obj, name, value) {
    try { obj[name] = value; } catch (e) { /* unsupported in this Plasma version */ }
}

var unit = (typeof gridUnit !== "undefined") ? gridUnit : 18;

// ---- Top bar: launcher | app menu | ---- clock ---- | system tray ----
var top = new Panel;
top.location = "top";
top.height = Math.round(unit * 1.6);
trySet(top, "floating", false);
top.addWidget("org.kde.plasma.kickoff");        // Nova Launcher (search, favourites, recents, power)
top.addWidget("org.kde.plasma.appmenu");        // active application's menu
top.addWidget("org.kde.plasma.panelspacer");
top.addWidget("org.kde.plasma.digitalclock");   // real system date/time
top.addWidget("org.kde.plasma.panelspacer");
top.addWidget("org.kde.plasma.systemtray");     // network, sound, battery, bluetooth, notifications

// ---- Dock: floating, centred, icon-only task manager ----
var dock = new Panel;
dock.location = "bottom";
dock.height = Math.round(unit * 3);
dock.alignment = "center";
dock.hiding = "none";                            // user can switch to auto-hide in panel edit mode
trySet(dock, "floating", true);
trySet(dock, "lengthMode", "fit");

var tasks = dock.addWidget("org.kde.plasma.icontasks");
tasks.currentConfigGroup = ["General"];
tasks.writeConfig("launchers", [
    "applications:org.kde.dolphin.desktop",
    "applications:firefox-esr.desktop",
    "applications:org.kde.konsole.desktop",
    "applications:org.kde.kate.desktop",
    "applications:org.kde.kcalc.desktop",
    "applications:org.kde.discover.desktop",
    "applications:systemsettings.desktop"
].join(","));
try { dock.addWidget("org.kde.plasma.trash"); } catch (e) { /* optional */ }

// ---- Wallpaper on every desktop ----
var desktopsArray = desktopsForActivity(currentActivity());
for (var i = 0; i < desktopsArray.length; i++) {
    var d = desktopsArray[i];
    d.wallpaperPlugin = "org.kde.image";
    d.currentConfigGroup = ["Wallpaper", "org.kde.image", "General"];
    d.writeConfig("Image", "file:///usr/share/wallpapers/NovaOS");
}
