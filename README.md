# NovaOS

*Simple outside. Powerful inside.*

NovaOS yra planuojama diegiama Linux distribucija: **Debian 13 + KDE Plasma 6** su originaliu
NovaOS dizainu ir savais įrankiais. Tai **nėra** nauja OS nuo nulio ir nėra žaidimas ar UI demonstracija.
Dabartinė versija: **0.1.0-dev. ISO build sistema parašyta, bet dar NĖ KARTO nepaleista, todėl ISO dar nėra.**
Kaip gauti ISO ir išbandyti: `docs/BUILD_ISO.md`, `docs/VIRTUALBOX.md`. Žr. `docs/STATUS.md`.

## Katalogų struktūra
Rodomi tik **egzistuojantys** failai. Planuojami pažymėti (planned).

```
novaos/
├── README.md
├── Makefile                      make gen | make test
├── docs/
│   ├── ARCHITECTURE.md           pasirinkta technologinė bazė ir kodėl
│   ├── STATUS.md                 tikra funkcijų būsena (veikia / netestuota / nėra)
│   ├── REQUIREMENTS.md           aparatūros suderinamumo reikalavimai
│   ├── BUILD_ISO.md              kaip gauti ISO per GitHub (Windows naudotojui)
│   └── VIRTUALBOX.md             kaip išbandyti VirtualBox
├── theme/
│   ├── tokens.json               dizaino žetonai – vienas tiesos šaltinis
│   └── color-schemes/            GENERUOJAMA: NovaDark.colors, NovaLight.colors
├── tools/
│   └── gen_colorschemes.py       tokens.json -> KDE spalvų schemos (+ WCAG kontrastas)
├── src/novacore/                 realių sistemos servisų sluoksnis (Python, tik stdlib)
│   ├── sysinfo.py                /etc, /proc, /sys: OS, CPU, RAM, diskas, baterija
│   ├── config.py                 ~/.config/novaos/settings.json (atominis įrašas, validacija)
│   ├── updates.py                apt atnaujinimų būsena (be root); diegimo komandos tik su pkexec
│   └── cli.py                    `novactl about | updates | config`
├── tests/                        52 testai (įsk. išdėstymo skripto logiką su imituota Plasma API)
│
├── iso/                          live-build konfigūracija (3 + 7 etapai)
│   ├── build.sh                  surenka ISO (root, Debian 13)
│   └── config/                   paketų sąrašas, hook'ai, includes.chroot (Plasma LnF, tapetai, skel)
├── .github/workflows/build-iso.yml  debesies surinkimas + Release
├── VERSION
├── settings-app/  (planned, 4–5 etapas) Nova Settings
├── sddm/ plymouth/ (planned, 6 etapas) prisijungimo ir paleidimo temos
```

## Paleidimas (šiandien)
Reikia Python ≥ 3.10, nieko daugiau.
```bash
make test                          # 52 testai
cd src && python3 -m novacore about
cd src && python3 -m novacore updates
cd src && python3 -m novacore config set theme dark
make gen                           # perkuria spalvų schemas iš tokens.json
```
