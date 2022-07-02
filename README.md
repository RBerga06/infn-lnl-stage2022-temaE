# Stage 2022 ai Laboratori Nazionali di Legnaro (LNL) dell'Istituto Nazionale di Fisica Nucleare (INFN) – Elaborato del Tema E

True Random Number Generator based on Physical Phenomena

## Installazione

Non essendo una vera e propria libreria, questo progetto non necessita di essere installato; tuttavia, per poter eseguire i programmi localmente è necessario installare alcune dipendenze.

### Dipendenze

Librerie Python:

* Libreria open-source [matplotlib](https://matplotlib.org/) (per i grafici)
* Framework [PyROOT](https://root.cern/) del CERN (per la lettura dei file di dati)

Per installare le dipdendenze nell'ambiente `conda` attualmente attivo:

```bash
conda install -c conda-forge root matplotlib
```

(non essendo `PyROOT` disponibile su PyPI, non esiste un comando analogo per `pip`)

> **Note**
>
> Per gli utenti Windows, è necessario compilare ROOT dal codice sorgente, [come illustrato nella documentazione](https://root.cern/install/#build-from-source) (in effetti esiste ROOT per Windows precompilato, ma PyROOT non è incluso).
>
> L'alternativa è utilizzare una macchina virtuale Unix, come descritto in seguito.

### Setup consigliato

Di seguito i passaggi consigliati per disporre di un ambiente di sviluppo robusto e veloce, ma che non occupa troppo spazio su disco.

#### Setup su Unix

Digita i seguenti comandi, uno alla volta, nel tuo terminale:

```bash
# 1. Installa il gestore di pacchetti e di ambienti Python `mamba`
brew install mambaforge || { { wget -O Mambaforge.sh "https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-$(uname)-$(uname -m).sh" || curl -fsSLo Mambaforge.sh "https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-MacOSX-$(uname -m).sh" ; } && bash Mambaforge.sh -b; }
# 2. Attiva `mamba`
mamba init "$(basename "${SHELL}")"
# 3. Riavvia la shell
exec "$SHELL"
# 4. Crea un ambiente virtuale (qui chiamato `iLoveTemaE` - per scegliere un altro nome, semplicemente digitarlo al posto di `iLoveTemaE`)
mamba create -n iLoveTemaE python root matplotlib
# 5. Attiva l'ambiente virtuale
mamba activate iLoveTemaE
# 6. Clona questa repository
gh repo clone RBerga06/infn-lnl-stage2022-temaE || https://github.com/RBerga06/infn-lnl-stage2022-temaE.git
# 7. Entra nella repository
cd infn-lnl-stage2022-temaE
# 8. Esegui un file Python, in questo caso `stagisti.py`
python3 src/stagisti.py
```

Volendo, è possibile installare un IDE (Integrated Development Environment, Ambiente di Sviluppo Integrato) come [Visual Studio Code](https://code.visualstudio.com/).

Le estensioni di Visual Studio Code consigliate sono:

* [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
* [ROOT File Viewer](https://marketplace.visualstudio.com/items?itemName=albertopdrf.root-file-viewer)

#### Setup di una macchina virtuale con Ubuntu

> **Warning**
> Se qualcosa dovesse andare storto, **non** create una `issue` (o una discussione) in questa `repo` di GitHub – gli ex-stagisti del tema E *non* si impegnano a risolvere problemi del genere.
> Tuttavia, in questi casi [Google](https://www.google.com) si può rivelare uno strumento particolarmente utile, e se neanche così risolvete il vostro problema, potete sempre appellarvi a un forum.

> **Note**
> [Questo video](https://youtu.be/x5MhydijWmc) potrebbe esserti utile

> **Warning**
> VirtualBox chiama “MB” i “MiB” – Cerca di non dare di matto
> Per chi non sapesse cosa sono MB e MiB, collegarsi urgentemente a [Wikipedia](https://it.wikipedia.org/wiki/Bit), che fornisce una tabella molto utile

1. Scarica il sitema operativo Ubuntu come `.iso`:
    1. Vai alla [pagina ufficiale di download di Ubuntu in italiano](https://www.ubuntu-it.org/download)
    2. Seleziona la versione di interesse (consigliata: `22.04.4 LTS`)
    3. Seleziona il pacchetto corretto:
        * Se sei qui solo perché usi Windows, seleziona `Desktop`
        * Se sei qui perché ami UNIX e il terminale, anche `Server` va bene
    4. Clicca il pulsante `Avvia il download` e attendi che il file venga scaricato.

2. Scarica e installa VirtualBox (se non lo hai già):
    1. Vai alla [pagina ufficiale di download di VirtualBox](https://www.virtualbox.org/wiki/Downloads)
    2. Clicca il link di download adeguato alla tua piattaforma (preferibilmente nel primo paragrafo del tipo `VirtualBox 6.<qualcosa> platform packages`)
    3. È consigliabile anche scaricare l'extension pack, nel paragrafo immediatamente successivo
    4. Apri il primo file scaricato e lancia l'installer di VirtualBox
    5. Segui le istruzioni sullo schermo
    6. Su macOS, se e quando proposto da una finestra di dialogo, apri Preferenze di Sistema, sbloccalo cliccando sul lucchetto in basso a sinistra e inserendo la tua password (o usando TouchID) e clicca su `Consenti` nella scheda `Generale` del pannello `Sicurezza e Privacy` per abilitare l'estensione di sistema firmata `Orcale Inc.`
    7. Riavvia il computer quando richiesto
    8. Torna nella cartella dei download e lancia il file dell'estensione scaricato in precedenza: dovrebbe aprirsi VirtualBox.
    9. Segui le istruzioni sullo schermo

3. Crea una macchina virtuale con Ubuntu:
    1. Se necessario, apri VirtualBox
    2. Clicca sul pulsante `Nuova` per creare una macchina virtuale
    3. Assegnale un nome a piacimento (ad esempio `Ubuntu for Tema E`)
    4. Seleziona il sistema operativo `Ubuntu (64-bit)` nella categoria `Linux`
    5. Assegna alla macchina virtuale *almeno* 2GiB (= 2048 MiB) di RAM
    6. Segui le istruzioni a schermo – puoi lasciare gli altri parametri con i loro valori di default

4. Correggi le impostazioni della macchina virtuale con Ubuntu:
    1. Seleziona la macchina virtuale e clicca sul pulsante `Impostazioni`
    2. Seleziona il gruppo `Memoria` nella scheda `Sistema` e assegna alla VM *almeno* 2 core di CPU

5. Avvia la macchina virtuale:
    1. Seleziona la macchina virtuale e clicca sul pulsante `Avvia`
    2. Nella finestra di dialogo, clicca su `Sfoglia...` e seleziona il file `.iso` di Ubuntu.
    3. Clicca su `Avvia`

6. Una volta avviatosi l'installer del sistema, seleziona `Installa Ubuntu` e segui i passaggi visualizzati sullo schermo

7. Ora il tuo sistema è pronto: segui i passaggi descritti sopra per effettuare il setup dell'ambiente di sviluppo.
