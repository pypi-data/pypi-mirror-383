# Reader BOTDA

Pacchetto per lettura e visualizzazione delle misure salvate da software per sensore BOTDA.

## Installazione

Tramite `pip`:

```bash
pip install readerbotda
```

## Utilizzo

Per prima cosa è necessario caricare il necessario dai due moduli di lettura e visualizzazione:

```python
from ReaderBOTDA.reader import Profile, multipleProfile, Raw
from ReaderBOTDA.plotter.plotly import Plotly
```

Per il resto del codice utilizzeremo sempre lo stesso oggetto `plotter`, che va inizializzato e poi fornito quando si leggono i files.

```python
plotter = Plotly(theme='plotly')
```

Si può scegliere un tema che verrà usato per tutte le misure generate dal Plotter. [doc link](https://plotly.com/python/templates/)

> Available templates: ['ggplot2', 'seaborn', 'simple_white', 'plotly', 'plotly_white', 'plotly_dark', 'presentation', 'xgridoff', 'ygridoff', 'gridon', 'none']

L'idea è che chiunque potrebbe creare una nuova classe parente della classe `Plotter` in modo che non venga utilizzato il pacchetto `plotly` ma quello che si preferirà (bokeh, matplotlib...). La nuova classe dovrà avere una definizione di tutti i metodi astratti della classe `Plotter`.

### Misura Singola

Lettura di singola misura da un singolo file "profilo" di tipo json.

```python
misura = Profile('data/profiles/2021-11-08_16-51-16.652_rawarray.json',plotter=plotter)

fig = misura.plot() #misura.plot(title='Titolo custom')
plotter.show(fig)
fig.write_html("prova.html", full_html=False, include_plotlyjs='cdn')
```

### Misure multiple in una cartella

Lettura di tutti i file di tipo profilo in una cartella, contenente files di tipo json:

```python
from datetime import datetime
folder = 'data/profiles/'
misure = multipleProfile(folder, plotter = plotter)
misure = multipleProfile(folder, plotter = plotter, n_measure=10)
misure = multipleProfile(folder, plotter = plotter, n_measure=10, start_measure=5)
misure.plot()
misure.plot(startTime=datetime(2021,11,8,16,51,18))
misure.plot(startTime=datetime(2021,11,8,16,51,18),stopTime=datetime(2021,11,8,16,51,21))
```

E' possibile limitare la lettura a `n_measure` file consecutivi; in questo caso è anche possibile utilizzare il parametro `start_measure` per leggere `n_measure` a partire da `start_measure`.
Nei plot è quindi possibile indicare un range temporale utilizzando i parametri opzionali `startTime` e/o `stopTime`.

Infine è possibile calcolare e visualizzare media e deviazione standard dei profili misurati:

```python
misure.calcStatistics(plot=True)
```

#### Leggere solo un subset

Sono disponibili i parametri opzionali:

- `start_measure`, che può essere un intero o un `datetime.datetime`
- `stop_measure`, che può essere un `datetime.datetime`
- `n_measure`, che può essere un intero

```python
misure = multipleProfile(folder, plotter = plotter, n_measure=2, start_measure=1)

from datetime import datetime
start_datetime = datetime(2023,2,21,13,56,0)
stop_datetime = datetime(2023,2,21,13,57,0)

misure = multipleProfile(folder, plotter = plotter,start_measure=start_datetime,stop_measure=stop_datetime)
misure = multipleProfile(folder, plotter = plotter,start_measure=start_datetime,n_measure=2)
misure = multipleProfile(folder, plotter = plotter,stop_measure=stop_datetime)
misure = multipleProfile(folder, plotter = plotter,start_measure=2,stop_measure=stop_datetime)
```

#### Calcolo correlazione

```python
correlazioni_max = misure.calcCorrelations(type='max',reference='previous',range=(20,200))
correlazioni_bfs = misure.calcCorrelations(type='bfs',reference='previous')
correlazioni_bfs = misure.calcCorrelations(type='bfs',reference='first')
```

Si utilizza la funzione [`np.corrcoef`](https://numpy.org/doc/stable/reference/generated/numpy.corrcoef.html) per calcolo correlazione tra varie misure, dell'array dei massimi o dell'array dei bfs. Il riferimento su cui è calcolata la correlazione può essere la misura precedente o la primissima misura del set. E' inoltre possibile indicare un range, espresso in campioni, su cui limitare il calcolo. La funzione `calcCorrelations` ritorna un `np.array`.

### Misura Raw

Lettura di file json di debug che contiene intera matrice BGS e test dei metodi disponibili.

```python
raw = Raw(filename='data/raw/2021-11-08_16-51-16.652_rawmatrix.json', plotter=plotter)
raw.plot2d(title='prova titolo')
raw.plotMax()
raw.plot3d()
```

E' possibile plottare tutti i profili BGS e indicare uno specifico indice da mettere in primo piano:

```python
fig = raw.plotBGS(index=125)
plotter.show(fig)
```

## Lettura di misure in singolo file H5

Per leggere misure salvate in un file H5, è possibile utilizzare la classe `h5Profile`:

```python
from ReaderBOTDA.reader import h5Profile

h5 = h5Profile('data/2023_09/build1.3_profile.h5', plotter=plotter)
```

A questo punto l'oggetto `h5Profile` si dovrebbe comportare come `multipleProfile`, quindi è possibile utilizzare i metodi `plot()`, `calcStatistics()`, `calcCorrelations()` e così via.

## Plotter Bokeh

Oltre al plotter Plotly è disponibile anche una versione che utilizza il pacchetto `bokeh`. Non sono al momento disponibili i metodi `Bokeh.plot2d()` e `Bokeh.plot3d()`.

```python
from ReaderBOTDA.plotter.bokeh import Bokeh
from bokeh.io import output_notebook
output_notebook()
plotter = Bokeh(theme='night_sky')
```

I temi a disposizione di default sono:
>caliber, dark_minimal, light_minimal, night_sky, contrast

A questo punto è possibile chiamare i vari metodi come già mostrato per plotter Plotly:

```python
misura = Profile('data/profiles/2021-11-08_16-51-16.652_rawarray.json',plotter=plotter)
fig = misura.plot()
plotter.show(fig)
```

## TODO

1. lettura misure raw da file H5.
2. sistemare settings nelle ultime versioni di sw.
3. sistemare la timezone nelle misure.
4. aggiungere ricalcolo stima BFS a partire da dati raw.
