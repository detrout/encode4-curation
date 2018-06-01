import logging

from bokeh.layouts import row, column, widgetbox, Spacer
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.plotting import figure
from bokeh.models.widgets import Select, Div, Paragraph
from bokeh.models.callbacks import CustomJS
import numpy
import pandas

#from data import (
#    annotations,
#    experiments,
#    quantifications,
#)

logger = logging.getLogger(__name__)

def get_experiment_from_file(experiments, rep):
    return experiments[experiments['gene_quantification'] == rep].iloc[0]


def to_description(experiments, rep):
    r = get_experiment_from_file(experiments, rep)

    return '{} {} {} {}'.format(
        r['lab'],
        r['biosample_term_name'],
        r['assay'],
        rep)


def from_description(text):
    rep = text.split()[-1]

    return rep


def display_event(div, source, plot, scatter, attributes=[], style='float:left;clear:left;font_size=10pt'):
    "Build a suitable CustomJS to display the current event in the div model."
    return CustomJS(args=dict(div=div, scatter=scatter), code="""
var attrs = %s; var args = [];
//for (var i = 0; i<attrs.length; i++) {
//    args.push(attrs[i] + '=' + cb_obj[attrs[i]]);
//}
// args.push(source);
// args.push(plot);
//var o = plot;
//for (var key in o) {
//    var x = o[key];
//    args.push(key + ": " + x);
//}
args.push(scatter.y);
var line = "<span style=%r><b>" + o + " " + "</b>(" + args.join("<br/>") + ")</span>\\n";
// var text = div.text.concat(line);
//var lines = text.split("\\n")
//if (lines.length > 35)
//    lines.shift();
//div.text = lines.join("\\n");
div.text = line;
//scatter.y = scatter.x;
    """ % (attributes, style))


class Evaluation:
    LINE_ARGS = dict(color="#3A5785", line_color=None)

    def __init__(self, experiments, data, bins=30):
        self.experiments = experiments
        self.data = data
        self.bins = bins
        self.hover = HoverTool(tooltips=[
            ('gene_id', '@gene_id'),
            ('gene_name', '@gene_name'),
            ('x', '$x'),
            ('y', '$y'),
            ('chr', '@chromosome'),
            ('start', '@start'),
            ('stop', '@stop'),
            ('strand', '@strand')])
        self.figure = figure(plot_width=600, plot_height=600)
        self.figure.add_tools(self.hover)
        self.div = Div(width=1000)

        self.source = ColumnDataSource(data)
#            self.quantifications.merge(self.annotations, left_index=True, right_index=True))

        descriptions = [to_description(experiments, x) for x in experiments['gene_quantification']]
        self.x_widget = Select(title='x', value=descriptions[0], options=descriptions)
        self.y_widget = Select(title='y', value=descriptions[1], options=descriptions)

        #self.x_widget.on_change('value', self.x_axis_control_changed)
        #self.y_widget.on_change('value', self.y_axis_control_changed)

        #ph = self.make_horizontal_histogram()
        #pv = self.make_vertical_histogram()
        #self.layout = column(widgetbox([self.x_widget, self.y_widget]),
        #                     column(row(self.figure, pv), row(ph, Spacer(width=200, height=200))))

        self.figure = figure(plot_width=600, plot_height=600)
        self.figure.add_tools(self.hover)
        self.scatter = self.figure.circle(self.x, self.y, color='color', source=self.source)
        self.figure.xaxis.axis_label = self.x_widget.value
        self.figure.yaxis.axis_label = self.y_widget.value
        #self.layout.children[1].children[0] = self.figure
        #self.layout.children[1].children[0].children[0] = self.figure

        self.layout = column(widgetbox([self.x_widget, self.y_widget]), row(self.figure, self.div))

    def x_axis_control_changed(self, attr, new, old):
        return self.axis_control_changed('x', attr, new, old)

    def y_axis_control_changed(self, attr, new, old):
        return self.axis_control_changed('y', attr, new, old)

    def axis_control_changed(self, axis, attr, new, old):
        logger.info(axis, 'axis changing', attr, new, old)
        accession = from_description(new)
        if axis == 'x':
            x = accession
            y = from_description(self.y_widget.value)
        elif axis == 'y':
            x = from_description(self.y_widget.value)
            y = accession
        else:
            raise ValueError('Unrecognized axis {}'.format(axis))
        print(x, y)
        #self.update_plot(x, y)

    def make_horizontal_histogram(self):
        x = self.x
        p = self.figure

        # create the horizontal histogram
        self.hhist, self.hedges = numpy.histogram(self.source.data[x], bins=self.bins)
        self.hzeros = numpy.zeros(len(self.hedges)-1)
        hmax = max(self.hhist)*1.1

        ph = figure(toolbar_location=None, plot_width=p.plot_width, plot_height=200, x_range=p.x_range,
                    y_range=(-hmax, hmax), min_border=10, min_border_left=50, y_axis_location="right")
        ph.xgrid.grid_line_color = None
        ph.yaxis.major_label_orientation = numpy.pi/4
        ph.background_fill_color = "#fafafa"

        ph.quad(bottom=0, left=self.hedges[:-1], right=self.hedges[1:], top=self.hhist, color="white", line_color="#3A5785")
        self.hh1 = ph.quad(bottom=0, left=self.hedges[:-1], right=self.hedges[1:], top=self.hzeros, alpha=0.5, **Evaluation.LINE_ARGS)
        self.hh2 = ph.quad(bottom=0, left=self.hedges[:-1], right=self.hedges[1:], top=self.hzeros, alpha=0.1, **Evaluation.LINE_ARGS)

        return ph

    def make_vertical_histogram(self):
        y = self.y
        p = self.figure
        # create the vertical histogram
        self.vhist, self.vedges = numpy.histogram(self.source.data[y], bins=self.bins)
        self.vzeros = numpy.zeros(len(self.vedges)-1)
        vmax = max(self.vhist)*1.1

        pv = figure(toolbar_location=None, plot_width=200, plot_height=p.plot_height, x_range=(-vmax, vmax),
                    y_range=p.y_range, min_border=10, y_axis_location="right")
        pv.ygrid.grid_line_color = None
        pv.xaxis.major_label_orientation = numpy.pi/4
        pv.background_fill_color = "#fafafa"

        pv.quad(left=0, bottom=self.vedges[:-1], top=self.vedges[1:], right=self.vhist, color="white", line_color="#3A5785")
        self.vh1 = pv.quad(left=0, bottom=self.vedges[:-1], top=self.vedges[1:], right=self.vzeros, alpha=0.5, **Evaluation.LINE_ARGS)
        self.vh2 = pv.quad(left=0, bottom=self.vedges[:-1], top=self.vedges[1:], right=self.vzeros, alpha=0.1, **Evaluation.LINE_ARGS)

        return pv

    def update_histograms(self, attr, old, new):
        x_data = self.source.data[self.x]
        y_data = self.source.data[self.y]

        inds = numpy.array(new['1d']['indices'])
        if len(inds) == 0 or len(inds) == len(x_data):
            hhist1, hhist2 = self.hzeros, self.hzeros
            vhist1, vhist2 = self.vzeros, self.vzeros
        else:
            neg_inds = numpy.ones_like(x_data, dtype=numpy.bool)
            neg_inds[inds] = False
            hhist1, _ = numpy.histogram(x_data[inds], bins=self.hedges)
            vhist1, _ = numpy.histogram(y_data[inds], bins=self.vedges)
            hhist2, _ = numpy.histogram(x_data[neg_inds], bins=self.hedges)
            vhist2, _ = numpy.histogram(y_data[neg_inds], bins=self.vedges)

        self.hh1.data_source.data["top"]   =  hhist1
        self.hh2.data_source.data["top"]   = -hhist2
        self.vh1.data_source.data["right"] =  vhist1
        self.vh2.data_source.data["right"] = -vhist2

    @property
    def x(self):
        return from_description(self.x_widget.value)

    @property
    def y(self):
        return from_description(self.y_widget.value)


logger.info('read data')
store = pandas.HDFStore('evaluation.h5', 'r')
experiments = store['/experiments']
plot_data = store['/rna_evaluation_data']
store.close()
logger.info('loaded')
E = Evaluation(experiments, plot_data)

from bokeh.plotting import curdoc
curdoc().add_root(Paragraph(text="FPKMs from ENCODE RNA-seq evaluation"))
curdoc().add_root(E.layout)
curdoc().title = "Compare RNA-seq evalation datasets"

#from bokeh.plotting import output_file, show
#output_file('evaluation_plot.html')
#show(E.layout)
