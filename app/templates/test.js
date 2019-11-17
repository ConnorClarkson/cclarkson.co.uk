google.charts.load("current", {packages:["sankey"]})
google.charts.setOnLoadCallback(drawChart);
function drawChart() {
var data = new google.visualization.DataTable();
data.addColumn('string', 'From');
data.addColumn('string', 'To');
data.addColumn('number', 'Weight');
data.addRows("");

// Set chart options
var options = {
  width: 600,
  sankey: {
      node: {
        label: {
          fontName: 'Times-Roman',
          fontSize: 12,
          color: '#000',
          bold: true,
          italic: false
        },
        interactivity: true, // Allows you to select nodes.
        labelPadding: 6,     // Horizontal distance between the label and the node.
        nodePadding: 10,     // Vertical distance between nodes.
        width: 5,            // Thickness of the node.
        colors: [
          '#a6cee3',         // Custom color palette for sankey nodes.
          '#1f78b4',         // Nodes will cycle through this palette
          '#b2df8a',         // giving each node its own color.
          '#33a02c'
        ]
      }
  }
};

// Instantiate and draw our chart, passing in some options.
var chart = new google.visualization.Sankey(document.getElementById('sankey_multiple'));
chart.draw(data, options);
}


