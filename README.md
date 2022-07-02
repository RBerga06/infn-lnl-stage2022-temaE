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
> Per gli utenti Windows, è necessario compilare ROOT dal codice sorgente, [come illustrato nella documentazione](https://root.cern/install/#build-from-source) (in effetti esiste ROOT per Windows precompilato, ma PyROOT non è incluso).
>
> L'alternativa è utilizzare Unix virtualizzato, come descritto in seguito.

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


#### Setup di una macchina virtuale con Ubuntu su Windows

Giusto qualche dritta per installare Ubuntu su Windows (il procedimento è più o meno lo stesso anche su UNIX).

Potete fare riferimento a questi video:

    * [Ubuntu su Windows 11](https://youtu.be/v1JVqd8M3Yc)
    * [Ubuntu su Windows 10](https://youtu.be/x5MhydijWmc)

> **Warning**
> VirtualBox chiama “MB” i “MiB” – Cerca di non dare di matto
> Per chi non sapesse cosa sono MB e MiB, collegarsi urgentemente a [Wikipedia](https://it.wikipedia.org/wiki/Bit), che fornisce una tabella molto utile

> **Warning**
> **Disclaimer**
> Se qualcosa dovesse andare storto, **non** create una `issue` (o una discussione) in questa `repo` di GitHub – gli ex-stagisti del tema E *non* si impegnano a risolvere problemi del genere.
> Tuttavia, in questi casi [Google](https://www.google.com) si può rivelare uno strumento particolarmente utile, e se neanche così risolvete il vostro problema, potete sempre appellarvi a un forum.
