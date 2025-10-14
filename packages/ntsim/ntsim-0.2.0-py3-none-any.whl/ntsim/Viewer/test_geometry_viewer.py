def test_geometry_viewer(docks,widgets,data,frames,options):
    from ntsim.Viewer.geometry_viewer import geometry_viewer
    viewer = geometry_viewer(frames=frames)
    viewer.set_docks(docks)
    viewer.set_widgets(widgets)
    viewer.set_data(data)
    viewer.configure(options)
    return viewer
