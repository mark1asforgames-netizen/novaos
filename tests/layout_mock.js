// Runs the NovaOS Plasma layout script against a MOCK of the Plasma scripting API.
// This tests the script's logic only - NOT that real Plasma accepts it.
// usage: node layout_mock.js <layout.js> [degraded]
const fs = require("fs"), vm = require("vm");
const degraded = process.argv[3] === "degraded";
const log = { panels: [], desktops: [] };

class Widget {
  constructor(type) { this.type = type; this.config = {}; this.currentConfigGroup = []; }
  writeConfig(k, v) { this.config[k] = v; }
}
class Panel {
  constructor() { this.widgets = []; log.panels.push(this); }
  addWidget(type) {
    if (degraded && type === "org.kde.plasma.trash") throw new Error("unknown widget");
    const w = new Widget(type); this.widgets.push(w); return w;
  }
  set floating(v) { if (degraded) throw new Error("unsupported"); this._floating = v; }
  get floating() { return this._floating; }
  set lengthMode(v) { if (degraded) throw new Error("unsupported"); this._lengthMode = v; }
  get lengthMode() { return this._lengthMode; }
}
const desk = { currentConfigGroup: [], config: {}, writeConfig(k, v) { this.config[k] = v; } };
log.desktops.push(desk);

const ctx = { Panel, gridUnit: 18, currentActivity: () => "a", desktopsForActivity: () => [desk] };
vm.runInNewContext(fs.readFileSync(process.argv[2], "utf8"), ctx);

const out = {
  panels: log.panels.map(p => ({
    location: p.location, height: p.height, hiding: p.hiding, alignment: p.alignment,
    floating: p._floating, lengthMode: p._lengthMode,
    widgets: p.widgets.map(w => ({ type: w.type, config: w.config })),
  })),
  desktops: log.desktops.map(d => ({ plugin: d.wallpaperPlugin, group: d.currentConfigGroup, config: d.config })),
};
console.log(JSON.stringify(out));
