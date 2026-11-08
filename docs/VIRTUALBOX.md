# NovaOS išbandymas VirtualBox (Windows)

Saugiausias būdas: nieko nekeičia jūsų diske ir Windows.

1. Įdiekite VirtualBox (virtualbox.org).
2. **New**: Name `NovaOS`, ISO Image – pasirinkite NovaOS ISO, Type `Linux`, Version `Debian (64-bit)`.
   **Pažymėkite „Skip Unattended Installation“.**
3. RAM: **4096 MB** (geriau 6144), CPU: **2+**, Disk: **40 GB**.
4. Prieš paleidimą: Settings → **Display**: Video Memory **128 MB**, Graphics Controller **VMSVGA**.
5. **Start**. Meniu pasirinkite „Live system“.
6. Jei prašo prisijungti: vartotojas `nova`, slaptažodis `live`.

## Kas turėtų būti
Viršuje juosta (meniu mygtukas kairėje, laikrodis viduryje, sistemos ikonos dešinėje), apačioje dock,
NovaOS fonas, tamsi tema. Meta (Windows) klavišas atidaro paleidiklį, Alt+Tab perjungia langus.
Jei vietoj to matote įprastą Kubuntu/Debian stiliaus darbalaukį, tema nepritaikė: padarykite ekrano nuotrauką ir atsiųskite man.

## Diegimas į virtualų diską
Paleiskite „Install“ programą (kol kas gali rodyti Debian pavadinimą, NovaOS branding dar nepadarytas).
Virtualiame diske formatavimas saugus, jūsų tikram diskui jis neliečia.

## Į tikrą kompiuterį
**Dar ne.** Pirmiausia turi pasisekti VM testai. Tada: pasidarykite atsarginę failų kopiją, ir diegimo vedlyje
disko pasirinkimas gali ištrinti esamus duomenis.
