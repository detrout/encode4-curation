function Plot() {
    this.doc = new Bokeh.Document();

    // create some data and a ColumnDataSource
    var x = Bokeh.LinAlg.linspace(-0.5, 20.5, 10);
    var y = x.map(function (v) { return v * 0.5 + 3.0; });
    this.source = new Bokeh.ColumnDataSource({ data: { x: x, y: y } });
    
    // create some ranges for the plot
    var xdr = new Bokeh.Range1d({ start: -0.5, end: 20.5 });
    var ydr = new Bokeh.Range1d({ start: -0.5, end: 20.5 });
    
    // make the plot
    this.plot = new Bokeh.Plot({
        title: "BokehJS Plot",
        x_range: xdr,
        y_range: ydr,
        plot_width: 500,
        plot_height: 500,
        // background_fill_color: "#F2F2F7"
    });

    // add axes to the plot
    var xaxis = new Bokeh.LinearAxis();
    var yaxis = new Bokeh.LinearAxis();
    this.plot.add_layout(xaxis, "below");
    this.plot.add_layout(yaxis, "left");
    
    // add grids to the plot
    var xgrid = new Bokeh.Grid({ ticker: xaxis.ticker, dimension: 0 });
    var ygrid = new Bokeh.Grid({ ticker: yaxis.ticker, dimension: 1 });
    this.plot.add_layout(xgrid);
    this.plot.add_layout(ygrid);
    
    this.glyph = new Bokeh.Circle({
        x: { field: "x" },
        y: { field: "y" },
        line_color: "#666699",
        line_width: 2
    });
    r1 = this.plot.add_glyph(this.glyph, this.source);

    const tooltips = [
        ["index",         "$index"    ],
        ["data (x, y)",   "($x, $y)"  ],
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

    this.y_select = new Bokeh.Widgets.Select({
        value: "a",
        options: ["a", "b", "c"],
        callback: new Bokeh.CustomJS({
            code: "console.log('event len' + arguments.length);" +
                "for (var a in arguments) { " +
                "  console.log('event ' + a + ' ' + arguments[a]);" +
                "}" +
                "console.log(arguments[0g].value);"
        })
    });
    this.render();
    this.load();
    p.plot = this;
}

Plot.prototype.render = function () {
    var _this = this;
    // add the plot to a document and display it
    this.doc.add_root(new Bokeh.WidgetBox({
        children: [this.y_select],
        width: 600}));
    this.doc.add_root(this.plot);
    var div = document.getElementById("plot");
    Bokeh.embed.add_document_standalone(this.doc, div);
};

Plot.prototype.load = function() {
    var _this = this;
    var request = new XMLHttpRequest();
    request.open("GET", "http://localhost/~diane/rna_evaluation_plot/data.json");
    request.responseType = "json";
    request.onload = function() {
        console.log("loaded");
        _this.source.data = request.response;
        _this.render();
    };
    request.send();
}
