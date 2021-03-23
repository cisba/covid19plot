'''
Simple script to plot graphs from official data about COVID-19
'''
import sys
import requests
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

# Italian data header
# data,stato,ricoverati_con_sintomi,terapia_intensiva,totale_ospedalizzati,isolamento_domiciliare,totale_positivi,variazione_totale_positivi,nuovi_positivi,dimessi_guariti,deceduti,casi_da_sospetto_diagnostico,casi_da_screening,totale_casi,tamponi,casi_testati,note

# url, selection and data frame load
url = 'https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-andamento-nazionale/dpc-covid19-ita-andamento-nazionale.csv'
selection=["data","terapia_intensiva", "ricoverati_con_sintomi", "isolamento_domiciliare", "nuovi_positivi", "tamponi"]
df_all = pd.read_csv(url, usecols=selection, index_col=0, parse_dates=['data'])

# repeat for each graph
#for graph_name in ('', 'log', 'hos', 'tam', 'hosp', 'tamp'):
for graph_name in ('hos',):

    # create dataframe from url using columns selection
    percentage = False

    if graph_name in ('', 'log'):
        df = df_all.loc[:, ("terapia_intensiva", "ricoverati_con_sintomi", "isolamento_domiciliare", "tamponi")]
        legend=["Hospitalized ICU","Hospitalized not ICU", "Home isolation", "Daily tests"]
        # Daily data have to be calculated subtracting the previous day total
        df["nuovi_tamponi"] = df["tamponi"] - df["tamponi"].shift(1)
        df = df[["terapia_intensiva", "ricoverati_con_sintomi", "isolamento_domiciliare", "nuovi_tamponi"]]

    elif graph_name in ('hos'):
        df = df_all.loc[:, ("terapia_intensiva", "ricoverati_con_sintomi")]
        legend=["Hospitalized ICU","Hospitalized not ICU"]

    elif graph_name in ('tam'):
        df = df_all.loc[:, ("nuovi_positivi", "tamponi")]
        # Daily data have to be calculated subtracting the previous day total
        df["nuovi_tamponi"] = df["tamponi"] - df["tamponi"].shift(1)
        df["nuovi_negativi"] = df["nuovi_tamponi"] - df["nuovi_positivi"]
        df = df[["nuovi_positivi", "nuovi_negativi", "nuovi_tamponi"]]
        legend=["Daily positive cases","Daily negative cases", "Daily tests"]

    elif graph_name=='hosp':
        percentage = True
        df = df_all.loc[:, ("terapia_intensiva", "ricoverati_con_sintomi")]
        legend=["Hospitalized ICU","Hospitalized not ICU"]

    elif graph_name=='tamp':
        percentage = True
        df = df_all.loc[:, ("nuovi_positivi", "tamponi")]
        # Daily data have to be calculated subtracting the previous day total
        df["nuovi_tamponi"] = df["tamponi"] - df["tamponi"].shift(1)
        df["nuovi_negativi"] = df["nuovi_tamponi"] - df["nuovi_positivi"]
        df = df[["nuovi_positivi", "nuovi_negativi"]]
        legend=["Daily positive cases","Daily negative cases"]
        df = df.iloc[1:]
    timestamp=df.tail(n=1).index.astype(str)[0].split(' ')[0]

    # apply seaborn template and plot
    sns.set(rc={'figure.figsize':(12, 6)})
    if percentage:
        # transform the data to percentage (fraction)
        df_perc = df.divide(df.sum(axis=1), axis=0)
        df = df_perc * 100
        ax = df.plot.area()
    else:
        ax = df.plot()

    # create annotation to display the last value
    floor=0
    for line, name in zip(ax.lines, df.columns):
        y = line.get_ydata()[-1]
        if percentage:
            annot_format=f'{y-floor:.2f}%'
            py=floor+(y-floor)/2
        else:
            annot_format=f'{y:,}'
            py=y
        ax.annotate(annot_format, xy=(0.93,py), xytext=(6,0), color=line.get_color(),
                    xycoords = ax.get_yaxis_transform(), textcoords="offset points",
                    size=9, va="center", ha="left")
        floor+=y

    # set y axis number format
    tick = mtick.StrMethodFormatter('{x:,.0f}')
    ax.yaxis.set_major_formatter(tick)

    # hide label of x axis
    ax.xaxis.label.set_visible(False)

    # adjust margins
    ax.margins(0.08,0.03)

    # adjust others stuff
    legend_position='upper left'
    if graph_name=='log':
        ax.set_yscale('log')
    elif percentage:
        ax.set_ylabel('Percent (%)')
        ax.yaxis.set_major_formatter(mtick.PercentFormatter())
        legend_position='center'

    # plot legend, title, footer
    plt.legend(legend, loc=legend_position)
    plt.title('COVID-19 in Italy at %s' % timestamp)
    footer="Chart: Emanuele Cisbani - Data: Protezione Civile - License: CC BY-SA"
    plt.annotate(footer, (.5,.98), (0,0), xycoords='axes fraction', textcoords='offset points', va='top', ha='center', color='gray', size=8)

    # save
    ax.get_figure().savefig("Covid-19"+graph_name+".png")
    #plt.show()
