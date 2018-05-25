import logging
import pandas
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, Slider
from bokeh.plotting import figure
from bokeh.server.server import Server

logger = logging.getLogger(__name__)

print('read data')
store = pandas.HDFStore('evaluation.h5', 'r')
experiments = store['/experiments']
plot_data = store['/rna_evaluation_data']
store.close()
print('loaded')


def modify_doc(doc):
    print('hi')
    source = ColumnDataSource(data=plot_data)

    plot = figure()
    scatter = plot.circle(x='ENCFF200USH', y='ENCFF306TLL', color='color', source=source)

    def callback(attr, old, new):
        logger.info('callback', str(new))
        #y = experiments.iloc[new]
        #scatter.y = y

    slider = Slider(start=0, end=len(experiments), value=0, step=1)
    slider.on_change('value', callback)

    doc.add_root(column(slider, plot))


# Setting num_procs here means we can't touch the IOLoop before now, we must
# let Server handle that. If you need to explicitly handle IOLoops then you
# will need to use the lower level BaseServer class.
server = Server({'/': modify_doc}, num_procs=4)
server.start()

if __name__ == '__main__':
    print('Opening Bokeh application on http://localhost:5006/')

    #server.io_loop.add_callback(server.show, "/")
    server.io_loop.start()
