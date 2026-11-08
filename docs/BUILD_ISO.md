# Kaip gauti NovaOS ISO (be Linux ir be Python jūsų kompiuteryje)

ISO surenkamas GitHub debesyje. Jums reikia tik naršyklės ir nemokamos GitHub paskyros.
Ruošiamasi **~1–2 val. surinkimui**; pirmas bandymas gali nepavykti (žr. „Jei nepavyko“).

## 1. Įkelkite projektą į GitHub
1. Sukurkite paskyrą: github.com → Sign up.
2. Dešinėje viršuje **+ → New repository**. Pavadinimas: `novaos`. Palikite **Public**
   (nemokamoje paskyroje tai paprasčiausia; viešas – nes ISO bus matomas visiems). **Create repository**.
3. Išarchyvuokite `novaos-0.1.0-dev.zip`. Repozitorijos puslapyje spauskite **uploading an existing file**.
4. **Nutempkite VISO aplanko `novaos` TURINĮ** (ne patį aplanką): `.github`, `docs`, `iso`, `src`, `tests`,
   `theme`, `tools`, `Makefile`, `README.md`, `VERSION`. Spauskite **Commit changes**.
5. **Patikrinkite**: repozitorijoje turi matytis aplankas `.github` ir jame `workflows/build-iso.yml`.
   Jei `.github` nepasirodė: **Add file → Create new file**, kaip pavadinimą įrašykite
   `.github/workflows/build-iso.yml` ir įklijuokite to failo turinį.

## 2. Paleiskite surinkimą
1. Viršuje **Actions** (jei prašo – „I understand my workflows, enable them“).
2. Kairėje **Build NovaOS ISO → Run workflow → Run workflow**.
3. Palaukite, kol atsiras žalia varnelė (~1–2 val.). Raudonas X = nepavyko.

## 3. Atsisiųskite
Repozitorijos pagrindiniame puslapyje dešinėje **Releases** → naujausias → `novaos-0.1.0-dev-amd64.iso`
ir `SHA256SUMS`.

**Jei ISO suskaidytas į dalis** (`...iso.part00`, `...iso.part01`), sujunkite Windows `cmd`:
```
copy /b novaos-0.1.0-dev-amd64.iso.part00 + novaos-0.1.0-dev-amd64.iso.part01 novaos-0.1.0-dev-amd64.iso
```

## 4. Patikrinkite parašą (nebūtina, bet rekomenduojama)
PowerShell: `Get-FileHash novaos-0.1.0-dev-amd64.iso -Algorithm SHA256`
ir palyginkite su `SHA256SUMS` turiniu.

## Jei nepavyko
Actions → paspauskite raudoną paleidimą → **Build ISO inside a Debian 13 container** → nukopijuokite
**paskutines ~40 eilučių** ir atsiųskite man. Dažniausia pirmo karto priežastis – neteisingas paketo pavadinimas
sąraše `iso/config/package-lists/novaos.list.chroot`; tai taisoma viena eilute. Pilnas žurnalas yra
**build-log** artifact'e (paleidimo puslapio apačioje).
