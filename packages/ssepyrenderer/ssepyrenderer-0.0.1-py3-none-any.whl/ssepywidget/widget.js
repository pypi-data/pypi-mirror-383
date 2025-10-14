/**
 * this function is no-named function with export keyword:
 * - it is easy to understand how this function is called with the example:
 *   // assign this function as "render_widget"
 *   import render_widget from "./widget.js";
 *   // call this function with the specified name:
 *   render_widget({ model, el });
 * 
 */
async function render({ model, el }) {
    // model: widget's data/state
    // el: the DOM element that will be used to render the widget
    const canvas = document.createElement("canvas");
    el.appendChild(canvas);

    function resize() {
        canvas.width = model.get('width');
        canvas.height = model.get('height');
        canvas.style.border = "1px solid black";
    }
    resize();

    // model is from anywidget in python:
    // - it is intended to connect JS with python(anywidget)
    // - python's traitlets define this format:
    //   - it is called 'model interface'
    //   *** see https://anywidget.dev/en/afm/
    model.on('change:width', resize);
    model.on('change:height', resize);

    const ctx = canvas.getContext('2d');

    const draw = () => {
        ctx.fillStyle = model.get("color");
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        requestAnimationFrame(draw);
    };
    draw();

    model.on('change:color', draw);
}
export default { render };