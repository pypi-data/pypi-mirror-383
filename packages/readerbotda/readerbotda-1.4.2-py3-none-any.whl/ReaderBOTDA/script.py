#TODO trovare modo di integrarlo in setup.py di setuptools: https://typer.tiangolo.com/tutorial/package/

'''
Per help, digitare in terminale: python readBOTDA.py --help
e poi per help specifici su uno dei comandi: python readBOTDA.py multi --help
'''

import typer
from pathlib import Path
from ReaderBOTDA.reader import Profile, multipleProfile, Raw
from ReaderBOTDA.plotter.plotly import Plotly
from dataclasses import asdict

app = typer.Typer()
PLOTTER = Plotly(theme='plotly_dark')

@app.command()
def single(filename: str, title:str=None):
    if not title:
        title = filename
    data = Profile(filename,PLOTTER)
    PLOTTER.show(data.plot(title=title))
    typer.secho("Settings:", fg=typer.colors.GREEN, bold=True)
    typer.echo(str(data.settings))

@app.command()
def multi(folder: str, title: str =None, stat: bool = True):
    if not title:
        title = folder
    data = multipleProfile(folder,PLOTTER)
    typer.secho(f"Lette {len(data.timestamps)} misure nella cartella {folder}", fg=typer.colors.GREEN, bold=True)
    PLOTTER.show(data.plot(title=title))
    if stat:
        PLOTTER.show(data.calcStatistics(plot=True,title=title))
    typer.secho("Settings:", fg=typer.colors.GREEN, bold=True)
    typer.echo(str(data.settings))

@app.command()
def raw(filename: str, title: str = None):
    
    from plotly.subplots import make_subplots
    if not title:
        title = filename

    data = Raw(filename, PLOTTER)
    typer.secho("Settings:", fg=typer.colors.GREEN, bold=True)
    typer.echo(str(data.settings))

    fig2d = data.plot2d()
    figMax = data.plotMax()
    figBGS = data.plotBGS()
    fig = make_subplots(rows=2, cols=2, shared_xaxes='columns', column_widths=[0.25, 0.75],row_heights=[0.75, 0.25])

    fig.add_trace(fig2d.data[0], row=1, col=2)
    fig.add_trace(figMax.data[0], row=2, col=2)
    fig.add_traces(figBGS.data, rows=1, cols=1)
    fig.update_xaxes(title_text='Position (m)',row=2,col=2)
    fig.update_xaxes(title_text='Frequency (GHz)',row=1,col=1)
    fig.update_yaxes(title_text='Frequency (GHz)',row=1,col=2)
    fig.update_yaxes(title_text='Amplitude (V)',row=1,col=1)
    fig.update_yaxes(title_text='Max Amp (V)',row=2,col=2)
    fig.update_layout(title_text=title,showlegend=False)
    fig.show()

if __name__ == "__main__":
    app()