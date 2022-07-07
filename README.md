# Stage 2022 ai Laboratori Nazionali di Legnaro (LNL) dell'Istituto Nazionale di Fisica Nucleare (INFN) – Elaborato del Tema E

True Random Number Generator basato su fenomeni fisici.

Autori (ed ex-stagisti): **Riccardo Bergamaschi**, **Jacopo Di Nardo**, **Rosalinda Permunian** e **Giacomo Simonetto**

## Installazione

Non essendo una vera e propria libreria, questo progetto non necessita di essere installato; tuttavia, per poter eseguire i programmi localmente è necessario installare alcune dipendenze.

### Dipendenze

Di seguito sono elencate le dipendenze:

* Per i grafici:
  * Libreria open-source [matplotlib](https://matplotlib.org/)

* Per la lettura dei file di dati in formato `.root` (ne serve almeno una):
  * Libreria open-source [uproot](https://uproot.readthedocs.io/en/latest/) (consigliabile perché più leggera)
  * Framework [PyROOT](https://root.cern/) del CERN (disponibile solo su UNIX)

Per installare le dipdendenze nell'ambiente `conda` attualmente attivo:

```bash
conda install -c conda-forge uproot matplotlib
```

Per chi usa `mamba`:

```bash
mamba install -c conda-forge uproot matplotlib
```

Per chi usa `pip`:

```bash
pip install uproot awkward matplotlib
```

> **Note**
> Per gli utenti Windows che vogliono usare `PyROOT`, è necessario compilare il framework C++ `ROOT` da codice sorgente, [come illustrato nella documentazione](https://root.cern/install/#build-from-source) – in effetti esiste ROOT per Windows precompilato, ma PyROOT non è incluso.
>
> L'alternativa sarebbe utilizzare Unix virtualizzato, come descritto in seguito.

### Setup consigliato

Di seguito i passaggi consigliati per disporre di un ambiente di sviluppo robusto e veloce, ma che non occupa troppo spazio su disco.

Volendo, è possibile installare un IDE (Integrated Development Environment, Ambiente di Sviluppo Integrato) come [Visual Studio Code](https://code.visualstudio.com/).

Le estensioni di Visual Studio Code consigliate sono:

* [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
* [ROOT File Viewer](https://marketplace.visualstudio.com/items?itemName=albertopdrf.root-file-viewer)

#### Setup su Unix

Digita i seguenti comandi, uno alla volta, nel tuo terminale:

```bash
# 1. Installa il gestore di pacchetti e di ambienti Python `mamba`
brew install mambaforge || { { wget -O Mambaforge.sh "https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-$(uname)-$(uname -m).sh" || curl -fsSLo Mambaforge.sh "https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-MacOSX-$(uname -m).sh" ; } && bash Mambaforge.sh -b && export PATH="$HOME/mambaforge/bin:$PATH"; }
# 2. Attiva `mamba`
mamba init "$(basename "${SHELL}")"
# 3. Riavvia la shell
exec "$SHELL"
# 4. Crea un ambiente virtuale (qui chiamato `iLoveTemaE` - per scegliere un altro nome, semplicemente digitarlo al posto di `iLoveTemaE`)
mamba create -y -c conda-forge -n iLoveTemaE python uproot matplotlib
# 5. Attiva l'ambiente virtuale
mamba activate iLoveTemaE
# 6. Clona questa repository
gh repo clone RBerga06/infn-lnl-stage2022-temaE || git clone https://github.com/RBerga06/infn-lnl-stage2022-temaE.git
# 7. Entra nella repository
cd infn-lnl-stage2022-temaE
# 8. Esegui un file Python, in questo caso `stagisti.py`
python -O src/stagisti.py
```

È consigliabile installare anche Visual Studio Code e alcune estensioni, come mostrato sopra.

#### Setup su Windows

1. Scarica e installa `git` [dal sito ufficiale](https://git-scm.com/download/win)
2. Scarica e installa `mambaforge` [dal sito ufficiale](https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-Windows-x86_64.exe)
3. Installato `mambaforge`, esegui i seguenti comandi dal `Prompt dei Comandi`:

```bash
# 3.0. Attiva mambaforge
C:\Program Data\mambaforge\condabin\activate.bat
# 3.1. Crea un ambiente virtuale (qui chiamato `iLoveTemaE` - per scegliere un altro nome, semplicemente digitarlo al posto di `iLoveTemaE`)
mamba create -y -c conda-forge -n iLoveTemaE python uproot matplotlib
# 3.2. Attiva l'ambiente virtuale
mamba activate iLoveTemaE
# 3.3. Clona questa repository
git clone https://github.com/RBerga06/infn-lnl-stage2022-temaE.git
# 3.4. Entra nella repository
cd infn-lnl-stage2022-temaE
# 3.5. Esegui un file Python, in questo caso `stagisti.py`
python -O src/stagisti.py
```

È consigliabile installare anche Visual Studio Code e alcune estensioni, come mostrato sopra.

#### Setup di una macchina virtuale con Ubuntu su Windows

Giusto qualche dritta per installare Ubuntu su Windows (il procedimento è più o meno lo stesso anche su UNIX).

Potete fare riferimento a questi video:

* [Ubuntu 22.04 LTS su Windows 11](https://youtu.be/v1JVqd8M3Yc)
* [Ubuntu 20.04 LTS su Windows 10](https://youtu.be/x5MhydijWmc)

> **Warning**
> VirtualBox chiama “MB” i MiB – cercate di non frustrarvi troppo.
> Per chi non conoscesse la differenza tra MB e MiB, collegarsi urgentemente a [Wikipedia](https://it.wikipedia.org/wiki/Bit), che include una tabella molto chiara.

> **Warning**
> **Disclaimer**
> Se qualcosa dovesse andare storto, **non** create una `issue` (o una discussione) in questa `repo` di GitHub – gli ex-stagisti del tema E *non* si impegnano a risolvere problemi del genere.
> Tuttavia, in questi casi [Google](https://www.google.com) si può rivelare uno strumento particolarmente utile, e se neanche così risolvete il vostro problema, potete sempre appellarvi a un forum.

## Aggiornamento

Per aggiornare il clone locale di questa repository con gli ultimi miglioramenti, utilizzare i comandi:

```bash
git fetch
git pull
```

## Utilizzo

Per eseguire un file, aprire il terminale e assicurarsi di essere nella cartella principale.
Poi, digitare:

```bash
python src/nome-del-file.py
```

Di default, vengono stampate informazioni utili per capire cosa sta facendo il programma in questo momento (per esempio, per capire quali azioni richiedono maggior tempo).
Per disattivare questo comportamento, basta inserire la flag `-O`:

```bash
python -O src/nome-del-file.py
```

Di default, la libreria per leggere i dati è `PyROOT` (quando installata); altrimenti, viene utilizzata `uproot`.
Per forzare l'utilizzo di `uproot` anche quando `PyROOT` è installata, impostare la variabile d'ambiente `FORCE_UPROOT`.
Su UNIX:

```bash
export FORCE_UPROOT=1  # Anche '=True' va bene
python src/file.py
```

O, per evitare di usare `export`:

```bash
FORCE_UPROOT=1 python src/file.py
```

### Stagisti

Il file `stagisti.py` contiene il codice utilizzato per determinare l'ordine di presentazione del lavoro svolto.
Potete utilizzarlo come un test per vedere se tutto funziona correttamente: `python -O src/stagisti.py` dovrebbe scrivere a schermo `['Rosalinda', 'Riccardo', 'Giacomo', 'Jacopo']`.

### TRNG

Il TRNG (True Random Number Generator) è definito nel file `rand.py`.
Per utilizzarlo, basta importare da lì la classe `TrueRandomGenerator` e utilizzare il metodo `random_number`:

```python
from rand import TrueRandomGenerator

trng = TrueRandomGenerator()

# Un numero casuale tra 0 e 255
x = trng.random_number()

print(x)
```

> **Note**
> Essendo i dati casuali predeterminati (e salvati nel file `data.root`), ogni esecuzione del programma darà *sempre* gli stessi risultati.
> Per apprezzare la casualità dei dati è necessario chiamare `random_number()` più volte, per notare la successione di numeri che viene generata (sarà sempre la stessa, ma di per sé casuale).

```python
from rand import TrueRandomGenerator

trng = TrueRandomGenerator()

# Una lista di 10 numeri casuali
xs = [trng.random_number() for _ in range(10)]

print(*xs, sep=", ")
```

Il TRNG legge i tempi dal file `data.root`, ne calcola le differenze e da queste ricava bit casuali (`0` o `1` in ordine imprevedibile).
Raggruppando ad 8 ad 8 questi bit genera byte (anche questi casuali), convertiti poi in numeri decimali da 0 a 255.
Per aggiungere, alla fine di tutti i numeri, gli stessi convertiti erroneamente, passare il parametro `bug=True`:

```python
trng = TrueRandomGenerator(bug=True)
```

Abbiamo aggiunto la possibilità di caricare i dati direttamente da una lista di eventi (mediante il parametro `events=`), o di leggere i dati da file (uno – `file=` o più – `files=`).

```python
from rand import TrueRandomGenerator, Event, SRC
# Carica i dati da una lista
#   "data" dev'essere una lista di `Event`i
trng = TrueRandomGenerator(events=data)
# Legge i dati dal file ~/data/my_data.root
trng = TrueRandomGenerator(file="~/data/my_data.root")     # Due scritture
trng = TrueRandomGenerator(files=["~/data/my_data.root"])  #  equivalenti
# Legge i dati dai file ~/data/data1.root e ~/data/data2.root
trng = TrueRandomGenerator(files=["~/data/data1.root", "~/data/data2.root"])
# Se non viene specificato alcun parametro di caricamento dati, usa il file `SRC/data.root`
trng = TrueRandomGenerator()                      # Due scritture
trng = TrueRandomGenerator(file=SRC/"data.root")  #  equivalenti
```

> **Note**
> I parametri `file=` e `files=` sono incompatibili fra loro (se specificati entrambi, `file=` viene ignorato).
> Invece, `file=` e `events=` (o `files=` e `events=`) possono essere passati entrambi: *prima* verranno importati gli eventi da `events=`, e poi a questi andranno a concatenarsi quelli letti dai `files=` (o dal `file=`).
> Essendo totalmente scorrelato dall'acquisizione dati, `bug=` è compatibile con qualunque combinazione appena descritta.

> **Warning**
> I file specificati devono necessariamente avere la stessa struttura di `data.root` e `fondo.root` (aprite uno dei due con `rootbrowse` per i dettagli).

> **Warning**
> I file specificati devono necessariamente contenere almeno 9 eventi, cioè il minimo per generare un byte casuale.

### Stima di π

Il nostro gruppo ha utilizzato il TRNG per stimare π tramite il metodo Monte Carlo: potete trovare il codice in `pi.py`.
Abbiamo provato a stimare π combinando i dati in tre modi diversi per ottenere le coordinate dei punti: per apprezzare al meglio le differenze, abbiamo reso il programma interattivo.
Utilizzando infatti `python -O pi.py`, il programma chiede all'utente di selezionare un algoritmo di combinazione dei numeri casuali.
Per non doverlo specificare ogni volta a programma lanciato, abbiamo aggiunto la possibilità di specificarlo direttamente dalla riga dicomando.
Ad esempio, per utilizzare l'algoritmo n°`0`: `python -O pi.py 0`.
Esiste anche la possibilità di passare `bug=True` al TRNG da riga di comando: per questa opzione, specificare la flag `--bug` dopo l'eventuale numero: `python -O pi.py 0 --bug`.
È anche possibile disattivarla esplicitamente tramite la flag `--no-bug`.
Se vengono specificate entrambe, conta l'ultima inserita.
