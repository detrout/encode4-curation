function label_to_column (label) {
    const words = label.split(' ');
    return words[words.length-1];
}

function Plot() {
    this.experiment_to_file = {
        'Thomas Gingeras GM12878 total RNA-seq ENCFF783VBA': 'ENCFF783VBA',
        'Thomas Gingeras GM12878 total RNA-seq ENCFF906LSJ': 'ENCFF906LSJ',
        'Thomas Gingeras GM12878 polyA RNA-seq ENCFF550OHK': 'ENCFF550OHK',
        'Thomas Gingeras GM12878 polyA RNA-seq ENCFF902UYP': 'ENCFF902UYP',
        'Brenton Graveley GM12878 total RNA-seq ENCFF418FIT': 'ENCFF418FIT',
        'Brenton Graveley GM12878 total RNA-seq ENCFF306TLL': 'ENCFF306TLL',
        'Brenton Graveley GM12878 polyA RNA-seq ENCFF644DIQ': 'ENCFF644DIQ',
        'Brenton Graveley GM12878 polyA RNA-seq ENCFF456WWG': 'ENCFF456WWG',
        'Barbara Wold GM12878 polyA RNA-seq ENCFF102NLY': 'ENCFF102NLY',
        'Barbara Wold GM12878 polyA RNA-seq ENCFF392CRO': 'ENCFF392CRO',
        'Barbara Wold GM12878 polyA RNA-seq ENCFF905XDJ': 'ENCFF905XDJ',
        'Barbara Wold GM12878 polyA RNA-seq ENCFF200USH': 'ENCFF200USH',
        'Thomas Gingeras K562 polyA RNA-seq ENCFF185UMS': 'ENCFF185UMS',
        'Thomas Gingeras K562 polyA RNA-seq ENCFF472EUD': 'ENCFF472EUD',
        'Brenton Graveley K562 total RNA-seq ENCFF811VBA': 'ENCFF811VBA',
        'Brenton Graveley K562 total RNA-seq ENCFF553DDU': 'ENCFF553DDU',
        'Brenton Graveley K562 polyA RNA-seq ENCFF342LXD': 'ENCFF342LXD',
        'Brenton Graveley K562 polyA RNA-seq ENCFF427EWZ': 'ENCFF427EWZ',
        'Barbara Wold K562 polyA RNA-seq ENCFF156DDL': 'ENCFF156DDL',
        'Barbara Wold K562 polyA RNA-seq ENCFF461HPX': 'ENCFF461HPX',
        'Barbara Wold K562 polyA RNA-seq ENCFF026BMH': 'ENCFF026BMH',
        'Barbara Wold K562 polyA RNA-seq ENCFF868MFR': 'ENCFF868MFR'
    }
    this.experiments = Object.keys(this.experiment_to_file);

    // create some data and a ColumnDataSource
    var a = Bokeh.LinAlg.linspace(-0.5, 20.5, 10);
    var b = a.map(function (v) { return v * 0.5 + 3.0; });
    var c = a.map(function (v) { return Math.sin(v) + 3.0; });
    this.source2 = new Bokeh.ColumnDataSource({
        data: {
            'ENCFF026BMH': [],
            'ENCFF102NLY': [],
            'ENCFF156DDL': [],
            'ENCFF185UMS': [],
            'ENCFF200USH': [],
            'ENCFF306TLL': [],
            'ENCFF342LXD': [],
            'ENCFF392CRO': [],
            'ENCFF418FIT': [],
            'ENCFF427EWZ': [],
            'ENCFF456WWG': [],
            'ENCFF461HPX': [],
            'ENCFF472EUD': [],
            'ENCFF550OHK': [],
            'ENCFF553DDU': [],
            'ENCFF644DIQ': [],
            'ENCFF783VBA': [],
            'ENCFF811VBA': [],
            'ENCFF868MFR': [],
            'ENCFF902UYP': [],
            'ENCFF905XDJ': [],
            'ENCFF906LSJ': [],
            'chromosome': [],
            'source': [],
            'type': [],
            'start': [],
            'stop': [],
            'score': [],
            'strand': [],
            'frame': [],
            'gene_type': [],
            'gene_status': [],
            'gene_name': [],
            'level': [],
            'havana_gene': [],
            'transcript_id': [],
            'transcript_type': [],
            'transcript_status': [],
            'transcript_name': [],
            'tag': [],
            'transcript_support_level': [],
            'havana_transcript': [],
            'exon_number': [],
            'exon_id': [],
            'ont': [],
            'protein_id': [],
            'ccdsid': [],
            'color': []
    } });

    this.source = make_source();

    this.doc = new Bokeh.Document();

    // create some ranges for the plot
    var xdr = new Bokeh.Range1d({ start: -17, end: 20.5 });
    var ydr = new Bokeh.Range1d({ start: -17, end: 20.5 });

    // make the plot
    this.plot = new Bokeh.Plot({
        title: "RNA Evaluation Dataset ",
        x_range: xdr,
        y_range: ydr,
        plot_width: 800,
        plot_height: 800,
        // background_fill_color: "#F2F2F7"
    });

    // add axes to the plot
    this.xaxis = new Bokeh.LinearAxis({axis_label: this.experiments[0]});
    this.yaxis = new Bokeh.LinearAxis({axis_label: this.experiments[1]});
    this.plot.add_layout(this.xaxis, "below");
    this.plot.add_layout(this.yaxis, "left");

    // add grids to the plot
    var xgrid = new Bokeh.Grid({ ticker: this.xaxis.ticker, dimension: 0});
    var ygrid = new Bokeh.Grid({ ticker: this.yaxis.ticker, dimension: 1});
    this.plot.add_layout(xgrid);
    this.plot.add_layout(ygrid);

    this.glyph = new Bokeh.Circle({
        x: { field: label_to_column(this.experiments[0]) },
        y: { field: label_to_column(this.experiments[1]) },
        line_color: {field: "color"},
        fill_color: {field: "color"}
    });
    r1 = this.plot.add_glyph(this.glyph, this.source);

    var line_source = new Bokeh.ColumnDataSource({
        data: {
            x: [-17, 20.5],
            y: [-17, 20.5],
        }})
    var line = new Bokeh.Line({
        x: {field: "x"},
        y: {field: "y"},
        line_color: "#000000"
    })
    this.plot.add_glyph(line, line_source)

    const tooltips = [
        ['gene_id', '$index'],
        ['gene_name', '@gene_name'],
        ['data (x, y)', '($x, $y)'],
        ['chr', '@chromosome'],
        ['start', '@start'],
        ['stop', '@stop'],
        ['strand', '@strand']
    ];

    var tools = [
        new Bokeh.PanTool(),
        new Bokeh.BoxZoomTool(),
        new Bokeh.WheelZoomTool(),
        new Bokeh.SaveTool(),
        new Bokeh.ResetTool(),
        new Bokeh.HoverTool({tooltips: tooltips})
    ];
    for (t of tools) {
        this.plot.add_tools(t);
    }

    // set up drop downs
    this.x_select = new Bokeh.Widgets.Select({
        title: "x axis",
        value: this.experiments[0],
        options: this.experiments,
        callback: new Bokeh.CustomJS({
            args: {"glyph": this.glyph,
                   "xaxis": this.xaxis},
            code: "var glyph = arguments[0];" +
                "var xaxis = arguments[1];" +
                "var select = arguments[2];" +
                "glyph.x = {'field': label_to_column(select.value)};" +
                "xaxis.axis_label = select.value + ' axis';"
        })
    });
    this.y_select = new Bokeh.Widgets.Select({
        title: "y axis",
        value: this.experiments[1],
        options: this.experiments,
        callback: new Bokeh.CustomJS({
            args: {"glyph": this.glyph,
                   "yaxis": this.yaxis},
            code: "var glyph = arguments[0];" +
                "var yaxis = arguments[1];" +
                "var select = arguments[2];" +
                "glyph.y = {'field': label_to_column(select.value)};" +
                "yaxis.axis_label = select.value + ' axis';"
        })
    });

    this.render();
    p.plot = this;
    //this.load();
}

Plot.prototype.render = function () {
    var _this = this;
    // add the plot to a document and display it
    this.doc.add_root(new Bokeh.WidgetBox({
        children: [this.x_select, this.y_select],
        width: 800}));
    this.doc.add_root(this.plot);
    var div = document.getElementById("plot");
    Bokeh.embed.add_document_standalone(this.doc, div);
};

Plot.prototype.load = function() {
    var _this = this;
    var request = new XMLHttpRequest();
    const url = "http://localhost/~diane/rna_evaluation_plot/rna.json";
    console.log("GET " + url);
    request.open("GET", url);
    request.responseType = "json";
    request.onload = function() {
        console.log("loaded", request.statusText, request.status);
        if (request.status == 200) {
            _this.source.data = request.response;
            _this.render();
        } else {
            alert("unable to load " + url);
        }
    };
    request.send();
}
