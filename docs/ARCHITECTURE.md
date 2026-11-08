# NovaOS – techninė architektūra (1 etapas)

## Sprendimas

**Pakeitimas 2 etape:** pradžioje buvo pasirinktas Ubuntu 24.04. Pereita į **Debian 13 „trixie“**
(stabili nuo 2025-08-09, KDE Plasma 6.3, ~5 m. palaikymas), nes ISO kūrimas per `live-build` yra
standartinis Debian kelias (oficialūs Debian live atvaizdai su Calamares kuriami taip pat), o Ubuntu
sluoksniuoto squashfs remasterio negalėjau pagrįstai patikrinti. Spec. leidžia „kitą stabilią Linux distribuciją“.

| Sluoksnis | Pasirinkimas | Kodėl |
|---|---|---|
| Branduolys, tvarkyklės | Debian 13 (Linux 6.12 LTS) + `firmware-*` (pasirinktinai) | Stabilu, palaikoma |
| Paketų valdymas | apt, atnaujinimai per Discover / apt | Spec. §11 |
| Darbalaukis | KDE Plasma 6.3 | Realus langų tvarkytuvas (KWin), skydeliai, užrakinimas, keli monitoriai |
| Prisijungimas | SDDM + PAM | Tikra OS autentifikacija; tema – 6 etape |
| Paleidimo ekranas | Plymouth | Tema – 6 etape |
| Failų naršyklė | Dolphin | Šiukšlinė, USB, drag&drop, paieška |
| Programų centras | KDE Discover | Patikimos saugyklos |
| Terminalas / redaktorius / skaičiuotuvas / vaizdai | Konsole / Kate / KCalc / Gwenview | Esamos atviro kodo programos |
| Naršyklė | Firefox ESR | |
| Diegimo vedlys | Calamares (`calamares-settings-debian`) | Kalba, laiko juosta, vartotojas, disko pasirinkimas; **NovaOS branding dar nepadarytas** |
| ISO build | Debian `live-build`, paleidžiamas `debian:trixie` konteineryje GitHub Actions | Atkartojama |
| Windows .exe | Tik pasirenkamas Wine, **ne** native | Spec. §2 |

## Ko NovaOS sąmoningai NEDARO
- Nekuria savo branduolio, bootloader ar tvarkyklių.
- Nerašo savo langų tvarkytuvo/kompozitoriaus. Tai būtų daugelio žmogaus-mėnesių darbas,
  o KWin yra patikrintas. Todėl „langai – tikri, ne kortelės“ gaunama iš karto.
- Nekopijuoja Apple ženklų ar ikonų; naudojamas originalus identitetas (`theme/tokens.json`).
- Nevadina savęs „OS nuo nulio“: tai yra Ubuntu pagrindo distribucija su savo darbalaukio patirtimi.

## Kas yra originalus NovaOS darbas
1. **Dizaino sistema**: `theme/tokens.json` – vienas tiesos šaltinis. Iš jo generuojamos KDE
   spalvų schemos. Vėliau: Plasma / SDDM / Plymouth / Calamares temos.
2. **Numatytasis išdėstymas**: viršutinė juosta + dock (Plasma skydeliai).
3. **`novacore`** – Python biblioteka + `novactl` CLI: sistemos info (About), atnaujinimų būsena
   per apt, NovaOS nustatymų saugykla. Bus naudojama Nova Settings puslapiuose.
4. **Nova Settings**: KDE KCM modulių sugrupavimas į spec. §6 kategorijas + NovaOS puslapiai.
5. **ISO build sistema** ir diegimo dokumentacija.

## Etapai ir būsena
| # | Etapas | Būsena |
|---|---|---|
| 1 | Architektūra | ✅ šis dokumentas |
| 2 | Katalogų struktūra | ✅ žr. README.md |
| 3 | Shell: Plasma tema, viršutinė juosta, dock, tapetai | 🟡 parašyta, logika patikrinta su imitacija; **realiame Plasma dar nematyta** |
| 4 | Tikri OS servisai | 🟡 pradėta: sysinfo, updates, config (testuota smėlio dėžėje) |
| 5 | Dizaino sistema | 🟡 pradėta: tokens + spalvų schemos (testuota) |
| 6 | Login / boot | ⏳ |
| 7 | ISO build | 🟡 parašyta (live-build + GitHub Actions); **nė karto nepaleista** |
| 8 | Testai ir dokumentacija | ⏳ |

## Testavimo realybė
Šio etapo kodas patikrintas Python `unittest`. GUI ir ISO dalių negalima patikrinti be
Debian 13 + Plasma + root + VM. Jos bus žymimos „netestuota“, kol nebus realiai paleistos.
