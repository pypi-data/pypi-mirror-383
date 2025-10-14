import panel as pn
import param

pn.template.VanillaTemplate(
    title='DEMO',
    sidebar_width=750,
    sidebar=[pn.pane.Markdown("Meh"), ],
    main=[],
).servable()

