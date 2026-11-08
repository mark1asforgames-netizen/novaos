# NovaOS funkcijų būsena (0.1.0-dev)

Legenda: ✅ veikia ir patikrinta · 🧪 kodas yra, patikrintas tik fixtūromis/vienetiniais testais ·
📝 tik dizaino failas · ❌ nėra

| Sritis | Būsena | Pastaba |
|---|---|---|
| Linux pagrindas pasirinktas | ✅ | Ubuntu 24.04 + KDE Plasma (ARCHITECTURE.md) |
| Sistemos info (About) | ✅ | Paleista realioje sistemoje; baterija – tik fixtūra |
| Nustatymų saugykla | ✅ | Išlieka tarp paleidimų, atominis įrašas, atmeta blogas reikšmes |
| Atnaujinimų patikra (apt) | 🧪 | Veikia tikrame apt tik „0 atnaujinimų“ atvejui; `Inst` eilučių parseris patikrintas tik pagal rankiniu būdu parašytą formatą |
| Atnaujinimų diegimas | 🧪 | Tik sudaro `pkexec apt-get ...` komandą; UI patvirtinimo dar nėra |
| Spalvų schemos (šviesi/tamsi) | 🧪 | Sugeneruotos, WCAG AA patikrinta; tamsi pridedama į /etc/xdg/kdeglobals; **nematyta ekrane** |
| Plasma išdėstymas (viršutinė juosta, dock, tapetai) | 🧪 | Skriptas parašytas; logika patikrinta su imituota Plasma API (įsk. senesnę versiją be kai kurių savybių). **Tikrame Plasma nematyta** |
| Launcher, langai, Alt+Tab | 🧪 | Tai standartinės Plasma funkcijos (Kickoff, KWin); sukonfigūruotas tik Kickoff skydelyje. Nematyta |
| Failų naršyklė | 🧪 | Dolphin yra paketų sąraše; nepritaikyta, nematyta |
| Nova Settings | ❌ | Kol kas naudojami standartiniai KDE System Settings |
| Tinklas / garsas / Bluetooth valdymas | ❌ | Planuojama per NetworkManager / PipeWire / BlueZ |
| Pranešimai, greitieji nustatymai | ❌ | |
| Boot / Login ekranai | ❌ | Bus standartiniai SDDM/Plymouth, kol 6 etape nebus NovaOS temų |
| ISO, diegimo vedlys | 🧪 | Build skriptas + GitHub Actions parašyti, **nė karto nepaleisti**. Calamares bus su Debian pavadinimu |
| SHA256, release notes | ❌ | Kai bus ISO |
| Diegimo instrukcija, VM testavimo instrukcija | ❌ | 8 etapas |
| Wine suderinamumas | ❌ | Pasirinktinai, vėliau |

## Žinomi apribojimai
- Nieko iš ISO/Plasma dalies nebuvo paleista tikroje aplinkoje (nebuvo galimybės). Tikėtina, kad pirmas ISO build pareikalaus pataisymų.
- Paketų pavadinimai Debian 13 sąraše neverifikuoti prieš archyvą; neteisingas pavadinimas nutrauks build.
- Secure Boot nepatikrintas. Calamares dar su Debian branding.
- Live režimo automatinis prisijungimas priklauso nuo `live-config`; jei neįvyksta: nova / live.
- `novactl updates` rodo būseną pagal **vietinį** paketų indeksą (smėlio dėžėje jis 9 dienų senumo).
